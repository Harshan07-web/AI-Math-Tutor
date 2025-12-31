# app.py
# =================== MUST BE AT TOP ===================
from dotenv import load_dotenv
load_dotenv()   # Load Gemini API key BEFORE anything else
# =====================================================

import streamlit as st
from PIL import Image
import sys
import os
import asyncio

# Fix Windows asyncio issue (important for Python 3.12)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# ------------------- BACKEND IMPORTS -------------------
from _vision.ocr import OCRProcessor
from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler

# ------------------- INITIALIZE BACKEND ----------------
ocr = OCRProcessor()
solver = MathSolver()
extractor = StepExtractor()
normalizer = StepNormalizer()
explainer = StepExplainer()
doubt_handler = DoubtHandler()

# ------------------- STREAMLIT UI ---------------------
st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 AI Math Tutor")

# Sidebar
choice = st.sidebar.selectbox(
    "Choose Mode",
    ["Solve Math Problem", "Ask Doubt"]
)

# ------------------- MODE 1: SOLVE --------------------
if choice == "Solve Math Problem":
    st.subheader("Upload an image or type your math problem")

    input_type = st.radio("Input type", ["Image", "Text"])

    problem_input = ""

    if input_type == "Image":
        uploaded_file = st.file_uploader(
            "Upload an image of the math problem",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            latex = ocr.image_to_latex(image)
            st.markdown("**Detected Math Expression (LaTeX):**")
            st.latex(latex)

            problem_input = latex
    else:
        problem_input = st.text_area("Type your math problem here:")

    if st.button("Solve"):
        if not problem_input.strip():
            st.warning("Please provide a math problem.")
        else:
            solution = solver.solve(problem_input)

            raw_steps = extractor.extract_steps(solution)
            normalized_steps = normalizer.normalize_steps(raw_steps)

            st.markdown("### ✅ Solution")
            st.write(solution.get("final_answer", "No solution found"))

            st.markdown("### 📋 Steps")
            for step in normalized_steps:
                st.write(f"**Step {step['step_number']}**: {step['output']}")

            st.markdown("### 🤓 Explanation (Gemini 2.5)")
            explanation = explainer.explain_steps(
                normalized_steps,
                solution.get("final_answer", "")
            )
            st.write(explanation)

# ------------------- MODE 2: DOUBT --------------------
elif choice == "Ask Doubt":
    st.subheader("Ask your doubt about a solved problem")

    problem = st.text_area("Original Problem")
    steps_input = st.text_area(
        "Solution Steps (one step per line)"
    )
    doubt = st.text_area("Your doubt")

    if st.button("Get Doubt Answer"):
        if not problem or not steps_input or not doubt:
            st.warning("Please fill all fields.")
        else:
            steps_list = [
                {
                    "step_number": i + 1,
                    "output": s,
                    "explanation_hint": ""
                }
                for i, s in enumerate(steps_input.split("\n"))
                if s.strip()
            ]

            answer = doubt_handler.answer_doubt(
                user_question=doubt,
                normalized_steps=steps_list,
                final_answer="N/A"
            )

            st.markdown("### 💡 Doubt Answer")
            st.write(answer)
