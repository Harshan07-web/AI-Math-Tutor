import sympy as sp
from sympy import Eq


class MathSolver:
    def __init__(self):
        pass

    def _detect_variable(self, expr: str) -> str:
        """Detect variable automatically from input."""
        for ch in expr:
            if ch.isalpha():
                return ch
        return 'x'  # fallback

    def _classify_problem(self, problem_str: str) -> str:
        """Simple rule-based classification."""
        if "=" in problem_str:
            return "equation"
        if "d/d" in problem_str.lower():
            return "differentiation"
        return "integration"  # default for expressions

    def solve(self, problem_str: str) -> dict:
        """
        Accept raw math string input (not dict)
        Detects problem type, parses, and solves step-by-step.
        """
        try:
            # Problem understanding
            problem_type = self._classify_problem(problem_str)
            var_str = self._detect_variable(problem_str)
            var = sp.symbols(var_str)

            # Parse expression
            if problem_type == "equation":
                if "=" not in problem_str:
                    raise ValueError("Equation must contain '='")

                left_str, right_str = problem_str.split("=", 1)
                left = sp.sympify(left_str)
                right = sp.sympify(right_str)
                expr = Eq(left, right)
            else:
                expr = sp.sympify(problem_str)

            # --------------- INTEGRATION ---------------
            if problem_type == "integration":
                steps = []
                if isinstance(expr, sp.Add):
                    terms = expr.args

                    # Step 1: Linear splitting
                    steps.append({
                        "type": "linearity",
                        "input": str(expr),
                        "output": " + ".join([f"∫{t} d{var_str}" for t in terms]),
                        "explanation_hint": "Split the integral using linearity"
                    })

                    integrated_terms = []

                    for term in terms:
                        result_term = sp.integrate(term, var)
                        if term.is_Number:
                            rule = "constant_rule"
                            hint = "The integral of a constant is the constant multiplied by x"
                        else:
                            rule = "power_rule"
                            hint = "Increase exponent by 1 and divide by the new exponent"

                        steps.append({
                            "type": "rule_application",
                            "rule": rule,
                            "input": str(term),
                            "output": str(result_term),
                            "explanation_hint": hint
                        })

                        integrated_terms.append(result_term)

                    final_result = sum(integrated_terms)

                else:
                    final_result = sp.integrate(expr, var)

                    steps.append({
                        "type": "rule_application",
                        "rule": "power_rule",
                        "input": str(expr),
                        "output": str(final_result),
                        "explanation_hint": "Increase exponent by 1 and divide by the new exponent"
                    })

                return {
                    "final_answer": f"{final_result} + C",
                    "steps": steps,
                    "problem_type": "integration"
                }

            # --------------- DIFFERENTIATION ---------------
            elif problem_type == "differentiation":
                expr = sp.sympify(
                    problem_str.lower().replace(f"d/d{var_str}(", "").replace(")", "")
                )
                steps = []

                if isinstance(expr, sp.Add):
                    terms = expr.args

                    steps.append({
                        "type": "linearity",
                        "input": str(expr),
                        "output": " + ".join([f"d({t})/d{var_str}" for t in terms]),
                        "explanation_hint": "Split derivative using linearity"
                    })

                    differentiated_terms = []

                    for term in terms:
                        result_term = sp.diff(term, var)
                        if term.is_Number:
                            rule = "constant_rule"
                            hint = "The derivative of a constant is 0"
                        else:
                            rule = "power_rule"
                            hint = "Multiply exponent and subtract 1"

                        steps.append({
                            "type": "rule_application",
                            "rule": rule,
                            "input": str(term),
                            "output": str(result_term),
                            "explanation_hint": hint
                        })

                        differentiated_terms.append(result_term)

                    final_result = sum(differentiated_terms)

                else:
                    final_result = sp.diff(expr, var)

                    steps.append({
                        "type": "rule_application",
                        "rule": "power_rule",
                        "input": str(expr),
                        "output": str(final_result),
                        "explanation_hint": "Multiply exponent and subtract 1"
                    })

                return {
                    "final_answer": str(final_result),
                    "steps": steps,
                    "problem_type": "differentiation"
                }

            # --------------- EQUATION SOLVING ---------------
            elif problem_type == "equation":
                eq = expr
                steps = []

                solutions = sp.solve(eq, var, dict=True)

                steps.append({
                    "type": "isolation",
                    "input": str(eq),
                    "output": f"{var} = {solutions[0][var]}",
                    "explanation_hint": "Isolate the variable"
                })

                return {
                    "final_answer": f"{var} = {solutions[0][var]}",
                    "steps": steps,
                    "problem_type": "equation"
                }

            else:
                raise ValueError(f"Unsupported type: {problem_type}")

        except Exception as e:
            raise ValueError(f"Solver Error: {str(e)}")
