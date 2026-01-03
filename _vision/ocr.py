import re
from pix2tex.cli import LatexOCR
from PIL import Image
from .preprocessing import Preprocessor

<<<<<<< HEAD

class OCRProcessor:
    """
    Image → LaTeX OCR processor with cleanup
    """

    def __init__(self, use_preprocessing: bool = True):
        self.use_preprocessing = use_preprocessing
        self.model = LatexOCR()

    # --------------------------------------------------
    # MAIN OCR METHOD
    # --------------------------------------------------
=======
class OCRProcessor:
    def __init__(self, use_preprocessing=True):
        self.use_preprocessing = use_preprocessing
        self.model = LatexOCR()

>>>>>>> 4a199d77ee220a94d59fd8e958a07d76fdaf495d
    def image_to_latex(self, image: Image.Image) -> str:
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be PIL.Image")

        # 🧹 Preprocessing
        if self.use_preprocessing:
            image = Preprocessor.clean(image)

<<<<<<< HEAD
        # 🔍 OCR
        try:
            latex = self.model(image)
        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}")

        if not latex or not isinstance(latex, str):
            return ""

        # 🧠 Normalize OCR noise
        latex = self.normalize_ocr_latex(latex)

        return latex

    # --------------------------------------------------
    # OCR LATEX CLEANER
    # --------------------------------------------------
    @staticmethod
    def normalize_ocr_latex(latex: str) -> str:
        """
        Fix common OCR hallucinations so SymPy can parse
        """

        rules = [
            # ❌ Garbage symbols
            (r"\\vdash", ""),
            (r"\\angle", ""),
            (r"\\Omega", "0"),
            (r"\\mid", ""),
            (r"\|+", ""),

            # 🔁 Derivative fixes
            (r"\\mathcal\s*\{D\}", r"\\frac{d}{dx}"),
            (r"\\partial", r"\\frac{d}{dx}"),

            # 📐 Formatting noise
            (r"\\left|\\right", ""),
            (r"\\displaystyle", ""),

            # 🧹 Whitespace
            (r"\s+", " "),
        ]

        for pattern, repl in rules:
            latex = re.sub(pattern, repl, latex)

=======
        latex = self.model(image)
>>>>>>> 4a199d77ee220a94d59fd8e958a07d76fdaf495d
        return latex.strip()
