# Recog/ocr.py

import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(thresh, config='--psm 6')

    # Clean text
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,]', '', text)

    return text

if __name__ == "__main__":
    result = extract_text("test.png")  # 👈 your image name
    print("\n📄 Extracted Text:\n")
    print(result)