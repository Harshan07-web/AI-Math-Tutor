import streamlit as st
from PIL import Image
from _core.pipeline import Pipeline

st.set_page_config(page_title="📐 AI Math Tutor")

st.title("📐 AI Math Tutor")

pipeline = Pipeline()

uploaded = st.file_uploader(
    "Upload math image",
    type=["png", "jpg", "jpeg"]
)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, width=300)

    with st.spinner("Solving..."):
        output = pipeline.solve_and_explain(image)

    if "error" in output:
        st.error(output["error"])
    else:
        st.subheader("Final Answer")
        st.write(output["final_answer"])

        st.subheader("Explanation")
        st.write(output["explanation"])
