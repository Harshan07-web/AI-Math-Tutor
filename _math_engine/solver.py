import sympy as sp
from sympy import Eq, simplify
import re


class MathSolver:
    def __init__(self):
        pass

    def solve(self, user_input: str) -> dict:
        """Classify automatically based on notation & solve."""

        cleaned = user_input.replace("^", "**").strip()

        try:
            if "=" in cleaned:
                return self._solve_equation(cleaned)

            # Detect differentiation formats
            if cleaned.lower().startswith(("d/dx", "diff")):
                return self._solve_differentiation(cleaned)

            # Detect integration formats
            if cleaned.startswith("∫") or "integrate" in cleaned.lower():
                return self._solve_integration(self._extract_integrand(user_input))

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
    def _solve_differentiation(self, user_input: str) -> dict:
        expr_txt = user_input.replace("^", "**")

        # Extract expression inside d/dx(...)
        match = re.search(r"d/dx\s*\((.+)\)", expr_txt, flags=re.IGNORECASE)
        if not match:
            # Try diff(expr, x)
            match = re.search(r"diff\s*\((.+),\s*([a-zA-Z]+)\s*\)", expr_txt, flags=re.IGNORECASE)
            if not match:
                return {
                    "error": f"Could not understand differentiation input: {user_input}",
                    "message": "Try: d/dx(x^2) or diff(sin(x), x)"
                }
            expr_str = match.group(1)
            var = sp.Symbol(match.group(2))
        else:
            expr_str = match.group(1)
            var = sp.Symbol("x")

        try:
            expr = sp.sympify(expr_str)
        except Exception:
            return {
                "error": f"SymPy could not parse expression: {expr_str}",
                "message": "Rewrite using standard symbols: ^ → **, sin(x), etc."
            }

        steps = []
        final = None

        # ---- Quotient Rule ----
        if isinstance(expr, sp.Mul) and any(isinstance(a, sp.Pow) and a.exp == -1 for a in expr.args):
            f = expr.args[0]
            g = expr.args[1].base
            f_prime, g_prime = sp.diff(f, var), sp.diff(g, var)
            final = (f_prime * g - f * g_prime) / (g ** 2)
            steps.extend([
                f"1️⃣ Identify quotient: f={f}, g={g}",
                f"2️⃣ f'(x) = {f_prime}",
                f"3️⃣ g'(x) = {g_prime}",
                "4️⃣ Apply quotient rule: (f/g)' = (f'g - fg') / g²",
                f"5️⃣ Final result = {final}"
            ])

        # ---- Product Rule ----
        elif expr.is_Mul:
            f, g = expr.as_ordered_factors()
            f_prime, g_prime = sp.diff(f, var), sp.diff(g, var)
            final = f_prime * g + f * g_prime
            steps.extend([
                f"1️⃣ Identify product: f={f}, g={g}",
                f"2️⃣ f'(x) = {f_prime}",
                f"3️⃣ g'(x) = {g_prime}",
                "4️⃣ Apply product rule: (fg)' = f'g + fg'",
                f"5️⃣ Final result = {final}"
            ])

        # ---- Chain Rule ----
        elif expr.has(sp.sin) or expr.has(sp.cos) or isinstance(expr, sp.Pow):
            u = expr.args[0]
            final = sp.diff(expr, var)
            steps.extend([
                f"1️⃣ Identify inner function u = {u}",
                f"2️⃣ du/dx = {sp.diff(u, var)}",
                "3️⃣ Apply chain rule",
                f"4️⃣ Final result = {final}"
            ])

        # ---- Basic Differentiation ----
        else:
            final = sp.diff(expr, var)
            steps.append(f"1️⃣ Derivative = {final}")

        return {
            "final_answer": sp.sstr(final),
            "steps": steps,
            "problem_type": "differentiation",
            "latex": f"$$ {sp.latex(final)} $$"
        }

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _infer_variable(self, expr_str: str):
        symbols = re.findall(r"[a-zA-Z]", expr_str)
        return sp.Symbol(symbols[0]) if symbols else sp.Symbol("x")
