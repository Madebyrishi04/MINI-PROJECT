The mini project which is a 6 member project is under development with the idea to refine the news circulating on the social media. In this world of
rapidly developing technology we need to know what we consume daily for news is not fabricated or having a bias.

The front end is already prepared, here's a glimpse of it. <img width="1913" height="878" alt="image" src="https://github.com/user-attachments/assets/0a777253-7a15-4bc4-8d76-73780c03be8e" />

required node.js (https://nodejs.org/en/download/current)


cd frontend
<br>
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
<br>
npm install
<br>
npm run dev

<br>
https://release-assets.githubusercontent.com/github-production-release-asset/22887094/87baebb0-a3be-4707-97df-8198ef676a8e?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-03-27T12%3A40%3A49Z&rscd=attachment%3B+filename%3Dtesseract-ocr-w64-setup-5.5.0.20241111.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-03-27T11%3A40%3A47Z&ske=2026-03-27T12%3A40%3A49Z&sks=b&skv=2018-11-09&sig=XofBklMQ0BZS5tHUi2wZTucsdIAp6KB2GVbV1jwGSXo%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc3NDYxNDIwMywibmJmIjoxNzc0NjEyNDAzLCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.zN0rs-lYF0gtiYQiCxXuszBguzLldBNgfGM-R5G1RYw&response-content-disposition=attachment%3B%20filename%3Dtesseract-ocr-w64-setup-5.5.0.20241111.exe&response-content-type=application%2Foctet-stream


Your model:

was trained on a dataset (probably news articles)
NOT trained on:
government sites
educational pages
static informational content

👉 So it misclassifies non-news content as FAKE
ERY IMPORTANT (FOR VIVA)

If examiner asks:

“Does your model verify truth?”

👉 Say:

“No, it classifies based on linguistic patterns learned from training data, not factual verification.”


That dataset has:

Heavy US political news
Many fake/conspiracy style samples
Very specific writing patterns
