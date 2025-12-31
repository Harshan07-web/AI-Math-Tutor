import streamlit as st
from PIL import Image

from _core.pipeline import Pipeline

# -----------------------------------
# 🎯 App Config
# -----------------------------------
st.set_page_config(
    page_title="📐 AI Math Tutor",
    layout="centered"
)

st.title("📐 AI Math Tutor")
st.caption("Upload a math image or enter a math expression")

# -----------------------------------
# 🔧 Initialize Pipeline
# -----------------------------------
@st.cache_resource
def load_pipeline():
    return Pipeline()

pipeline = load_pipeline()

# -----------------------------------
# 📥 Input Section
# -----------------------------------
input_mode = st.radio("Choose input mode:", ["Image", "Text"])

user_input = None

if input_mode == "Image":
    uploaded_file = st.file_uploader(
        "Upload math image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=350)
        user_input = image

else:
    user_input = st.text_input(
        "Enter math expression",
        placeholder="Example: 2*x - 3 = -7"
    )

# -----------------------------------
# ▶ Solve Button
# -----------------------------------
if st.button("Solve"):
    if not user_input:
        st.warning("Please upload an image or enter a math expression.")
    else:
        with st.spinner("Analyzing problem..."):
            result = pipeline.solve_and_explain(user_input)

        # -----------------------------------
        # ❌ Error Handling
        # -----------------------------------
        if result.get("error"):
            st.error(result["error"])
            st.write(result.get("message", ""))
            st.stop()

        # -----------------------------------
        # 📐 Rendered LaTeX
        # -----------------------------------
        if result.get("latex"):
            st.subheader("📐 Recognized Expression")
            st.latex(result["latex"])

        # -----------------------------------
        # ✅ Final Answer
        # -----------------------------------
        st.subheader("✅ Final Answer")
        st.write(result.get("final_answer"))

        # -----------------------------------
        # 🧩 Steps
        # -----------------------------------
        if result.get("steps"):
            st.subheader("🧩 Solving Steps")
            for step in result["steps"]:
                st.markdown(
                    f"**Step {step['step_number']}**: "
                    f"{step['type']} → `{step['output']}`"
                )

        # -----------------------------------
        # 🧠 Explanation
        # -----------------------------------
        if result.get("explanation"):
            st.subheader("🧠 Explanation")
            st.write(result["explanation"])

# -----------------------------------
# 🧪 Footer
# -----------------------------------
st.markdown("---")
st.caption("🚀 AI Math Tutor | OCR → SymPy → Explanation")
