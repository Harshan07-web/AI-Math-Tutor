from PIL import Image
import re

from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler
#from _vision.ocr import OCRProcessor
from _nlp.statement_parser import StatementParser


class Pipeline:
    def __init__(self):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.explainer = StepExplainer()
        self.doubt = DoubtHandler()
        #self.ocr = OCRProcessor(use_preprocessing=True)
        self.statement_parser = StatementParser()

    # ---------------------------------------------------------
    # 🔍 DETECTION
    # ---------------------------------------------------------

    def _looks_like_statement_problem(self, text: str) -> bool:
        keywords = [
            "find", "solve", "calculate", "determine",
            "derivative", "differentiate", "integrate",
            "speed", "distance", "area", "rate"
        ]
        has_keywords = any(k in text.lower() for k in keywords)
        has_symbols = any(s in text for s in "=^*/()")
        return has_keywords and not has_symbols

    def _is_valid_math(self, text: str) -> bool:
        return bool(re.search(r"[0-9a-zA-Z=+\-*/^()]", text))

    # ---------------------------------------------------------
    # 🚀 MAIN PIPELINE
    # ---------------------------------------------------------

    def solve_and_explain(self, user_input) -> dict:

        # 🖼 IMAGE INPUT
        if isinstance(user_input, (str, Image.Image)):
            if isinstance(user_input, str) and user_input.lower().endswith((".png", ".jpg", ".jpeg")):
                img = Image.open(user_input)
                latex = self.ocr.image_to_latex(img)
                user_input = latex

            if isinstance(user_input, Image.Image):
                latex = self.ocr.image_to_latex(user_input)
                user_input = latex

        # 🧠 STATEMENT → NLP → EXPRESSION
        if isinstance(user_input, str) and self._looks_like_statement_problem(user_input):
            parsed = self.statement_parser.parse(user_input)

            if parsed.get("error"):
                return {
                    "error": "Statement parsing failed",
                    "message": "Could not convert word problem to math expression."
                }

            user_input = parsed["expression"]

        # ❌ INVALID INPUT
        if not isinstance(user_input, str) or not self._is_valid_math(user_input):
            return {
                "error": "Invalid input",
                "message": "Provide a valid math expression or word problem."
            }

        # 🧮 SOLVER
        result = self.solver.solve(user_input)

        if not isinstance(result, dict) or result.get("error"):
            return {
                "error": "Solver failed",
                "expression": user_input
            }

        result["expression"] = user_input

        # 🪜 STEPS
        extracted = self.extractor.extract_steps(result)
        normalized = self.normalizer.normalize_steps(extracted)

        explanation = self.explainer.explain_steps(
            normalized_steps=normalized,
            final_answer=result.get("final_answer", ""),
            problem_type=result.get("problem_type", "")
        )

        result["steps"] = normalized
        result["explanation"] = explanation
        return result

    # ---------------------------------------------------------
    # ❓ DOUBTS
    # ---------------------------------------------------------

    def answer_doubt(self, step_number: int, question: str):
        return self.doubt.answer_doubt(step_number, question)
