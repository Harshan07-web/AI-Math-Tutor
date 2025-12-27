import cv2
import numpy as np
from PIL import Image


class Preprocessor:
    @staticmethod
    def _deskew(img: np.ndarray) -> np.ndarray:
        coords = np.column_stack(np.where(img > 0))
        if coords.shape[0] < 10:
            return img
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        (h, w) = img.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=0)

    @staticmethod
    def clean_for_ocr(image: Image.Image, debug: bool = False) -> Image.Image:
        if image.mode != "RGB":
            image = image.convert("RGB")

        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if np.count_nonzero(bw) < 10:
            return image

        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        clean = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel_open, iterations=1)
        clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel_close, iterations=1)
        clean = cv2.medianBlur(clean, 3)

        clean = Preprocessor._deskew(clean)

        h, w = clean.shape
        pad = max(10, int(max(h, w) * 0.03))
        clean = cv2.copyMakeBorder(clean, pad, pad, pad, pad,
                                   cv2.BORDER_CONSTANT, value=0)

        h, w = clean.shape
        target_h, max_w = 512, 2048
        scale = min(target_h / h, max_w / w)
        new_w, new_h = int(w * scale), int(h * scale)
        clean = cv2.resize(clean, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        clean_rgb = cv2.cvtColor(clean, cv2.COLOR_GRAY2RGB)
        result = Image.fromarray(clean_rgb)

        if debug:
            result.show()

        return result