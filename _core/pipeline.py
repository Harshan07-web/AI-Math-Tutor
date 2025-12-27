from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler

class Pipeline:
    def __init__(self):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.explainer = StepExplainer()
        self.doubt = DoubtHandler()

    def solve_and_explain(self, user_input: str) -> dict:
        result = self.solver.solve(user_input)

        # ⛔ STOP if solver reported error
        if result.get("error"):
            return {
                "error": result["error"],
                "message": "I couldn't understand that expression. Please rewrite it using standard math notation.",
                "hint": "Example: d/dx(x^2 + 3*x) or (x^2 + 3*x)^2"
            }

        # 🔹 Ask clarification if solver needs it
        if result.get("requires_clarification"):
            return result

        final_answer = result.get("final_answer", "")
        problem_type = result.get("problem_type", "")

        # Extract & normalize steps
        extracted_steps = self.extractor.extract_steps(result)
        normalized_steps = self.normalizer.normalize_steps(extracted_steps)

        # Ask LLM ONLY when valid steps exist
        explanation = self.explainer.explain_steps(
            normalized_steps=normalized_steps,
            final_answer=final_answer,
            problem_type=problem_type
        )

        result["steps"] = normalized_steps
        result["explanation"] = explanation
        return result

    def answer_doubt(self, step_number: int, question: str):
        return self.doubt.handle_doubt(step_number, question)
