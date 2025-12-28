import streamlit as st
from PIL import Image
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from _vision import OCRProcessor


st.set_page_config(page_title="AI Math Tutor – OCR", layout="centered")

st.title("📐 AI Math Tutor – Math OCR")

ocr = OCRProcessor(use_preprocessing=True)

uploaded_file = st.file_uploader(
    "Upload a math equation image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Uploaded Image", width=400)

    with st.spinner("Recognizing math equation..."):
        latex = ocr.image_to_latex(image)

    st.success("OCR Completed")

    st.subheader("Rendered LaTeX")
    st.latex(latex)

    st.subheader("Raw LaTeX")
    st.code(latex)
