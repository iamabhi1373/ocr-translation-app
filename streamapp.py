import streamlit as st
from PIL import Image
import io
import os

# Try to import Google Cloud services, but handle if credentials are missing
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

# Check if credentials file exists
credentials_file = 'credentials.json'
if not os.path.exists(credentials_file):
    st.error("❌ **credentials.json file not found!**")
    st.markdown("""
    ### To use this app, you need to:
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select existing one
    3. Enable Vision API and Translation API
    4. Create a service account and download the JSON key
    5. Save it as `credentials.json` in this directory
    """)
    st.stop()

# Try to initialize Google Cloud clients
if GOOGLE_CLOUD_AVAILABLE:
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        translate_client = translate.Client(credentials=credentials)
        st.success(" Welcome , All set! Services are ready to go fell free to upload  image  🚀")
    except Exception as e:
        st.error(f"❌ **Authentication Error:** {str(e)}")
        st.markdown("""
        ### Your credentials appear to be invalid or expired. Please:
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Check if your project is active
        3. Verify the service account has proper permissions
        4. Download a new service account key
        5. Replace the current `credentials.json` file
        """)
        st.stop()
else:
    st.error("❌ **Google Cloud libraries not installed!**")
    st.markdown("Please install required packages: `pip install google-cloud-vision google-cloud-translate`")
    st.stop()

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Language selection
languages = {
    "en": "English", "hi": "Hindi", "fr": "French", "es": "Spanish", 
    "de": "German", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ur": "Urdu"
}
target_language = st.selectbox("Translate to", list(languages.keys()), index=1)

# Process image and display extracted text and translation
if uploaded_file is not None:
    try:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        
        # OCR using Google Cloud Vision API
        vision_image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=vision_image)
        texts = response.text_annotations

        if texts:
            extracted_text = texts[0].description.strip()
            st.subheader("Extracted Text (OCR):")
            st.text_area("", extracted_text, height=100)

            # Translate extracted text
            result = translate_client.translate(extracted_text, target_language=target_language)
            translated_text = result['translatedText']
            st.subheader(f"Translated Text ({languages.get(target_language)}):")
            st.text_area("", translated_text, height=100)
        else:
            st.warning("⚠️ No text detected in the image")
            
    except Exception as e:
        st.error(f"❌ **Error processing image:** {str(e)}")
        st.markdown("Please check your Google Cloud credentials and API permissions.")

