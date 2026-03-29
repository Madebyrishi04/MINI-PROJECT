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

spec_arch = importlib.util.spec_from_file_location("model_arch", model_arch_path)
model_arch_module = importlib.util.module_from_spec(spec_arch)
spec_arch.loader.exec_module(model_arch_module)

sys.modules["model_arch"] = model_arch_module

from bs4 import BeautifulSoup

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
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # 🔥 TAKE FIRST FEW SENTENCES ONLY
    sentences = text.split(".")
    text = " ".join(sentences[:5])

    return text

# ✅ 5. SEND TEXT TO MEMBER 2 MODEL
def send_to_model(text, predictor):
    try:
        return predictor.predict(text)
    except Exception as e:
        return {"error": str(e)}


# ✅ 6. FULL PIPELINE
def process_url(url, predictor):

    if not check_url(url):
        return {"error": "Invalid URL"}

    url = expand_url(url)
    if not url:
        return {"error": "URL not reachable"}

    # 🔥 Step 1: Try main extraction
    text = get_article_text(url)

    if text:
        print("\n===== EXTRACTED TEXT =====\n")
        print(text[:1000])
    else:
        print("\n❌ Primary extraction failed\n")

    # 🔥 Step 2: Fallback if needed
    if not text:
        print("⚠ Using fallback extraction...")
        text = fallback_extract(url)

    # 🔥 Step 3: Check again
    if not text:
        return {"error": "Failed to extract article"}

    if len(text) < 50:
        return {"error": "Content too short"}

    # 🔥 Step 4: Clean text
    text = clean_text(text)
    text = text[:500]

    print("\n===== CLEANED TEXT =====\n")
    print(text)
    print("\n========================\n")

    # 🔥 Step 5: Model prediction
    result = send_to_model(text, predictor)
    print("MODEL RESULT:", result)

# 🔥 ADD THIS BLOCK HERE
    if "error" in result:
        return {
            "prediction": "UNCERTAIN",
            "confidence": 0.0
        }
    return result 


# ✅ 7. RUN
if __name__ == "__main__":
    url = input("Enter URL: ")
    output = process_url(url)
    print("\nRESULT:")
    print(output)