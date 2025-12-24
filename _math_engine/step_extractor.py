class StepExtractor:
    def __init__(self):
        pass

    def extract_steps(self, solver_output: dict) -> list[dict]:
        """
        Converts solver output into standardized step objects.

        Expected solver_output format:
        {
            "final_answer": "...",
            "steps": [ {...}, {...} ],
            "problem_type": "integration"
        }
        """

        if "steps" not in solver_output:
            raise ValueError("Solver output does not contain steps")

        extracted_steps = []

        for idx, step in enumerate(solver_output["steps"], start=1):
            extracted_steps.append({
                "step_number": idx,
                "type": step.get("type"),
                "rule": step.get("rule", None),
                "input": step.get("input"),
                "output": step.get("output"),
                "hint": step.get("explanation_hint")
            })

        return extracted_steps
