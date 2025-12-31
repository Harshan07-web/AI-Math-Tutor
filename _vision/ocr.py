from pix2tex.cli import LatexOCR
from PIL import Image
from .preprocessing import Preprocessor

class OCRProcessor:

    def __init__(self, use_preprocessing=True):
        self.use_preprocessing = use_preprocessing
        self.model = LatexOCR()

<<<<<<< HEAD
    def extract_text(self, image: Image.Image) -> str:
=======
    def image_to_latex(self, image: Image.Image) -> str:
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be PIL.Image")
>>>>>>> c69c82bd0b9df88c70ab8d8e6b2e5158a370bf98

        if self.use_preprocessing:
            image = Preprocessor.clean(image)

        if not isinstance(image, Image.Image):
            raise TypeError("Input must be PIL.Image")

        latex = self.model(image)
        return latex.strip()
