from sympy.parsing.latex import parse_latex
import re


class LatexToSympyConverter:

    @staticmethod
    def clean_latex(latex: str) -> str:
        """
        Clean and normalize OCR-generated LaTeX
        so SymPy can understand it.
        """

        if not latex or not isinstance(latex, str):
            raise ValueError("Invalid LaTeX input")

        # -------------------------------
        # 1️⃣ Remove LaTeX formatting noise
        # -------------------------------
        latex = re.sub(r"\\left|\\right|\\displaystyle", "", latex)

        latex = re.sub(r"\\math[a-zA-Z]*\{([^}]*)\}", r"\1", latex)
        latex = re.sub(r"\\[,!;\s]+", "", latex)

        latex = re.sub(
            r"\\begin\{array\}.*?\\end\{array\}",
            "",
            latex,
            flags=re.DOTALL,
        )

        latex = re.sub(r"\\check\{.*?\}|\\hat\{.*?\}", "", latex)

        # -------------------------------
        # 2️⃣ Normalize OCR symbols
        # -------------------------------
        replacements = {
            "−": "-",
            "×": "*",
            "÷": "/",
            "∣": "|",
            "mid": "|",
        }

        for k, v in replacements.items():
            latex = latex.replace(k, v)

        # -------------------------------
        # 3️⃣ Fix absolute values
        # |x| → Abs(x)
        # -------------------------------
        latex = re.sub(r"\|(.+?)\|", r"Abs(\1)", latex)

        # -------------------------------
        # 4️⃣ Fix derivatives
        # D(x^2) → Derivative(x^2, x)
        # -------------------------------
        latex = re.sub(
            r"D\s*\((.+?)\)",
            r"Derivative(\1, x)",
            latex
        )

        # -------------------------------
        # 5️⃣ Fix differentials
        # -------------------------------
        latex = latex.replace("d x", "dx").replace("d y", "dy")

        # -------------------------------
        # 6️⃣ Implicit multiplication
        # 2x → 2*x , 3(x+1) → 3*(x+1)
        # -------------------------------
        latex = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", latex)
        latex = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", latex)
        latex = re.sub(r"(\))(\()", r"\1*\2", latex)

        return latex.strip()

    @staticmethod
    def to_sympy(latex: str):
        """
        Convert LaTeX → SymPy using real LaTeX grammar
        """
        try:
            cleaned = LatexToSympyConverter.clean_latex(latex)
            return parse_latex(cleaned)
        except Exception as e:
            raise ValueError(f"LaTeX → SymPy failed: {e}")
