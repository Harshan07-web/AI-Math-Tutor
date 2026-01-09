import sympy as sp
from sympy import Eq, simplify
import re


class MathSolver:
    def __init__(self):
        pass

    def solve(self, user_input: str) -> dict:
        """Classify automatically based on keywords & solve."""
        cleaned = user_input.replace("^", "**").strip()

        try:
            # 1. Differentiation detection
            # Matches: diff, differentiate, d/dx, derivative
            diff_keywords = ["d/dx", "diff", "differentiate", "derivative"]
            if any(k in cleaned.lower() for k in diff_keywords):
                return self._solve_differentiation(cleaned)

            # 2. Integration detection
            # Matches: ∫, integrate, integral
            int_keywords = ["∫", "integrate", "integral"]
            if any(k in cleaned.lower() for k in int_keywords):
                return self._solve_integration(self._extract_integrand(cleaned))
            
            # 3. Equation detection (if "=" is present)
            if "=" in cleaned:
                return self._solve_equation(cleaned)

        except Exception:
            return {
                "error": f"I couldn't understand the input: {user_input}",
                "message": "Try rewriting using normal math syntax.",
                "hint": "Example: differentiate(x^2) or integrate(x+2)"
            }
        
        return {"error": "Unknown command", "message": "Try: differentiate(x^2) or x^2+5=0"}
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
        """
        Formats the output into a clean, vertical 'Notebook Style' layout 
        instead of a cramped table.
        """
        # 1. Start with the problem type header
        formatted_lines = [f"### Solution for {ptype.capitalize()}", ""]

        # 2. Iterate through steps and format them vertically
        for i, step_text in enumerate(steps, 1):
            # Clean up existing numbering if present (e.g., "1. Apply...")
            clean_text = re.sub(r"^\d+\.\s*", "", step_text)
            
            # Add a bold Step header
            formatted_lines.append(f"**Step {i}:**")
            
            # Check if the step has math that should be displayed on its own line
            # (Heuristic: if it contains an equals sign or '∫', indent it)
            if "=" in clean_text or "∫" in clean_text:
                formatted_lines.append(f"> {clean_text}")
            else:
                formatted_lines.append(f"{clean_text}")
            
            formatted_lines.append("") # Empty line for breathing room

        # 3. Add the Final Answer prominently
        formatted_lines.append("---")
        formatted_lines.append("### Final Answer")
        
        # We format the final solution in a LaTeX block for clear visibility
        latex_sol = sp.latex(solution)
        formatted_lines.append(f"$$ {latex_sol} $$")

        # Join it all into one string
        full_output = "\n".join(formatted_lines)

        return {
            "final_answer": sp.sstr(solution),
            "latex": latex_sol,
            "steps": steps,          # Keep raw list for code usage
            "display": full_output   # Use this for printing to the user
        }
    # ------------------------------------------------------------
    # Integration
    # ------------------------------------------------------------
    def _extract_integrand(self, text: str) -> str:
        """Extracts the math part from integrate() or ∫...dx strings."""
        text = text.replace("^", "**")

        # 1. Remove the keywords (integrate, ∫, integral)
        # We replace them with an empty string
        clean = re.sub(r"(integrate|integral|∫)\s*", "", text, flags=re.IGNORECASE)

        # 2. Remove outer parentheses if they exist
        # e.g., "(x^2 + 5)" becomes "x^2 + 5"
        clean = clean.strip()
        if clean.startswith("(") and clean.endswith(")"):
            # Check if these parens are actually matching outer parens
            # (simple check)
            clean = clean[1:-1]

        # 3. Remove trailing 'dx', 'dy', 'dt' if present
        # This handles "integrate(x^2 dx)" or "∫ x^2 dx"
        clean = re.sub(r"\s*d[a-zA-Z]$", "", clean, flags=re.IGNORECASE)

        return clean.strip()

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

        # Regex explanation:
        # 1. (?: ... ) matches the keyword (differentiate OR diff OR d/dx)
        # 2. \s*\(? matches optional space and optional opening '('
        # 3. (.+) captures the content inside
        # 4. \)? matches optional closing ')'
        match = re.search(r"(?:differentiate|diff|d/dx|derivative)\s*\(?(.+?)\)?$", expr_txt, flags=re.IGNORECASE)

        if match:
            content = match.group(1).strip()
            # Remove trailing closing parenthesis if the regex caught it oddly (e.g. nested brackets)
            if content.endswith(")") and not content.count("(") == content.count(")"):
                content = content[:-1]
        else:
            return {"error": "Could not parse differentiation input."}

        # Check for explicitly defined variable (e.g., "x**2, y")
        # We look for a comma followed by a single letter at the end
        var_match = re.search(r",\s*([a-zA-Z])$", content)
        
        if var_match:
            # User specified a variable: diff(x*y, y)
            var_str = var_match.group(1)
            var = sp.Symbol(var_str)
            # The expression is everything BEFORE the last comma
            expr_str = content[:var_match.start()].strip()
        else:
            # Default behavior: diff(x^2) -> implies x
            var = sp.Symbol("x")
            expr_str = content

        try:
            expr = sp.sympify(expr_str)
        except Exception:
            return {
                "error": f"SymPy could not parse expression: {expr_str}",
                "message": "Ensure your parentheses match."
            }
        steps = []
        final = sp.diff(expr, var) 

        # 2. Step Logic (Now generating Data Objects)
        try:
            # ---- Quotient Rule Check ----
            if isinstance(expr, sp.Mul):
                denom = [a for a in expr.args if (isinstance(a, sp.Pow) and a.exp == -1)]
                if denom:
                    g_part = denom[0].base 
                    f_part = expr * g_part 
                    
                    f_prime = sp.diff(f_part, var)
                    g_prime = sp.diff(g_part, var)
                    
                    # Store steps as distinct data points
                    steps.append({
                        "type": "identification",
                        "output": f"Identify Quotient Rule: f(x)={sp.sstr(f_part)}, g(x)={sp.sstr(g_part)}",
                        "hint": "Formula: (f'g - fg') / g^2"
                    })
                    
                    steps.append({
                        "type": "derivation",
                        "output": f"Differentiate Numerator: f'(x) = {sp.sstr(f_prime)}"
                    })

                    steps.append({
                        "type": "derivation",
                        "output": f"Differentiate Denominator: g'(x) = {sp.sstr(g_prime)}"
                    })
                    
                    steps.append({
                        "type": "calculation",
                        "output": f"Apply Rule: ({sp.sstr(f_prime)})*({sp.sstr(g_part)}) - ({sp.sstr(f_part)})*({sp.sstr(g_prime)}) / ({sp.sstr(g_part)})^2"
                    })
                    
                    steps.append({
                        "type": "simplification",
                        "output": f"Simplify: {sp.sstr(final)}"
                    })
                    
                    # Return the data-rich response
                    return {
                        "final_answer": sp.sstr(final),
                        "latex": sp.latex(final),
                        "problem_type": "Differentiation",
                        "steps": steps
                    }

            # ---- Product Rule Check ----
            if isinstance(expr, sp.Mul):
                factors = expr.as_ordered_factors()
                if len(factors) >= 2:
                    f = factors[0]
                    g = sp.Mul(*factors[1:])
                    
                    f_prime = sp.diff(f, var)
                    g_prime = sp.diff(g, var)

                    steps.append({
                        "type": "identification",
                        "output": f"Identify Product Rule: f={sp.sstr(f)}, g={sp.sstr(g)}",
                        "hint": "Formula: f'g + fg'"
                    })
                    
                    steps.append({
                        "type": "derivation",
                        "output": f"Differentiate terms: f'={sp.sstr(f_prime)}, g'={sp.sstr(g_prime)}"
                    })
                    
                    steps.append({
                        "type": "calculation",
                        "output": f"Apply Rule: ({sp.sstr(f_prime)})({sp.sstr(g)}) + ({sp.sstr(f)})({sp.sstr(g_prime)})"
                    })
                    
                    return {
                        "final_answer": sp.sstr(final),
                        "latex": sp.latex(final),
                        "problem_type": "Differentiation",
                        "steps": steps
                    }

            # ---- Chain Rule Check ----
            if hasattr(expr, 'args') and expr.args:
                inner = expr.args[0]
                if inner != var and not inner.is_Number:
                    u = inner
                    u_prime = sp.diff(u, var)
                    outer_prime = sp.diff(expr, u).subs(u, inner)
                    
                    steps.append({
                        "type": "identification",
                        "output": f"Identify Chain Rule: Inner function u = {sp.sstr(u)}",
                        "hint": "Formula: f'(g(x)) * g'(x)"
                    })
                    
                    steps.append({
                        "type": "derivation",
                        "output": f"Differentiate Inner: u' = {sp.sstr(u_prime)}"
                    })

                    steps.append({
                        "type": "derivation",
                        "output": f"Differentiate Outer: f'(u) = {sp.sstr(outer_prime)}"
                    })
                    
                    steps.append({
                        "type": "calculation",
                        "output": f"Multiply: ({sp.sstr(outer_prime)}) * ({sp.sstr(u_prime)})"
                    })

                    return {
                        "final_answer": sp.sstr(final),
                        "latex": sp.latex(final),
                        "problem_type": "Differentiation",
                        "steps": steps
                    }

        except Exception:
            # Fallback if specific detection fails
            pass

        # ---- Generic Fallback ----
        steps.append({
            "type": "standard_rule",
            "output": f"Differentiate using standard power rules: d/dx({sp.sstr(expr)})",
            "hint": "Power Rule: d/dx(x^n) = n*x^(n-1)"
        })
        
        return {
            "final_answer": sp.sstr(final),
            "latex": sp.latex(final),
            "problem_type": "Differentiation",
            "steps": steps
        }

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _infer_variable(self, expr_str: str):
        symbols = re.findall(r"[a-zA-Z]", expr_str)
        return sp.Symbol(symbols[0]) if symbols else sp.Symbol("x")