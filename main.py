import streamlit as st
import numpy as np
from PIL import Image

from _vision.ocr import OCRProcessor

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(
    page_title="AI Math OCR",
    page_icon="🧮",
    layout="centered"
)

# -------------------------
# App Header
# -------------------------
st.markdown(
    """
    <h1 style="text-align:center;">🧮 AI Math OCR</h1>
    <p style="text-align:center;">
        Upload a handwritten or printed math equation image<br>
        and convert it into <b>LaTeX</b>
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Load OCR Model (cached)
# -------------------------
@st.cache_resource
def load_ocr():
    return OCRProcessor()

ocr = load_ocr()

# -------------------------
# Image Upload
# -------------------------
uploaded_file = st.file_uploader(
    "📤 Upload a math image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    # Read image
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Show uploaded image
    st.image(image, caption="Uploaded Image", use_container_width=True)

    st.markdown("---")

    # OCR Button
    if st.button("🔍 Convert Image to LaTeX"):
        with st.spinner("Processing image..."):
            try:
                latex_output = ocr.image_to_latex(img_array)

                st.success("LaTeX Generated Successfully!")

                # Display LaTeX
                st.subheader("📐 LaTeX Output")
                st.code(latex_output, language="latex")

                st.subheader("📊 Rendered Equation")
                st.latex(latex_output)

            except Exception as e:
                st.error("❌ OCR failed")
                st.exception(e)

else:
    st.info("👆 Upload an image to get started")

# -------------------------
# Footer
# -------------------------
st.markdown(
    """
    <hr>
    <p style="text-align:center; font-size:14px;">
        Built with ❤️ using Streamlit + Pix2Tex
    </p>
    """,
    unsafe_allow_html=True
)
