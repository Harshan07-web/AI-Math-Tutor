import re

class StepNormalizer:
    def __init__(self):
        pass

    def normalize_steps(self, steps: list[str]) -> list[str]:
       
        normalized = []
        for i, step in enumerate(steps, 1):
            # Trim and clean
            step = re.sub(r'\s+', ' ', step.strip())
            # Add numbering and math delimiters if equations present
            if re.search(r'[=+\-*/^]', step):
                step = f"{i}. {step.split(':')[0]}: $$ {step.split(':')[-1].strip()} $$" if ':' in step else f"{i}. $$ {step} $$"
            else:
                step = f"{i}. {step}"
            normalized.append(step)
        
        return normalized
