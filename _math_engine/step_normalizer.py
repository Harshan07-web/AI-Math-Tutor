class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[dict]) -> list[dict]:


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
