import streamlit as st
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import os
from PIL import Image
import io

# Load Google Cloud credentials
credentials = service_account.Credentials.from_service_account_file('credentials.json')
vision_client = vision.ImageAnnotatorClient(credentials=credentials)
translate_client = translate.Client(credentials=credentials)

# Streamlit UI setup
st.title("Image OCR & Translation Tool")
st.markdown("Extract text from images and translate it to multiple languages")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type="jpg")

# Language selection
languages = {
    "en": "English", "hi": "Hindi", "fr": "French", "es": "Spanish", 
    "de": "German", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ur": "Urdu"
}
target_language = st.selectbox("Translate to", list(languages.keys()), index=1)

# Process image and display extracted text and translation
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    
    # OCR using Google Cloud Vision API
    image = vision.Image(content=image_bytes)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        extracted_text = texts[0].description.strip()
        st.subheader("Extracted Text (OCR):")
        st.text(extracted_text)

        # Translate extracted text
        result = translate_client.translate(extracted_text, target_language=target_language)
        translated_text = result['translatedText']
        st.subheader(f"Translated Text ({languages.get(target_language)}):")
        st.text(translated_text)
    else:
        st.error("No text detected in the image")

