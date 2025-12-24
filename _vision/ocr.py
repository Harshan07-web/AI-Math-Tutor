import cv2
import numpy as np
from PIL import Image
import torch

from pix2tex.cli import model_from_pretrained  # correct import
from .preprocessing import Preprocessor

class OCRProcessor:
    """OCR Processor using Pix2Tex + OpenCV preprocessing."""

    def __init__(self, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Load the pretrained Pix2Tex model
        self.model = model_from_pretrained("im2latex")  # or any available checkpoint
        self.model.to(self.device)
        self.model.eval()

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply OpenCV preprocessing to make the image Pix2Tex-ready."""
        img = Preprocessor.clean_for_ocr(image)
        return img

    def image_to_latex(self, image: np.ndarray) -> str:
        """
        Convert an input image (numpy array) to LaTeX string.
        """
        preprocessed = self.preprocess_image(image)
        pil_img = Image.fromarray(preprocessed)
        latex_str = self.model.predict(pil_img)  # Pix2Tex inference
        return latex_str
