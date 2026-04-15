🚀 AI-Powered Fake News Detection System
📌 Overview

This mini project is developed by a team of 6 members with the aim of detecting and refining news circulating on social media platforms. In today’s rapidly evolving digital world, it is important to ensure that the information we consume is not fabricated or biased. This system uses AI and NLP techniques to classify news as REAL, FAKE, or UNCERTAIN.

💻 Frontend Preview

The frontend interface has been designed to provide a clean and interactive user experience.

⚙️ Frontend Setup
🔹 Requirements
Node.js (Download: https://nodejs.org/en/download/current
)
🔹 Steps to Run Frontend
cd frontend
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
npm install
npm run dev
🖼️ OCR Setup (Tesseract)

Download and install Tesseract OCR:

👉 https://github.com/tesseract-ocr/tesseract

(Use the Windows installer if required)

🧠 Model Understanding

The model is trained on news datasets and works based on linguistic patterns.

⚠️ Important Note:
The model is trained on news articles
It is NOT trained on:
Government websites
Educational content
Static informational pages

👉 Therefore, it may sometimes classify such content as FAKE

🎯 Very Important (For Viva)
❓ Does the model verify facts?

👉 Answer:

No, the model does not verify factual correctness. It classifies content based on linguistic patterns learned from training data.

📊 Dataset Characteristics

The dataset used in training includes:

Large number of news articles
Heavy presence of US political news
Fake and conspiracy-style content
Specific writing patterns

👉 This influences how the model learns and predicts.

⚠️ Limitations
Works mainly for English language
Cannot perform factual verification
May misclassify non-news content
Dependent on dataset patterns
👥 Team Members
Mohammad Anwar Raza – Backend Integration
Snehangshu Sarkar – Frontend Development
Aditya Mukherjee – NLP Model Design
Nasim – OCR Module
Soumya Jhaa – JavaScript & Dataset Integration
Zeeshan – URL Scraping Module
