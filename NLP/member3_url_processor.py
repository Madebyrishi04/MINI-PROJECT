import os
import requests
import validators
from newspaper import Article
import importlib.util

# 🔥 FIX model_arch import issue
import sys

model_arch_path = os.path.join(
    os.path.dirname(__file__),
    "model_arch.py"
)

TRUSTED_SOURCES = ["bbc", "reuters", "thehindu", "ndtv", "cnn", "aljazeera"]

BIAS_WORDS = ["said", "reported", "according to", "confirmed", "official", "statement"]

spec_arch = importlib.util.spec_from_file_location("model_arch", model_arch_path)
model_arch_module = importlib.util.module_from_spec(spec_arch)
spec_arch.loader.exec_module(model_arch_module)

sys.modules["model_arch"] = model_arch_module

from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_domain(url):
    return urlparse(url).netloc.lower()


def fallback_extract(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")

        text = " ".join([
            p.get_text() for p in paragraphs 
            if len(p.get_text()) > 50
        ])

        return text
    except:
        return None
    
# ✅ LOAD 6_prediction.py FROM SAME FOLDER (nlp1)
def load_prediction_module():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "prediction.py"
    )

    spec = importlib.util.spec_from_file_location("prediction_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


predict_module = load_prediction_module()


# ✅ 1. Check URL
def check_url(url):
    return validators.url(url)


# ✅ 2. Expand short URL
def expand_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.url
    except:
        return url   # fallback


# ✅ 3. Extract article text
def get_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None


# ✅ 4. Clean text
import re
def clean_text(text):
    import re

    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def get_clean_chunk(text, limit=500):
    if len(text) <= limit:
        return text

    # take first part
    start = text[:limit]
    if "." in start:
        start = start[:start.rfind(".") + 1]

    # take last part
    end = text[-limit:]
    if "." in end:
        end = end[end.find(".") + 1:]

    return start + " " + end

# ✅ 5. FULL PIPELINE
def process_url(url, predictor):

    domain = get_domain(url)

    # basic trust signal
    trusted_sources = ["bbc", "reuters", "thehindu", "ndtv", "cnn", "aljazeera"]


    if not check_url(url):
        return {"error": "Invalid URL"}

    url = expand_url(url)
    if not url:
        return {"error": "URL not reachable"}

    # Step 1: Extract
    text = get_article_text(url)

    if not text:
        print("⚠ Using fallback extraction...")
        text = fallback_extract(url)

    if not text:
        return {"error": "Failed to extract article"}

    if len(text) < 50:
        return {"error": "Content too short"}

    # Step 2: Clean
    text = clean_text(text)

    # 🔥 IMPORTANT: start + end
    text = get_clean_chunk(text)
    

    print("\n===== CLEANED TEXT =====\n")
    print(text[:500])
    print("\n========================\n")

    # Step 3: Prediction
    result = predictor.predict_long_text(text)

# 🔥 Domain-based boost
    if any(src in domain for src in TRUSTED_SOURCES):
        result["real_prob"] = min(result["real_prob"] + 0.05, 1.0)
        result["fake_prob"] = 1 - result["real_prob"]

    # 🔥 Bias correction (language-based)
    if any(word in text for word in BIAS_WORDS):
        result["real_prob"] = min(result["real_prob"] + 0.05, 1.0)
        result["fake_prob"] = 1 - result["real_prob"]

# 🔥 FINAL DECISION
    result["label"] = "REAL" if result["real_prob"] > result["fake_prob"] else "FAKE"
    result["confidence"] = round(max(result["real_prob"], result["fake_prob"]), 4)

    if result["confidence"] < predictor.threshold:
        result["verdict"] = "UNCERTAIN"
    else:
        result["verdict"] = result["label"]

    # 🔥 Extra safety
    if result["confidence"] < 0.60:
        result["verdict"] = "UNCERTAIN"

    # 🔥 Explanation
    if result["verdict"] == "FAKE":
        result["reason"] = "Content shows patterns similar to misinformation."
    elif result["verdict"] == "REAL":
        result["reason"] = "Content matches patterns of verified news reporting."
    else:
        result["reason"] = "Model is uncertain due to mixed signals."

    print("MODEL RESULT:", result)

    return result

# ✅ 7. RUN
if __name__ == "__main__":
    url = input("Enter URL: ")
    output = process_url(url)
    
    print("\nRESULT:")
    print(output)