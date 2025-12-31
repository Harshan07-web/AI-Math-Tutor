import streamlit as st
from PIL import Image
from _vision.ocr import OCRProcessor

st.set_page_config(page_title="Math OCR Test", layout="centered")

st.title("🖼 Math OCR Test")
st.caption("Upload a math image to see both rendered and LaTeX output")

uploaded_file = st.file_uploader(
    "Upload math image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.subheader("📷 Uploaded Image")
    st.image(image, width=350)

    ocr = OCRProcessor()

    with st.spinner("Running OCR..."):
        latex_text = ocr.extract_text(image)

    st.success("OCR Completed")

    # -------------------------------
    # RAW LATEX OUTPUT
    # -------------------------------
    st.subheader("📄 LaTeX Output (Raw)")
    st.code(latex_text, language="latex")

    # -------------------------------
    # RENDERED MATH OUTPUT
    # -------------------------------
    st.subheader("📐 Rendered Output")

    try:
        # Streamlit renders LaTeX inside $$ $$
        st.latex(latex_text)
    except Exception as e:
        st.error("LaTeX rendering failed")
        st.write(str(e))
