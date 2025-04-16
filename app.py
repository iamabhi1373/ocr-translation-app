import os
from flask import Flask, render_template, request
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load Google Cloud credentials
credentials = service_account.Credentials.from_service_account_file('credentials.json')
vision_client = vision.ImageAnnotatorClient(credentials=credentials)
translate_client = translate.Client(credentials=credentials)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    extracted_text = ""
    translated_text = ""
    target_lang = ""

    if request.method == 'POST':
        file = request.files['image']
        target_lang = request.form.get('language', 'hi')  # Default to Hindi if not selected

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # OCR using Vision API
        with open(filepath, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            extracted_text = texts[0].description.strip()

            # Translate extracted text
            result = translate_client.translate(extracted_text, target_language=target_lang)
            translated_text = result['translatedText']

    return render_template('index.html',
                           extracted_text=extracted_text,
                           translated_text=translated_text,
                           language=target_lang)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
