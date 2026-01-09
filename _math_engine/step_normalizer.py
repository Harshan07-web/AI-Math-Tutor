class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[dict]) -> list[dict]:
        """
        Ensure clean formatting of step text for UI or LLM use.
        """
        normalized = []

        for step in steps:
            # OPTIONAL IMPROVEMENT: Clean up the 'type' for display
            raw_type = step.get("type", "info")
            display_type = raw_type.replace("_", " ").title() # "product_rule" -> "Product Rule"

            normalized.append({
                "step_number": step["step_number"],
                "type": display_type,  # Use the cleaner version
                "input": step.get("input", ""),
                "output": step.get("output", ""),
                "hint": step.get("hint", "")
            })

        return normalized