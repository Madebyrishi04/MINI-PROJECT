import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
from NLP.prediction import FakeNewsPredictor
from Recog.ocr import extract_text
from NLP.member3_url_processor import process_url

# ✅ Create app ONCE
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/predict_url', methods=['POST'])
def predict_url():

    data = request.json
    url = data.get('url', '')

    result = process_url(url, predictor)
    text = process_url(url, predictor)

    if "error" in result:
        return jsonify(result)

    return jsonify({
        "prediction": result["verdict"],
        "confidence": float(result["confidence"]),
        "fake_prob": result["fake_prob"],
        "real_prob": result["real_prob"]
    })


# ✅ Load model
predictor = FakeNewsPredictor()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return "Fake News Detection API Running 🚀"


# 🔥 IMAGE API
@app.route('/predict_image', methods=['POST'])
def predict_image():

    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    file = request.files['image']

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = extract_text(filepath)

    result = predictor.predict(text)
    print("MODEL OUTPUT:", result)
    return jsonify({
        "prediction": result["verdict"],
        "extracted_text": text,
        "confidence": float(result["confidence"])
    })


# 🔥 TEXT API (FIXED)
@app.route('/predict_text', methods=['POST'])
def predict_text():

    data = request.json
    text = data.get('text', '')

    result = predictor.predict(text)
    print("MODEL OUTPUT:", result)
    return jsonify({
        "prediction": result["verdict"],
        "confidence": float(result["confidence"])
    })


if __name__ == '__main__':
    app.run(debug=True)