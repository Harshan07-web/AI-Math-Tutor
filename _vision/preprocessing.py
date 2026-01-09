import cv2
import numpy as np
from PIL import Image, ImageEnhance

class Preprocessor:

    @staticmethod
    def clean(image: Image.Image) -> Image.Image:
        """
        Best preprocessing for Math OCR (pix2tex)
        Returns PIL Image
        """

        if not isinstance(image, Image.Image):
            raise TypeError("Input must be PIL.Image")

        # Convert PIL → OpenCV
        img = np.array(image.convert("RGB"))

        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

<<<<<<< HEAD
    @staticmethod
    def preprocess(img: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Full preprocessing pipeline: read → grayscale → enhance → denoise → threshold."""
        img = Preprocessor.read_image(img)
        img = Preprocessor.enhance_contrast(img)
        img = Preprocessor.to_grayscale(img)
        img = Preprocessor.denoise(img)
        img = Preprocessor.threshold(img)
        return img

=======
        # Adaptive Threshold
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )

        # Morphological cleaning
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Convert back to PIL
        pil_img = Image.fromarray(cleaned)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(2.0)

        return pil_img
>>>>>>> d650762247c0519fda0bd6231f11f821ed3c6595
