import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Union


class Preprocessor:
    """Image preprocessing for OCR using OpenCV and PIL."""

    @staticmethod
    def read_image(source: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Read image from file path, numpy array, or PIL Image."""
        if isinstance(source, np.ndarray):
            img = source.copy()
        elif isinstance(source, Image.Image):
            img = np.array(source.convert("RGB"))[:, :, ::-1]  # RGB to BGR
        else:
            img = cv2.imread(source)
            if img is None:
                raise FileNotFoundError(f"Cannot read image: {source}")
        return img

    @staticmethod
    def to_grayscale(img: np.ndarray) -> np.ndarray:
        if img.ndim == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img.copy()

    @staticmethod
    def enhance_contrast(img: np.ndarray, factor: float = 1.5) -> np.ndarray:
        pil = Image.fromarray(img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil = ImageEnhance.Contrast(pil).enhance(factor)
        img = np.array(pil)
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    @staticmethod
    def denoise(img: np.ndarray, ksize: int = 3) -> np.ndarray:
        return cv2.medianBlur(img, ksize)

    @staticmethod
    def threshold(img: np.ndarray) -> np.ndarray:
        gray = Preprocessor.to_grayscale(img)
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 25, 10)

    @staticmethod
    def preprocess(img: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Full preprocessing pipeline: read → grayscale → enhance → denoise → threshold."""
        img = Preprocessor.read_image(img)
        img = Preprocessor.enhance_contrast(img)
        img = Preprocessor.to_grayscale(img)
        img = Preprocessor.denoise(img)
        img = Preprocessor.threshold(img)
        return img

