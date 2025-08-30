# app.py
import streamlit as st
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from PIL import Image
import io

st.set_page_config(page_title="OCR + Translate", layout="centered")
st.title("📝 OCR + Translation (Google Cloud)")

# === Load credentials from streamlit secrets ===
# In Streamlit Cloud put a [google_cloud] table with the JSON fields.
service_account_info = st.secrets["google_cloud"]          # dict-like
creds = service_account.Credentials.from_service_account_info(service_account_info)

# === Initialize clients ===
vision_client = vision.ImageAnnotatorClient(credentials=creds)
translate_client = translate.Client(credentials=creds)

st.markdown("Upload an image and I'll extract the text and translate it.")

uploaded_file = st.file_uploader("Choose image", type=["png", "jpg", "jpeg"])
target_lang = st.text_input("Target language code (e.g. 'hi' for Hindi, 'fr' for French)", value="hi")

if uploaded_file:
    # show image
    st.image(uploaded_file, use_column_width=True)

    # read bytes
    image_bytes = uploaded_file.read()
    image = vision.Image(content=image_bytes)

    try:
        # OCR call
        response = vision_client.text_detection(image=image)
        if response.error.message:
            st.error(f"Vision API error: {response.error.message}")
        else:
            texts = response.text_annotations
            if not texts:
                st.warning("No text detected in the image.")
            else:
                extracted_text = texts[0].description  # full text
                st.subheader("📖 Extracted Text")
                st.text_area("Detected text", extracted_text, height=250)

                # Translate
                if target_lang:
                    try:
                        translation = translate_client.translate(extracted_text, target_language=target_lang)
                        st.subheader(f"🌍 Translation — {target_lang}")
                        st.write(translation.get("translatedText", "(no translatedText returned)"))
                    except GoogleAPIError as e:
                        st.error(f"Translation API error: {e}")
    except GoogleAPIError as e:
        st.error(f"API error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
