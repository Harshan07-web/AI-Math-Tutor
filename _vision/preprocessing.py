import io
from typing import Union, Optional
from PIL import Image, ImageEnhance
import numpy as np
import cv2


class Preprocessor:
    """Utilities to read and preprocess images for OCR."""

    @staticmethod
    def read_image(source: Union[str, bytes, Image.Image, np.ndarray]) -> np.ndarray:
        if isinstance(source, np.ndarray):
            img = source.copy()
        elif isinstance(source, bytes):
            img = Image.open(io.BytesIO(source)).convert("RGB")
            img = np.array(img)[:, :, ::-1]  # RGB -> BGR
        elif isinstance(source, Image.Image):
            img = np.array(source.convert("RGB"))[:, :, ::-1]
        else:
            img = cv2.imread(str(source))
            if img is None:
                raise FileNotFoundError(f"Could not read image: {source}")
        return img

    @staticmethod
    def to_grayscale(img: np.ndarray) -> np.ndarray:
        if img.ndim == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img.copy()

    @staticmethod
    def enhance_contrast(img: np.ndarray, factor: float = 1.5) -> np.ndarray:
        # Accept grayscale or color
        if img.ndim == 2:
            pil = Image.fromarray(img)
            pil = ImageEnhance.Contrast(pil).enhance(factor)
            return np.array(pil)
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil = ImageEnhance.Contrast(pil).enhance(factor)
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    @staticmethod
    def denoise(img: np.ndarray, ksize: int = 3) -> np.ndarray:
        # Prefer median blur for simple noise; if larger images use fastNlMeansDenoising
        if img.ndim == 2:
            return cv2.medianBlur(img, ksize)
        return cv2.medianBlur(img, ksize)

    @staticmethod
    def adaptive_threshold(img: np.ndarray, block_size: int = 25, c: int = 10) -> np.ndarray:
        gray = Preprocessor.to_grayscale(img)
        if gray.dtype != np.uint8:
            gray = (255 * (gray / np.max(gray))).astype(np.uint8)
        # use Gaussian adaptive threshold; ensure block_size is odd and >=3
        bs = block_size if block_size % 2 == 1 and block_size >= 3 else 25
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, bs, c)

    @staticmethod
    def deskew(img: np.ndarray) -> np.ndarray:
        # Expect binary or grayscale image; produce deskewed binary image
        gray = Preprocessor.to_grayscale(img)
        # Binarize for angle detection
        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(bw == 0))  # text is dark -> zeros
        if coords.size == 0:
            return img
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = gray.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        # Return binary image after rotation
        _, rotated_bw = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return rotated_bw

    @staticmethod
    def resize_to_max(img: np.ndarray, max_dim: int = 2000) -> np.ndarray:
        h, w = img.shape[:2]
        scale = min(1.0, max_dim / max(h, w))
        if scale == 1.0:
            return img
        new_size = (int(w * scale), int(h * scale))
        return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

    @staticmethod
    def clean_for_ocr(source: Union[str, bytes, Image.Image, np.ndarray],
                      enhance: bool = True,
                      denoise_ksize: int = 3,
                      max_dim: Optional[int] = 2000) -> np.ndarray:
        img = Preprocessor.read_image(source)
        if max_dim:
            img = Preprocessor.resize_to_max(img, max_dim)
        if enhance:
            img = Preprocessor.enhance_contrast(img, factor=1.4)
        gray = Preprocessor.to_grayscale(img)
        den = Preprocessor.denoise(gray, ksize=denoise_ksize)
        th = Preprocessor.adaptive_threshold(den, block_size=25, c=10)
        deskewed = Preprocessor.deskew(th)
        # Ensure uint8 binary image returned
        return deskewed.astype(np.uint8)