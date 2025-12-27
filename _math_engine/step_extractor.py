class StepExtractor:
    def __init__(self):
        pass

    def extract_steps(self, solver_output: dict) -> list[dict]:
        """
        Convert raw solver steps into ordered, numbered step objects.
        """

        if "steps" not in solver_output:
            return []

        extracted_steps = []

        for idx, step in enumerate(solver_output["steps"], start=1):
            if isinstance(step, dict):
                extracted_steps.append({
                    "step_number": idx,
                    "type": step.get("type", "unknown"),
                    "input": step.get("input", None),
                    "output": step.get("output", None),
                    "hint": step.get("hint", None)
                })
            else:
                # Fallback string formatting if necessary
                extracted_steps.append({
                    "step_number": idx,
                    "type": "info",
                    "input": None,
                    "output": str(step),
                    "hint": None
                })

        return extracted_steps
