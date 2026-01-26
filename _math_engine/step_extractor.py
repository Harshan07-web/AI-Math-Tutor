class StepExtractor:
    def __init__(self):
        pass

    def extract_steps(self, solver_output: dict) -> list[dict]:
        """
        Convert solver-generated steps into numbered step objects.
        """

        raw_steps = solver_output.get("steps", [])
        extracted_steps = []

        for idx, step in enumerate(raw_steps, start=1):
            extracted_steps.append({
                "step_number": idx,
                "type": step.get("type", "info"),
                "input": step.get("input"),
                "output": step.get("output"),
                "hint": step.get("explanation_hint")
            })

        return extracted_steps
