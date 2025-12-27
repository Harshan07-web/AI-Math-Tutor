import sympy as sp
import re


class MathSolver:
    def __init__(self):
        pass

    def solve(self, user_input: str) -> dict:
        """
        Master solve function with automatic detection:
        - Integration: ∫, integrate(), etc.
        - Differentiation: d/dx(), diff()
        - Algebra: ask user for type
        """
        try:
            cleaned = user_input.replace(" ", "").replace("^", "**")

            # Detect differentiation formats
            if cleaned.lower().startswith(("d/dx", "diff")):
                return self._solve_differentiation(cleaned)

            # Detect integration formats
            if cleaned.startswith("∫") or "integrate" in cleaned.lower():
                return self._solve_integration(self._extract_integrand(user_input))

            # Algebraic → clarification needed
            if any(ch.isalpha() for ch in user_input):
                return {
                    "requires_clarification": True,
                    "expression": user_input,
                    "message": f"I see an expression: {user_input}. Do you want to differentiate or integrate it?"
                }

            return {"error": "Invalid or unsupported input."}

        except Exception as e:
            return {
                "error": f"{str(e)}",
                "steps": []
            }

    # ------------------------------------------------------------
    # Integration
    # ------------------------------------------------------------
    def _extract_integrand(self, text: str) -> str:
        """Extract integrand & set default variable."""
        text = text.replace("^", "**")

        # ∫( ... )dx   → extract inside parenthesis
        match = re.search(r"∫\(?(.+?)\)?dx", text.replace(" ", ""))
        if match:
            return match.group(1)

        # ∫ x^2        → no dx → assume x
        if text.startswith("∫"):
            return text[1:]

        # Integrate x^2 + 2
        if "integrate" in text.lower():
            return text.lower().replace("integrate", "").strip()

        raise ValueError("Unable to detect integrand")

    def _solve_integration(self, expr_str: str) -> dict:
        expr = sp.sympify(expr_str)
        var = self._infer_variable(expr_str)

        steps = []
        if isinstance(expr, sp.Add):
            terms = expr.args
            steps.append(f"1. Break into separate integrals: {expr}")

            integrated_terms = []
            step = 2

            for term in terms:
                result = sp.integrate(term, var)
                rule = "constant rule" if term.is_Number else "power rule"

                steps.append(f"{step}. Apply {rule}: ∫{term} dx = {result}")
                step += 1
                integrated_terms.append(result)

            final = sum(integrated_terms)
        else:
            final = sp.integrate(expr, var)
            steps.append(f"1. Apply power rule: ∫{expr} dx = {final}")

        return {
            "final_answer": f"{sp.sstr(final)} + C",
            "steps": steps,
            "problem_type": "integration"
        }

    # ------------------------------------------------------------
    # Differentiation
    # ------------------------------------------------------------
    def _solve_differentiation(self, cleaned: str) -> dict:
        # d/dx(...)
        if cleaned.lower().startswith("d/dx"):
            expr = cleaned[4:-1]
            var = sp.Symbol("x")
        else:
            inside = cleaned[5:-1]
            expr, var = inside.split(",")
            var = sp.Symbol(var)

        expr = sp.sympify(expr)
        steps = []

        # ---- Quotient Rule ----
        if isinstance(expr, sp.Mul) and any(isinstance(a, sp.Pow) and a.exp == -1 for a in expr.args):
            f = expr.args[0]
            g = expr.args[1].base
            f_prime = sp.diff(f, var)
            g_prime = sp.diff(g, var)
            final = (f_prime*g - f*g_prime) / (g**2)

            steps.extend([
                f"1️⃣ Identify quotient: f(x)={f}, g(x)={g}",
                f"2️⃣ f'(x) = {f_prime}",
                f"3️⃣ g'(x) = {g_prime}",
                "4️⃣ Apply quotient rule: (f/g)' = (f'g - fg') / g²",
                f"5️⃣ Final result = {final}"
            ])

        # ---- Chain Rule ----
        elif isinstance(expr, sp.Pow) or any(expr.has(f) for f in [sp.sin, sp.cos, sp.exp]):
            u = expr.args[0] if isinstance(expr, sp.Pow) else expr.args[0]
            outer_derivative = sp.diff(expr.subs(u, sp.Symbol("u")), sp.Symbol("u"))
            inner_derivative = sp.diff(u, var)
            final = sp.diff(expr, var)

            steps.extend([
                f"1️⃣ Identify inner function u = {u}",
                f"2️⃣ Compute du/dx = {inner_derivative}",
                f"3️⃣ Compute derivative of outer: d/du({expr}) = {outer_derivative}",
                "4️⃣ Apply chain rule: (outer ∘ inner)' = outer'(inner) · inner'",
                f"5️⃣ Final result = {final}"
            ])

        # ---- Product Rule ----
        elif isinstance(expr, sp.Mul):
            f, g = expr.as_ordered_factors()
            f_prime, g_prime = sp.diff(f, var), sp.diff(g, var)
            final = f_prime*g + f*g_prime

            steps.extend([
                f"1️⃣ Identify product: f(x)={f}, g(x)={g}",
                f"2️⃣ f'(x) = {f_prime}",
                f"3️⃣ g'(x) = {g_prime}",
                "4️⃣ Apply product rule: (fg)' = f'g + fg'",
                f"5️⃣ Final result = {final}"
            ])

        # ---- Simple differentiation ----
        else:
            final = sp.diff(expr, var)
            steps.append(f"1️⃣ Derivative: {final}")

        return {
            "final_answer": sp.sstr(final),
            "steps": steps,
            "problem_type": "differentiation"
        }
    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _infer_variable(self, expr_str: str):
        symbols = re.findall(r"[a-zA-Z]", expr_str)
        return sp.Symbol(symbols[0]) if symbols else sp.Symbol("x")
