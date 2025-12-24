class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[dict]) -> list[dict]:
        """
        Normalizes extracted steps into a consistent schema.

        Expected input:
        [
            {
                "step_number": 1,
                "type": "rule_application",
                "rule": "power_rule",
                "input": "x**2",
                "output": "x**3/3",
                "hint": "Increase the exponent by 1 and divide by the new exponent"
            }
        ]
        """

        normalized_steps = []

        for idx, step in enumerate(steps, start=1):
            normalized_steps.append({
                "step_number": idx,
                "type": step.get("type", "unknown"),
                "rule": step.get("rule"),
                "input": step.get("input"),
                "output": step.get("output"),
                "explanation_hint": step.get("hint", "")
            })

        return normalized_steps
