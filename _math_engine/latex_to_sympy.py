from sympy.parsing.latex import parse_latex
from sympy import sympify, Eq
import re

class LatexToSympyConverter:
    @staticmethod
    def clean_latex(latex: str) -> str:
        if not latex: return ""
        # Basic cleanup
        latex = re.sub(r"\\left|\\right|\\displaystyle", "", latex)
        latex = latex.replace("−", "-").replace("×", "*").replace("÷", "/")
        # Implicit mult: 2x -> 2*x
        latex = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", latex)
        return latex.strip()

    @staticmethod
    def _safe_parse(text: str):
        """Try LaTeX parser, failover to SymPy string parser"""
        try:
            # parse_latex is strict. If it fails...
            return parse_latex(text)
        except Exception:
            # ...sympify is flexible (handles '2*x+5' well)
            return sympify(text)

    @staticmethod
    def to_sympy(latex: str):
        cleaned = LatexToSympyConverter.clean_latex(latex)
        
        # ✅ THE CRITICAL CHECK
        if "=" in cleaned:
            parts = cleaned.split("=", 1)
            lhs = LatexToSympyConverter._safe_parse(parts[0].strip())
            rhs = LatexToSympyConverter._safe_parse(parts[1].strip())
            return Eq(lhs, rhs)
            
        return LatexToSympyConverter._safe_parse(cleaned)