from PIL import Image
from sympy import Eq, sstr

from _vision.ocr import OCRProcessor
from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler
from _math_engine.latex_to_sympy import LatexToSympyConverter


class Pipeline:
    """
    End-to-end pipeline:
    Image / Text → OCR → LaTeX → SymPy → Solve → Steps → Explain
    """

    def __init__(self):
        self.ocr = OCRProcessor(use_preprocessing=True)
        self.solver = MathSolver()          # ❌ DO NOT MODIFY SOLVER
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.explainer = StepExplainer()
        self.doubt = DoubtHandler()

    # ------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------
    def solve_and_explain(self, user_input):
        latex_expr = None

        # -------------------------
        # 🖼 IMAGE INPUT
        # -------------------------
        if isinstance(user_input, Image.Image):
            print("🖼 OCR Mode: PIL Image detected")
            latex_expr = self.ocr.image_to_latex(user_input)

            if not latex_expr:
                return {
                    "error": "OCR failed",
                    "message": "Could not read math from image",
                    "expression": ""
                }

        # -------------------------
        # ✍️ TEXT INPUT
        # -------------------------
        elif isinstance(user_input, str):
            latex_expr = user_input.strip()

            if not latex_expr:
                return {
                    "error": "Empty input",
                    "message": "Please enter a math problem",
                    "expression": ""
                }

        else:
            return {
                "error": "Invalid input",
                "message": "Expected image or math text",
                "expression": ""
            }

        print("\n📐 LaTeX Input:")
        print(latex_expr)

        # -------------------------
        # 🔁 LaTeX → SymPy
        # -------------------------
        try:
            sympy_expr = LatexToSympyConverter.to_sympy(latex_expr)
        except Exception as e:
            return {
                "error": "LaTeX parsing failed",
                "message": str(e),
                "expression": latex_expr
            }

        print("\n🧠 SymPy Parsed Expression:")
        print(sympy_expr)

        # -------------------------
        # 🧮 SOLVE (🔥 FIXED SECTION)
        # -------------------------
        try:
            # ✅ Convert SymPy → solver-safe string
            if isinstance(sympy_expr, Eq):
                lhs = sstr(sympy_expr.lhs)   # forces explicit *
                rhs = sstr(sympy_expr.rhs)
                problem_str = f"{lhs} = {rhs}"
            else:
                problem_str = sstr(sympy_expr)

            print("\n🧮 Solver Input:")
            print(problem_str)

            # 🔑 ONLY public solver API
            result = self.solver.solve(problem_str)

        except Exception as e:
            return {
                "error": "Solver failure",
                "message": str(e),
                "expression": latex_expr
            }

        if not isinstance(result, dict):
            return {
                "error": "Invalid solver response",
                "message": "Solver did not return a valid result",
                "expression": latex_expr
            }

        # -------------------------
        # 🪜 STEP EXTRACTION
        # -------------------------
        try:
            steps = self.extractor.extract_steps(result)
            steps = self.normalizer.normalize_steps(steps)
        except Exception:
            steps = result.get("steps", [])

        # -------------------------
        # 🧠 EXPLANATION (LLM)
        # -------------------------
        explanation = self.explainer.explain_steps(
            normalized_steps=steps,
            final_answer=result.get("final_answer"),
            problem_type=result.get("problem_type")
        )

        # -------------------------
        # ✅ FINAL PAYLOAD
        # -------------------------
        result["expression"] = latex_expr
        result["steps"] = steps
        result["explanation"] = explanation

        return result

    # ------------------------------------------------------------
    # 🙋 DOUBT HANDLING
    # ------------------------------------------------------------
    def answer_doubt(self, step_number, question):
        return self.doubt.answer_doubt(step_number, question)
