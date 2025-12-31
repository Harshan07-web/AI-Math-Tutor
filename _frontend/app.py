# app.py
import streamlit as st
from PIL import Image

# Import your backend modules
from _vision.ocr import OCRProcessor
from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer, MathExplainer
from _llm.doubt_handler import DoubtHandler

# Initialize backend components
ocr = OCRProcessor()
solver = MathSolver()
extractor = StepExtractor()
normalizer = StepNormalizer()
explainer = StepExplainer()
doubt_handler = DoubtHandler()

# ------------------- STREAMLIT UI -------------------
st.set_page_config(page_title="AI Math Tutor", page_icon="🧮", layout="wide")
st.title("🧮 AI Math Tutor")

# Sidebar for navigation
choice = st.sidebar.selectbox("Choose Mode", ["Solve Math Problem", "Ask Doubt"])

# ------------------- MODE 1: Solve Math Problem -------------------
if choice == "Solve Math Problem":
    st.subheader("Upload an image or type your math problem")
    
    # Input type selection
    input_type = st.radio("Input type", ["Image", "Text"])
    
    if input_type == "Image":
        uploaded_file = st.file_uploader("Upload an image of the math problem", type=["png","jpg","jpeg"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # OCR conversion
            latex = ocr.image_to_latex(image)
            st.markdown("**Detected Math Expression (LaTeX):**")
            st.latex(latex)
            
            problem_input = latex
    else:
        problem_input = st.text_area("Type your math problem here:")
    
    if st.button("Solve"):
        if not problem_input:
            st.warning("Please provide a math problem.")
        else:
            # Solve using backend
            solution = solver.solve(problem_input)
            
            # Extract and normalize steps
            raw_steps = extractor.extract_steps(solution)
            normalized_steps = normalizer.normalize_steps(raw_steps)
            
            # Display solution and steps
            st.markdown("### ✅ Solution:")
            st.write(solution.get("final_answer", "No solution found"))
            
            st.markdown("### 📋 Steps:")
            for step in normalized_steps:
                st.write(f"Step {step['step_number']}: {step['output']}")
            
            # Optional: LLM explanation
            st.markdown("### 🤓 Explanation:")
            explanation = explainer.explain_steps(normalized_steps, solution.get("final_answer",""))
            st.write(explanation)

# ------------------- MODE 2: Ask Doubt -------------------
elif choice == "Ask Doubt":
    st.subheader("Ask your doubt about a solved problem")
    
    problem = st.text_area("Original Problem")
    steps_input = st.text_area("Solution Steps (separate by new lines)")
    doubt = st.text_area("Your doubt about the steps")
    
    if st.button("Get Doubt Answer"):
        if not problem or not steps_input or not doubt:
            st.warning("Please fill all fields.")
        else:
            # Convert steps_input to structured format for DoubtHandler
            steps_list = [{"step_number": i+1, "output": s, "explanation_hint": ""} 
                          for i, s in enumerate(steps_input.split("\n"))]
            
            answer = doubt_handler.answer_doubt(
                user_question=doubt,
                normalized_steps=steps_list,
                final_answer="N/A"
            )
            st.markdown("### 💡 Doubt Answer:")
            st.write(answer)
