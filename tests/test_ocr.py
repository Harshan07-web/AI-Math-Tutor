import sys
import os

# 🔥 Ensure project root is in PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
from PIL import Image
from _vision.ocr import OCRProcessor

st.set_page_config(page_title="AI Math Tutor OCR", layout="centered")
st.title("📐 AI Math Tutor – Math OCR")

ocr = OCRProcessor(use_preprocessing=True, device="cpu")

uploaded_file = st.file_uploader("Upload a math equation image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", width=600)

    with st.spinner("Recognizing math equation..."):
        try:
            # Get raw OCR output directly from the model
            if hasattr(ocr.model, "predict"):
                raw_latex = ocr.model.predict(image)
            elif hasattr(ocr.model, "to_latex"):
                raw_latex = ocr.model.to_latex(image)
            else:
                raw_latex = ocr.model(image)

            # Clean the LaTeX using OCRProcessor's cleanup
            cleaned_latex = ocr._clean_latex(raw_latex)

            st.success("OCR Completed ✅")

            # Show results
            st.subheader("LaTeX Output (rendered)")
            st.latex(cleaned_latex)

            st.subheader("Raw LaTeX Code")
            st.code(raw_latex)

            st.subheader("Cleaned LaTeX Code")
            st.code(cleaned_latex)

        except Exception as e:
            st.error(f"OCR failed: {e}")