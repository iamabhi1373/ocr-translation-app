import streamlit as st
from PIL import Image
import io
import os
import json

# Try to import Google Cloud services
try:
    from google.cloud import vision
    from google.cloud import translate_v2 as translate
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Streamlit UI setup
st.title("Image OCR & Translation Tool")
st.markdown("Extract text from images and translate it to multiple languages")

# -------------------
# Load credentials
# -------------------
credentials = None
vision_client = None
translate_client = None

if GOOGLE_CLOUD_AVAILABLE:
    try:
        # First try local file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        credentials_file = os.path.join(BASE_DIR, "credentials.json")

        if os.path.exists(credentials_file):
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
        else:
            # Fallback: load from Streamlit secrets (when deployed)
            if "google_cloud" in st.secrets:
                creds_json = st.secrets["google_cloud"]
                credentials = service_account.Credentials.from_service_account_info(creds_json)
            else:
                st.error("❌ No credentials found! Please provide `credentials.json` locally or set `google_cloud` in Streamlit Secrets.")
                st.stop()

        # Initialize clients
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        translate_client = translate.Client(credentials=credentials)
        st.success("✅ Google Cloud services initialized! Upload an image 🚀")

    except Exception as e:
        st.error(f"❌ **Authentication Error:** {str(e)}")
        st.markdown("""
        ### Fix this issue:
        1. Ensure Vision API & Translation API are enabled in Google Cloud
        2. Verify your service account has proper permissions
        3. If running locally → place `credentials.json` in the app folder
        4. If on Streamlit Cloud → paste the JSON into `Secrets` as `[google_cloud]`
        """)
        st.stop()
else:
    st.error("❌ **Google Cloud libraries not installed!**")
    st.markdown("Please install required packages: `pip install google-cloud-vision google-cloud-translate`")
    st.stop()

# -------------------
# Streamlit App Logic
# -------------------
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

languages = {
    "en": "English", "hi": "Hindi", "fr": "French", "es": "Spanish",
    "de": "German", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ur": "Urdu"
}
target_language = st.selectbox("Translate to", list(languages.keys()), index=1)

if uploaded_file is not None:
    try:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Convert to bytes
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()

        # OCR
        vision_image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=vision_image)
        texts = response.text_annotations

        if texts:
            extracted_text = texts[0].description.strip()
            st.subheader("Extracted Text (OCR):")
            st.text_area("", extracted_text, height=100)

            # Translation
            result = translate_client.translate(extracted_text, target_language=target_language)
            translated_text = result['translatedText']
            st.subheader(f"Translated Text ({languages.get(target_language)}):")
            st.text_area("", translated_text, height=100)
        else:
            st.warning("⚠️ No text detected in the image")

    except Exception as e:
        st.error(f"❌ **Error processing image:** {str(e)}")
        st.markdown("Please check your Google Cloud credentials and API permissions.")
