class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[dict]) -> list[dict]:
        """
        Ensure clean formatting of step text for UI or LLM use.
        """

        normalized = []

        for step in steps:
            normalized.append({
                "step_number": step["step_number"],
                "type": step.get("type", "info"),
                "input": step.get("input", ""),
                "output": step.get("output", ""),
                "hint": step.get("hint", "")
            })

        return normalized
