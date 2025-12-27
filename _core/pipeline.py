from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer
from _llm.explainer import StepExplainer
from _llm.doubt_handler import DoubtHandler

class MathPipeline:
    def __init__(self):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.explainer = StepExplainer()
        self.doubts = DoubtHandler()

        self.last_normalized_steps = None
        self.last_explanation = None
        self.last_answer = None

    def solve_and_explain(self, user_input: str) -> dict:
        solve_result = self.solver.solve(user_input)
        final_answer = solve_result["final_answer"]
        steps = solve_result["steps"]
        problem_type = solve_result["problem_type"]

        extracted = self.extractor.extract_steps(solve_result)

        normalized_steps = self.normalizer.normalize_steps(extracted)

        explanation = self.explainer.explain_steps(
            normalized_steps, final_answer
        )

        self.last_normalized_steps = normalized_steps
        self.last_explanation = explanation
        self.last_answer = final_answer

        return {
            "final_answer": final_answer,
            "steps": normalized_steps,
            "explanation": explanation,
            "type": problem_type
        }

    def answer_doubt(self, user_question: str) -> str:
        if not self.last_normalized_steps:
            return "Please solve a problem first 😊"

        return self.doubts.answer_doubt(
            user_question=user_question,
            normalized_steps=self.last_normalized_steps,
            final_answer=self.last_answer,
            previous_explanation=self.last_explanation
        )