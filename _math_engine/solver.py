import os
import sympy as sp
from sympy import Eq, Integral, simplify
import re

# optional helpers for image OCR
try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

# try to use local latex -> sympy converter if present
try:
    from .latex_to_sympy import latex_to_sympy
except Exception:
    latex_to_sympy = None


class MathSolver:
    def __init__(self):
        pass

    def solve(self, user_input: str) -> dict:
        """Classify automatically based on notation & solve.
        Accepts plain text, LaTeX, or path to an image containing math.
        """

        # If input is an image path, extract text/LaTeX first
        if isinstance(user_input, str) and self._is_image_path(user_input):
            try:
                extracted = self._process_image(user_input)
                # if OCR returns something, continue solving that
                if extracted:
                    user_input = extracted
            except Exception as e:
                return {"error": "OCR failed", "message": str(e)}

        cleaned = self._to_sympy_friendly(user_input.strip())

        try:
            # -------------------------
            # EQUATIONS
            # -------------------------
            if "=" in cleaned:
                return self._solve_equation(cleaned)

            # -------------------------
            # DIFFERENTIATION
            # -------------------------
            if cleaned.lower().startswith(("d/dx", "diff", "deriv", "d/d")) or "d/d" in cleaned.lower():
                return self._solve_differentiation(cleaned)

            # -------------------------
            # INTEGRATION
            # -------------------------
            if cleaned.startswith("∫") or "integrate" in cleaned.lower() or cleaned.startswith("int("):
                integrand = self._extract_integrand(cleaned)
                return self._solve_integration(integrand)

            # -------------------------
            # FALLBACK: try to simplify/evaluate
            # -------------------------
            expr = sp.sympify(cleaned)
            simplified = sp.simplify(expr)

            return {
                "final_answer": sp.sstr(simplified),
                "steps": [f"Simplify the expression: {simplified}"],
                "problem_type": "simplification",
                "latex": f"$$ {sp.latex(simplified)} $$"
            }

        except Exception as e:
            return {
                "error": f"I couldn't understand the input: {user_input}",
                "message": str(e),
                "hint": "Example: 2x-3=7 | d/dx(x^2) | ∫ x^2 dx | path/to/image.png"
            }

    # --------------------------------------------------------------------
    # IMAGE / OCR HELPERS
    # --------------------------------------------------------------------
    def _is_image_path(self, path: str) -> bool:
        if not isinstance(path, str):
            return False
        if not os.path.isfile(path):
            return False
        return os.path.splitext(path)[1].lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}

    def _process_image(self, path: str) -> str:
        """Try to extract LaTeX or plain math text from an image file."""
        if Image is None or pytesseract is None:
            raise RuntimeError("PIL/pytesseract not available for OCR")

        img = Image.open(path).convert("L")
        # basic preprocessing: threshold can be added here if needed
        raw = pytesseract.image_to_string(img, config="--psm 6")
        raw = raw.strip()
        if not raw:
            raise ValueError("No text detected in image")

        # try to extract LaTeX between $...$ or \[...\]
        m = re.search(r"\$+(.+?)\$+|\\\[(.+?)\\\]|\\\((.+?)\\\)", raw, re.S)
        if m:
            # group will have the captured latex
            for g in m.groups():
                if g:
                    return g.strip()

        # fallback: return the raw OCR text (will be cleaned later)
        return raw

    # --------------------------------------------------------------------
    # NORMALIZATION / LATEX -> SYMPY
    # --------------------------------------------------------------------
    def _to_sympy_friendly(self, text: str) -> str:
        text = text.replace("^", "**")
        # remove displaystyle and common LaTeX wrappers
        text = re.sub(r"\\displaystyle", "", text)
        text = re.sub(r"\\left|\\right", "", text)
        text = text.strip()
        # if it looks like LaTeX and converter available, use it
        if latex_to_sympy and (r"\frac" in text or r"\sqrt" in text or "\\" in text or "$" in text):
            try:
                converted = latex_to_sympy(text)
                if converted:
                    return converted
            except Exception:
                pass

        # simple replacements to help sympy parse
        text = text.replace(r"\cdot", "*")
        text = text.replace(r"\times", "*")
        text = text.replace(" ", "")
        # common integral notation: ∫ f dx -> int(f, x)
        text = re.sub(r"∫\s*(.+)dx", r"int(\1, x)", text)
        # simple derivative short-hands
        text = re.sub(r"d/d([a-zA-Z])\s*\((.+)\)", r"diff(\2, \1)", text)
        # convert LaTeX sums/products (basic form) to SymPy
        # e.g. \sum_{k=1}^{n} f(k)  -> Sum(f(k), (k, 1, n))
        text = re.sub(
            r"\\sum_\{\s*([a-zA-Z]+)\s*=\s*([^}]+)\s*\}\^\{\s*([^}]+)\s*\}\s*(.+)",
            r"Sum(\4, (\1, \2, \3))",
            text
        )
        text = re.sub(
            r"\\prod_\{\s*([a-zA-Z]+)\s*=\s*([^}]+)\s*\}\^\{\s*([^}]+)\s*\}\s*(.+)",
            r"Product(\4, (\1, \2, \3))",
            text
        )
        return text

    # --------------------------------------------------------------------
    # ➕ EQUATIONS
    # --------------------------------------------------------------------
    def _solve_equation(self, eq_str: str) -> dict:
        left, right = eq_str.split("=", 1)
        left = sp.sympify(left)
        right = sp.sympify(right)

        eq = Eq(left, right)
        vars_ = list(eq.free_symbols)
        var = vars_[0] if vars_ else sp.Symbol("x")

        std_form = simplify(left - right)

        steps = [f"1. Rewrite in standard form: {std_form} = 0"]

        deg = None
        try:
            deg = sp.degree(std_form, var)
        except Exception:
            deg = None

        if deg == 1:
            sol = sp.solve(eq, var)
            steps.append("2. Solve by isolating the variable")
            return self._format_response(sol, steps, "equation")

        if deg == 2:
            factored = sp.factor(std_form)
            if factored != std_form:
                steps.append(f"2. Factor: {factored} = 0")
                sol = sp.solve(eq, var)
                steps.append("3. Solve each factor")
                return self._format_response(sol, steps, "equation")

        sol = sp.solve(eq, var)
        steps.append("2. Solve using symbolic solver")
        return self._format_response(sol, steps, "equation")

    # --------------------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------------------
    def _format_response(self, solution, steps, ptype):
        sol_str = ", ".join(map(str, solution)) if isinstance(solution, (list, tuple)) else str(solution)
        # convert solution to a LaTeX-friendly string
        try:
            latex_repr = sp.latex(solution)
        except Exception:
            latex_repr = sol_str
        return {
            "final_answer": sol_str,
            "steps": steps,
            "problem_type": ptype,
            "latex": f"$$ {latex_repr} $$"
        }

    # --------------------------------------------------------------------
    # INTEGRATION
    # --------------------------------------------------------------------
    def _extract_integrand(self, text: str) -> str:
        text = text.replace("^", "**")
        # try to find int(expr, var) or integrate(expr, var) or ∫...dx
        m = re.search(r"int\(\s*(.+?)\s*,\s*([a-zA-Z])\s*\)", text)
        if m:
            return m.group(1)
        m = re.search(r"integrate\(\s*(.+?)\s*(,\s*([a-zA-Z]))?\s*\)", text, re.I)
        if m:
            return m.group(1)
        m = re.search(r"∫\s*\(?(.+?)\)?\s*d([a-zA-Z])", text)
        if m:
            return m.group(1)
        # fallback: try to strip 'integrate' or '∫' markers
        text = re.sub(r"integrate", "", text, flags=re.I)
        text = text.lstrip("∫")
        return text

    def _solve_integration(self, expr_str: str) -> dict:
        expr = sp.sympify(self._to_sympy_friendly(expr_str))
        var = self._infer_variable(expr_str)
        result = sp.integrate(expr, var)

        return {
            "final_answer": f"{result} + C",
            "steps": [f"Integrate with respect to {var}"],
            "problem_type": "integration",
            "latex": f"$$ {sp.latex(result)} + C $$"
        }

    # --------------------------------------------------------------------
    # DIFFERENTIATION
    # --------------------------------------------------------------------
    def _solve_differentiation(self, user_input: str) -> dict:
        expr_txt = user_input.replace("^", "**")

        m = re.search(r"d/d([a-zA-Z])\s*\((.+)\)", expr_txt, re.I)
        if m:
            var = sp.Symbol(m.group(1))
            expr = sp.sympify(self._to_sympy_friendly(m.group(2)))
        else:
            m = re.search(r"diff\(\s*(.+?)\s*,\s*([a-zA-Z])\s*\)", expr_txt, re.I)
            if not m:
                # try simple shorthand d/dx f where f follows
                m2 = re.search(r"d/d([a-zA-Z])\s+(.+)", expr_txt)
                if m2:
                    var = sp.Symbol(m2.group(1))
                    expr = sp.sympify(self._to_sympy_friendly(m2.group(2)))
                else:
                    return {"error": "Couldn't parse differentiation input"}

            else:
                var = sp.Symbol(m.group(2))
                expr = sp.sympify(self._to_sympy_friendly(m.group(1)))

        result = sp.diff(expr, var)

        return {
            "final_answer": str(result),
            "steps": [f"Differentiate with respect to {var}"],
            "problem_type": "differentiation",
            "latex": f"$$ {sp.latex(result)} $$"
        }

    # --------------------------------------------------------------------
    # VARIABLE INFERENCE
    # --------------------------------------------------------------------
    def _infer_variable(self, text: str) -> str:
        # crude variable inference: look for x, y, z, t, or any letter
        m = re.search(r"[a-zA-Z]", text)
        if m:
            return sp.Symbol(m.group(0))
        return sp.Symbol("x")  # fallback to x

    def solve(self, expr):
        # Differentiation
        if isinstance(expr, sp.Derivative):
            return expr.doit()

        # Integration
        if isinstance(expr, sp.Integral):
            return expr.doit()

        # Equations
        if isinstance(expr, sp.Eq):
            return sp.solve(expr)

        # Expressions / simplify
        return sp.simplify(expr)
