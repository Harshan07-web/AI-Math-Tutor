
from _core.pipeline import Pipeline

pipeline = Pipeline()

print("=== Solve ===")

# Change expression here for testing:
user_expression = "abc"
#user_expression = "3*(x-1)=15 "   # → Will ask: differentiate or integrate?
#user_expression = "∫(x^2 + 2) dx"  # If you later support symbolic integral frontend

result = pipeline.solve_and_explain(user_expression)

print(result)


import sympy as sp
from sympy import Eq, simplify


class MathSolver:
    def __init__(self):
        pass

    def solve(self, user_input: str) -> dict:
        """Classify automatically based on notation & solve."""

        cleaned = user_input.replace("^", "**").strip()

        try:
            if "=" in cleaned:
                return self._solve_equation(cleaned)

            if cleaned.lower().startswith(("d/dx", "diff")):
                return self._solve_differentiation(cleaned)

            return self._solve_integration(cleaned)

        except Exception:
            return {
                "error": f"I couldn't understand the input: {user_input}",
                "message": "Try rewriting using normal math syntax.",
                "hint": "Example: x^2 - 5x + 6 = 0 OR ∫(x^2 + 2)"
            }

    # --------------------------------------------------------------------
    # ➕ EQUATIONS (Linear & Quadratic)
    # --------------------------------------------------------------------
    def _solve_equation(self, eq_str: str) -> dict:
        left, right = eq_str.split("=", 1)
        left = sp.sympify(left)
        right = sp.sympify(right)

        eq = Eq(left, right)
        var = list(eq.free_symbols)[0] if eq.free_symbols else sp.Symbol("x")

        # Rewrite to standard form (move everything to LHS)
        std_form = simplify(left - right)

        steps = [
            f"1. Rewrite in standard form: {sp.sstr(std_form)} = 0"
        ]

        deg = sp.degree(std_form, var)

        if deg == 1:
            # Linear equation
            solution = sp.solve(eq, var)
            steps.append("2. Solve by isolating the variable")
            return self._format_response(solution, steps, "equation")

        elif deg == 2:
            # Quadratic: Try factorization
            factored = sp.factor(std_form)

            if factored != std_form:
                steps.append(
                    f"2. Factor the quadratic: {sp.sstr(factored)} = 0"
                )
                roots = sp.solve(eq, var)
                steps.append("3. Set each factor = 0 and solve")
                return self._format_response(roots, steps, "equation")

            # Fallback to quadratic formula
            steps.append("2. Use Quadratic Formula")
            a = std_form.as_coefficients_dict()[var**2]
            b = std_form.as_coefficients_dict()[var]
            c = std_form.as_coefficients_dict().get(1, 0)

            D = b**2 - 4*a*c
            steps.append(f"3. Compute discriminant: D = {sp.sstr(D)}")

            x1 = (-b + sp.sqrt(D)) / (2 * a)
            x2 = (-b - sp.sqrt(D)) / (2 * a)

            solution = [sp.simplify(x1), sp.simplify(x2)]
            steps.append("4. Apply quadratic formula and simplify")

            return self._format_response(solution, steps, "equation")

        else:
            # fallback generic solver
            solution = sp.solve(eq, var)
            steps.append("2. Solve equation using symbolic solver")
            return self._format_response(solution, steps, "equation")

    # --------------------------------------------------------------------
    # 🔁 Shared Formatting
    # --------------------------------------------------------------------
    def _format_response(self, solution, steps, ptype):
        # Convert to readable strings
        if isinstance(solution, list):
            sol_str = ", ".join([sp.sstr(s) for s in solution])
        else:
            sol_str = sp.sstr(solution)

        return {
            "final_answer": f"{sol_str}",
            "steps": steps,
            "problem_type": ptype,
            "latex": f"$$ {sp.latex(solution)} $$"
        }