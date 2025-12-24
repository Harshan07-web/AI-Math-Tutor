import sympy as sp
from sympy import Eq


class MathSolver:
    def __init__(self):
        pass

    def solve(self, problem_input: dict) -> dict:
        """
        Solves a math problem deterministically using SymPy.

        Expected problem_input format:
        {
            "problem_type": "integration" | "differentiation" | "equation" | "simplification",
            "expression": "x**2",
            "variable": "x",
            "metadata": {...}   # ignored by solver
        }
        """

        try:
            problem_type = problem_input["problem_type"]
            expr_str = problem_input["expression"]
            var_str = problem_input.get("variable", None)

            # Create SymPy symbols
            if var_str:
                var = sp.symbols(var_str)
            else:
                var = None

            # Parse expression
            expr = sp.sympify(expr_str)

            # ---- INTEGRATION ----
            if problem_type == "integration":
                steps = []

                # Check if expression is a sum (linearity case)
                if isinstance(expr, sp.Add):
                    terms = expr.args  # individual terms

                    # Step 1: Linearity
                    steps.append({
                        "type": "linearity",
                        "input": str(expr),
                        "output": " + ".join([f"∫{t} dx" for t in terms]),
                        "explanation_hint": "Split the integral using linearity"
                    })

                    integrated_terms = []

                    # Step 2: Integrate each term
                    for term in terms:
                        result_term = sp.integrate(term, var)

                        # Decide rule type
                        if term.is_Number:
                            rule = "constant_rule"
                            hint = "The integral of a constant is the constant multiplied by x"
                        else:
                            rule = "power_rule"
                            hint = "Increase the exponent by 1 and divide by the new exponent"

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
                    # Single-term integration (no linearity needed)
                    final_result = sp.integrate(expr, var)

                    steps.append({
                        "type": "rule_application",
                        "rule": "power_rule",
                        "input": str(expr),
                        "output": str(final_result),
                        "explanation_hint": "Increase the exponent by 1 and divide by the new exponent"
                    })

                return {
                    "final_answer": f"{final_result} + C",
                    "steps": steps,
                    "problem_type": "integration"
                }
            # ---- DIFFERENTIATION ----
            elif problem_type == "differentiation":
                steps = []

                # Linearity check
                if isinstance(expr, sp.Add):
                    terms = expr.args

                    # Step 1: Linearity
                    steps.append({
                        "type": "linearity",
                        "input": str(expr),
                        "output": " + ".join([f"d/d{var}({t})" for t in terms]),
                        "explanation_hint": "Split the derivative using linearity"
                    })

                    differentiated_terms = []

                    for term in terms:
                        result_term = sp.diff(term, var)

                        if term.is_Number:
                            rule = "constant_rule"
                            hint = "The derivative of a constant is zero"
                        else:
                            rule = "power_rule"
                            hint = "Multiply by the exponent and reduce the power by 1"

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
                    # Single-term differentiation
                    final_result = sp.diff(expr, var)

                    steps.append({
                        "type": "rule_application",
                        "rule": "power_rule",
                        "input": str(expr),
                        "output": str(final_result),
                        "explanation_hint": "Multiply by the exponent and reduce the power by 1"
                    })

                return {
                    "final_answer": str(final_result),
                    "steps": steps,
                    "problem_type": "differentiation"
                }
            # ---- EQUATION SOLVING ----
            elif problem_type == "equation":
                if "=" not in expr_str:
                    raise ValueError("Equation must contain '='")

                left_str, right_str = expr_str.split("=", 1)
                left = sp.sympify(left_str)
                right = sp.sympify(right_str)

                eq = sp.Eq(left, right)
                steps = []

                # Step 1: Original equation
                steps.append({
                    "type": "equation",
                    "input": str(eq),
                    "output": str(eq),
                    "explanation_hint": "Start with the given equation"
                })

                # Step 2: Move constants to the right
                simplified_eq = sp.solve(eq, var, dict=True)

                steps.append({
                    "type": "isolation",
                    "input": str(eq),
                    "output": f"{var} = {simplified_eq[0][var]}",
                    "explanation_hint": "Isolate the variable on one side"
                })

                return {
                    "final_answer": f"{var} = {simplified_eq[0][var]}",
                    "steps": steps,
                    "problem_type": "equation"
                }

            # ---- SIMPLIFICATION ----
            elif problem_type == "simplification":
                result = sp.simplify(expr)

                steps = [
                    {
                        "type": "simplification",
                        "input": str(expr),
                        "output": str(result),
                        "explanation_hint": "Combine like terms and simplify the expression"
                    }
                ]

                return {
                    "final_answer": str(result),
                    "steps": steps,
                    "problem_type": "simplification"
                }

            else:
                raise ValueError(f"Unsupported problem type: {problem_type}")

        except Exception as e:
            raise ValueError(f"Solver error: {e}")


