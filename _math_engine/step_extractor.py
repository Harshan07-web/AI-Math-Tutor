from sympy import latex
import re

class StepExtractor:
    def __init__(self):
        pass

    def extract_steps(self, solution: str, problem_type: str = 'equation') -> list[str]:
        """
        Extract steps from a solution string (e.g., from MathSolver).
        
        Args:
            solution (str): Raw solution (e.g., "[x=2, x=3]").
            problem_type (str): Type to guide extraction.
        
        Returns:
            list[str]: Numbered steps as strings.
        """
        steps = []
        
        if problem_type == 'quadratic':
            # Example extraction for quadratic: factor, roots
            steps = [
                "1. Rewrite equation in standard form: ax^2 + bx + c = 0.",
                "2. Compute discriminant: D = b^2 - 4ac.",
                "3. Find roots: x = [-b ± sqrt(D)] / (2a).",
                f"4. Solutions: {solution}."
            ]
        else:
            # Generic extraction: Split on operations
            operations = re.split(r'(=|\+|-|\*|/|\^)', solution)
            for i, op in enumerate(operations):
                if op.strip() in ['=', '+', '-', '*', '/', '^']:
                    steps.append(f"{i+1}. Apply operation: {op.strip()}")
        
        # Use SymPy latex for math rendering if needed (return as strings)
        steps[-1] += f" Final: $$ {solution} $$"  # Inline math example
        
        return steps
