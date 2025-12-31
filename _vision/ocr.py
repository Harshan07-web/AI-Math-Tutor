from pix2tex.cli import LatexOCR
from PIL import Image
from .preprocessing import Preprocessor


class OCRProcessor:

    def __init__(self, use_preprocessing=True):
        self.use_preprocessing = use_preprocessing
        self.model = LatexOCR()  # pix2tex auto-detects device

    def image_to_latex(self, image: Image.Image) -> str:
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be PIL.Image")

        if self.use_preprocessing:
            image = Preprocessor.clean(image)

        latex = self.model(image)

        # Small cleanup (optional)
        latex = latex.replace("~~~~", " ")

        return latex
