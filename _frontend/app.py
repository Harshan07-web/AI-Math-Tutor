# app.py
# =================== MUST BE AT TOP ===================
from dotenv import load_dotenv
load_dotenv()   # Load environment variables (API keys)
# =====================================================

import streamlit as st
from PIL import Image
import sys
import os

# Add project root to path so imports work correctly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ------------------- 1. LOAD PIPELINE -------------------
@st.cache_resource
def get_pipeline():
    """
    Initializes the Pipeline once and caches it.
    This prevents reloading heavy AI models on every button click.
    """
    try:
        from _core.pipeline import Pipeline
        return Pipeline()
    except ImportError as e:
        st.error(f"Failed to import Pipeline. Ensure 'pipeline.py' is in the same folder. Error: {e}")
        return None
    except Exception as e:
        st.error(f"Critical Error initializing models: {e}")
        st.info("💡 Tip: If this is a 'pix2tex' error, run: pip install 'pix2tex[gui]'")
        return None

# ------------------- 2. PAGE CONFIG & STATE -------------------
st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="🧮",
    layout="wide"
)

# Initialize Session State to remember history
if "history" not in st.session_state:
    st.session_state.history = {
        "latex": "",
        "solution": None,  # Will hold the dictionary returned by pipeline
    }

# Load the pipeline
with st.spinner("🧠 Waking up the AI Tutor..."):
    pipeline = get_pipeline()

if not pipeline:
    st.stop()  # Stop execution if pipeline failed to load

# ------------------- 3. SIDEBAR NAVIGATION -------------------
with st.sidebar:
    st.title("Navigation")
    mode = st.radio("Select Mode", ["📸 Solve Problem", "🙋‍♂️ Ask Doubt"])
    
    st.markdown("---")
    st.markdown("### 📝 Current Context")
    if st.session_state.history["solution"]:
        st.success("✅ Solution Loaded")
        if st.button("Clear History"):
            st.session_state.history = {"latex": "", "solution": None}
            st.rerun()
    else:
        st.caption("No problem solved yet.")

# ------------------- 4. MODE: SOLVE PROBLEM -------------------
if mode == "📸 Solve Problem":
    st.title("🧮 Solve & Explain")
    st.markdown("Upload a math problem image or type the LaTeX directly.")

    # --- Input Section ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        input_method = st.radio("Input Method", ["Image", "Text"], horizontal=True)

    user_input = None

    if input_method == "Image":
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Problem", width=400)
            user_input = image
    else:
        text_input = st.text_area("Enter Math Expression (LaTeX or standard)", value=st.session_state.history["latex"])
        if text_input:
            user_input = text_input

    # --- Solve Button ---
    if st.button("🚀 Solve Now", type="primary"):
        if not user_input:
            st.warning("Please upload an image or enter text first.")
        else:
            with st.spinner("🔍 Reading, Solving & Generating Explanation..."):
                # CALL THE PIPELINE
                result = pipeline.solve_and_explain(user_input)
                
                # Check for pipeline errors
                if result.get("error"):
                    st.error(f"❌ Error: {result.get('message')}")
                    if result.get("hint"):
                        st.info(f"💡 Hint: {result.get('hint')}")
                else:
                    # Save to session state
                    st.session_state.history["solution"] = result
                    if isinstance(user_input, str):
                        st.session_state.history["latex"] = user_input
                    else:
                        st.session_state.history["latex"] = result.get("expression", "")
                    
                    st.rerun() # Refresh to show results cleanly

    # --- Results Display ---
    sol = st.session_state.history["solution"]
    if sol:
        st.markdown("---")
        
        # 1. The Expression
        st.subheader("1. Identified Problem")
        st.latex(sol.get("expression", ""))

        # 2. The Final Answer
        st.subheader("2. Final Answer")
        st.info(sol.get("final_answer", "N/A"))

        # 3. Steps
        with st.expander("📂 View Step-by-Step Derivation", expanded=True):
            steps = sol.get("steps", [])
            if steps:
                for step in steps:
                    st.markdown(f"**Step {step['step_number']}**")
                    st.latex(step['output'])
            else:
                st.write("No intermediate steps available.")

        # 4. Explanation
        st.subheader("3. AI Tutor Explanation")
        st.markdown(sol.get("explanation", ""))

# ------------------- 5. MODE: ASK DOUBT -------------------
elif mode == "🙋‍♂️ Ask Doubt":
    st.title("💬 Doubt Session")

    # Check context
    sol = st.session_state.history["solution"]
    
    if not sol:
        st.warning("⚠️ Please solve a problem in the 'Solve Problem' tab first.")
        st.markdown("I need to know what math problem we are talking about before I can answer doubts!")
    else:
        # Display Context (Small)
        with st.expander("Reference: Current Problem", expanded=False):
            st.latex(sol.get("expression", ""))
            st.write(f"**Final Answer:** {sol.get('final_answer')}")

        st.subheader("What's confusing you?")
        
        col_step, col_q = st.columns([1, 3])
        
        with col_step:
            # Dropdown to select step number (0 could mean "General")
            steps = sol.get("steps", [])
            step_options = [s['step_number'] for s in steps]
            selected_step = st.selectbox("Related Step #", step_options)
        
        with col_q:
            question = st.text_input("Your Question", placeholder="e.g., Why did we divide by 2 here?")

        if st.button("🤔 Ask Tutor"):
            if not question:
                st.warning("Please type a question.")
            else:
                with st.spinner("Analyzing context..."):
                    # CALL THE PIPELINE DOUBT HANDLER
                    # Note: Using the signature defined in your pipeline.py
                    try:
                        answer = pipeline.answer_doubt(
                            step_number=selected_step, 
                            question=question
                        )
                        st.markdown("### 💡 Tutor's Answer")
                        st.success(answer)
                    except Exception as e:
                        st.error(f"Error processing doubt: {e}")