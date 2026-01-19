from PIL import Image
from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler
#from _vision.ocr import OCRProcessor
import os
import re


class Pipeline:
    def __init__(self):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.explainer = StepExplainer()
        self.doubt = DoubtHandler()
        #self.ocr = OCRProcessor(use_preprocessing=True)

    def _clean_math_expr(self, latex_str: str) -> str:
        """
        Translates raw LaTeX from OCR into SymPy-compatible string.
        Example: "\frac{x}{2}" -> "(x)/(2)"
        """
        if not latex_str:
            return ""

        # 1. Basic Cleanups
        expr = latex_str.replace(" ", "")  # Remove whitespace
        expr = expr.replace(r"\left", "").replace(r"\right", "") # Remove sizing tags
        expr = expr.replace("{", "(").replace("}", ")") # Convert brackets
        
        # 2. Convert LaTeX symbols to Python
        replacements = {
            r"\times": "*",
            r"\cdot": "*",
            r"\div": "/",
            r"\pi": "pi",
            r"\sqrt": "sqrt",
            r"\sin": "sin",
            r"\cos": "cos",
            r"\tan": "tan",
            r"\log": "log",
            r"\ln": "ln",
            r"\int": "integrate", 
            "^": "**"
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)

        # 3. Handle Fractions: \frac(a)(b) -> ((a)/(b))
        # This regex looks for \frac followed by two groups in parentheses
        expr = re.sub(r"\\frac\((.*?)\)\((.*?)\)", r"((\1)/(\2))", expr)

        # 4. Remove any remaining backslashes (cleanup)
        expr = expr.replace("\\", "")
        
        return expr.strip()

    
    def solve_and_explain(self, user_input) -> dict:

        # 🔍 Detect if input is a filepath image
        if isinstance(user_input, str) and user_input.lower().endswith((".png", ".jpg", ".jpeg")):
            print("📸 OCR Mode: Image File Detected")

            try:
                img = Image.open(user_input)
                user_input = self.ocr.image_to_latex(img)
            except Exception:
                return {
                    "error": "File error",
                    "message": "Cannot load the image file.",
                    "expression": ""
                }

        # 🖼 Detect if input is a PIL image object
        elif isinstance(user_input, Image.Image):
            print("🖼 OCR Mode: PIL Image Detected")
            latex_expr = self.ocr.image_to_latex(user_input)

            if not latex_expr or latex_expr.strip() == "":
                return {
                    "error": "OCR failed",
                    "message": "Could not extract math from image",
                    "expression": ""
                }

            print("\n📐 OCR Raw Output:", latex_expr)

            # 🧽 Clean Latex → SymPy-friendly format
            user_input = self._clean_math_expr(latex_expr)
            print("✨ Cleaned Expression:", user_input)

            if not user_input or not isinstance(user_input, str):
                return {
                    "error": "OCR failed",
                    "message": "The OCR did not extract valid math from the image.",
                    "expression": ""
                }


        # 🧹 Validate OCR output or text input
        if not isinstance(user_input, str) or user_input.strip() == "":
            return {
                "error": "Invalid or unreadable input",
                "message": "Provide a valid math expression or a clear math image.",
                "expression": ""
            }

        # 🧠 Solve
        result = self.solver.solve(user_input)

# 🚨 Validate solver output before accessing dictionary keys
        if not isinstance(result, dict):
            return {
                "error": "Internal solver failure",
                "message": "The math solver could not process the expression.",
                "expression": user_input
            }

        result["expression"] = user_input  # always store expression


        # ⛔ Error handling from the solver
        if result.get("error"):
            return {
                "error": result["error"],
                "message": "I couldn't understand that. Try rewriting the math clearly.",
                "hint": "Example: d/dx(x^2 + 3*x) or (x^2 + 3*x)^2"
            }

        # ❓ Clarification required case
        if result.get("requires_clarification"):
            return result

        final_answer = result.get("final_answer", "")
        problem_type = result.get("problem_type", "")

        # 🪜 Extract → Normalize → Explain
        extracted_steps = self.extractor.extract_steps(result)
        normalized_steps = self.normalizer.normalize_steps(extracted_steps)

        explanation = self.explainer.explain_steps(
            normalized_steps=normalized_steps,
            final_answer=final_answer,
            problem_type=problem_type
        )

        result["steps"] = normalized_steps
        result["explanation"] = explanation
        return result

    def answer_doubt(self, step_number: int, question: str):
        return self.doubt.answer_doubt(step_number, question)