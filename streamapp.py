import streamlit as st
from PIL import Image
import io

# Try to import Google Cloud services
try:
    from google.cloud import vision
    from google.cloud import translate_v2 as translate
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Streamlit UI
st.title("🖼️ OCR & Translation Tool")
st.markdown("Upload an image, extract text using Google Vision API, and translate it with Google Translate API.")

if not GOOGLE_CLOUD_AVAILABLE:
    st.error("❌ **Google Cloud libraries not installed!**")
    st.markdown("Install: `pip install google-cloud-vision google-cloud-translate`")
    st.stop()

# Initialize Google Cloud clients with caching
@st.cache_resource
def init_clients():
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        translate_client = translate.Client(credentials=credentials)
        return vision_client, translate_client
    except Exception as e:
        st.error(f"❌ **Authentication Error:** {str(e)}")
        st.stop()

vision_client, translate_client = init_clients()
st.success("✅ Connected to Google Cloud APIs successfully!")

# Upload image
uploaded_file = st.file_uploader("📂 Upload an image...", type=["jpg", "jpeg", "png"])

# Language selection
languages = {
    "en": "English", "hi": "Hindi", "fr": "French", "es": "Spanish", 
    "de": "German", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ur": "Urdu"
}
target_language = st.selectbox("🌍 Translate to:", list(languages.keys()), index=1)

if uploaded_file:
    try:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()

        # OCR with Vision API
        vision_image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=vision_image)
        texts = response.text_annotations

        if texts:
            extracted_text = texts[0].description.strip()
            st.subheader("📝 Extracted Text (OCR):")
            st.text_area("OCR Result", extracted_text, height=120)

            # Show detected blocks (optional)
            if len(texts) > 1:
                with st.expander("Show Detected Segments"):
                    for i, t in enumerate(texts[1:], start=1):
                        st.write(f"{i}. {t.description}")

            # Auto-detect source language
            detection = translate_client.detect_language(extracted_text)
            detected_lang = detection.get("language", "unknown")
            st.info(f"Detected language: **{detected_lang.upper()}**")

            # Translate
            result = translate_client.translate(extracted_text, target_language=target_language)
            translated_text = result["translatedText"]

            st.subheader(f"🌐 Translated Text ({languages.get(target_language)}):")
            st.text_area("Translation", translated_text, height=120)

            # Download buttons
            st.download_button("⬇️ Download Extracted Text", extracted_text, "ocr_text.txt")
            st.download_button("⬇️ Download Translation", translated_text, f"translated_{target_language}.txt")

        else:
            st.warning("⚠️ No text detected in the image")

    except Exception as e:
        st.error(f"❌ **Error processing image:** {str(e)}")
        st.markdown("Please check your Google Cloud credentials and API permissions.")
