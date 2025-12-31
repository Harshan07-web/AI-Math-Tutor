from sympy.parsing.latex import parse_latex
from sympy import Symbol
import re

class LatexToSympyConverter:

    @staticmethod
    def clean_latex(latex: str) -> str:
        """
        Clean OCR LaTeX for SymPy compatibility
        """

        replacements = {
            r"\left": "",
            r"\right": "",
            r"\,": "",
            r"\!": "",
            r"\cdot": "*",
            r"d x": "dx",
            r"d y": "dy",
        }

        for k, v in replacements.items():
            latex = latex.replace(k, v)

        latex = latex.strip()
        return latex

    @staticmethod
    def to_sympy(latex: str):
        """
        Convert LaTeX → SymPy expression
        """
        try:
            cleaned = LatexToSympyConverter.clean_latex(latex)
            return parse_latex(cleaned)
        except Exception as e:
            raise ValueError(f"LaTeX → SymPy failed: {e}")
