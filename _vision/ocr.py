from pix2tex.cli import LatexOCR
from PIL import Image
from .preprocessing import Preprocessor


class OCRProcessor:
    def __init__(self, use_preprocessing: bool = False, device: str | None = None, *args, **kwargs):
        """
        OCR Processor using Pix2Tex LatexOCR.
        """
        self.use_preprocessing = use_preprocessing
        try:
            self.model = LatexOCR(device=device, *args, **kwargs)
        except TypeError:
            self.model = LatexOCR(*args, **kwargs)

    def _clean_latex(self, latex: str) -> str:
        """
        Clean common OCR artifacts from LaTeX output.
        """
        # Remove noisy tokens
        artifacts = [
            "::", "*", "\\vdots", "\\scriptstyle", "\\scriptsize",
            "\\!", "\\displaystyle"
        ]
        for artifact in artifacts:
            latex = latex.replace(artifact, "")

        # Flatten arrays
        latex = latex.replace("\\begin{array}{c}", "")
        latex = latex.replace("\\end{array}", "")

        # Fix \left...\right. without closing
        latex = latex.replace("\\left(", "(").replace("\\right.", ")")

        # Remove filler (~ or long commas)
        latex = latex.replace("~", "").replace(",","")

        # Balance braces
        while "{{" in latex:
            latex = latex.replace("{{", "{")
        while "}}" in latex:
            latex = latex.replace("}}", "}")

        # Trim trailing unmatched braces/parentheses
        open_braces = latex.count("{")
        close_braces = latex.count("}")
        if close_braces > open_braces:
            latex = latex.rstrip("}")
        elif open_braces > close_braces:
            latex += "}"

        open_paren = latex.count("(")
        close_paren = latex.count(")")
        if close_paren > open_paren:
            latex = latex.rstrip(")")
        elif open_paren > close_paren:
            latex += ")"

        return latex.strip()
    

    

    def image_to_latex(self, image: Image.Image) -> str:
        """
        Convert a PIL.Image to LaTeX using Pix2Tex.
        """
        if self.use_preprocessing:
            image = Preprocessor.clean_for_ocr(image)

        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL.Image")

        try:
            if hasattr(self.model, "predict"):
                latex = self.model.predict(image)
            elif hasattr(self.model, "to_latex"):
                latex = self.model.to_latex(image)
            else:
                latex = self.model(image)
        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}")

        return self._clean_latex(latex)


