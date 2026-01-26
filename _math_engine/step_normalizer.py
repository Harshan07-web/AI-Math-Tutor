class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[dict]) -> list[dict]:
        """
        Clean and format steps for UI and LLM.
        """
        normalized = []

        for step in steps:
            raw_type = step.get("type", "info")
            display_type = raw_type.replace("_", " ").title()

            normalized.append({
                "step_number": step.get("step_number"),
                "type": display_type,
                "input": step.get("input", ""),
                "output": step.get("output", ""),
                "hint": step.get("hint", "")
            })

        return normalized
