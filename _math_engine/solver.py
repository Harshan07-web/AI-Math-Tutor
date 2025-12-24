from sympy import sympify, solve, Eq
from sympy.parsing.sympy_parser import parse_expr
import re

class MathSolver:
    def __init__(self):
        pass

    def solve(self, problem: str) -> dict:
        
        try:
            # Parse the equation (assume form 'expr1 = expr2')
            if '=' in problem:
                left, right = problem.split('=', 1)
                left = left.strip()
                right = right.strip()
                eq = Eq(sympify(left), sympify(right))
                variables = self._extract_variables(left + right)
                solutions = solve(eq, variables[0] if variables else None)
                
                # Generate basic steps (simplified; SymPy doesn't natively step-by-step)
                steps = self._generate_basic_steps(eq, solutions)
                
                return {
                    'solution': str(solutions),
                    'steps': steps,
                    'type': self._classify_problem(problem)
                }
            else:
                # For expressions (e.g., simplify)
                expr = sympify(problem)
                return {
                    'solution': str(expr),
                    'steps': [f"Simplified: {expr}"],
                    'type': 'simplification'
                }
        except Exception as e:
            raise ValueError(f"Could not solve problem: {e}")

    def _extract_variables(self, expr: str) -> list:
        """Extract variable symbols from expression."""
        vars_found = re.findall(r'[a-zA-Z]', expr)
        return list(set(vars_found))  # Unique variables

    def _generate_basic_steps(self, eq, solutions) -> list[str]:
        """Placeholder for steps; integrate with SymPy's printers for real use."""
        return [
            f"Equation: {eq}",
            f"Solve for variable: {solutions}"
        ]

    def _classify_problem(self, problem: str) -> str:
        """Simple classification."""
        if '^2' in problem and '=' in problem:
            return 'quadratic'
        return 'equation'
