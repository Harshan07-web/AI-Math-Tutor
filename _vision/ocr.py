import re
from typing import Union, Optional, Dict, Any
from PIL import Image
import numpy as np
import pytesseract

from _math_engine import MathSolver, StepExtractor, StepNormalizer
from .preprocessing import Preprocessor


class OCRProcessor:
    """Convert images to math problem text via OCR and run the math engine."""

    def __init__(self, tesseract_lang: str = "eng", tesseract_config: str = "--psm 6"):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.tesseract_lang = tesseract_lang
        self.tesseract_config = tesseract_config

    def _clean_ocr_text(self, text: str) -> str:
        text = text.replace("×", "*").replace("−", "-").replace("—", "-")
        text = text.replace("•", "*").replace("÷", "/")
        # keep digits, letters, common math symbols and simple function names
        text = re.sub(r"[^0-9A-Za-z=+\-*/^().,xXyY\s\\sqrt\\pi]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def image_to_text(self, source: Union[str, bytes, Image.Image, np.ndarray]) -> str:
        img = Preprocessor.clean_for_ocr(source)
        pil = Image.fromarray(img) if isinstance(img, np.ndarray) else img
        raw = pytesseract.image_to_string(pil, lang=self.tesseract_lang, config=self.tesseract_config)
        return self._clean_ocr_text(raw)

    def extract_problem(self, text: str) -> Optional[str]:
        # prefer explicit equation lines
        eq = re.search(r"([^\n=]+\=[^\n=]+)", text)
        if eq:
            return eq.group(1).strip()
        # otherwise return first line that looks mathematical
        for line in (l.strip() for l in text.splitlines() if l.strip()):
            if re.search(r"[0-9xyXYZ()=+\-*/^]", line):
                return line
        return None

    def solve_image(self, source: Union[str, bytes, Image.Image, np.ndarray]) -> Dict[str, Any]:
        text = self.image_to_text(source)
        problem = self.extract_problem(text)
        if not problem:
            raise ValueError("No math problem detected in image OCR output.")
        result = self.solver.solve(problem)
        raw_steps = self.extractor.extract_steps(result.get("solution", ""), result.get("type", "equation"))
        norm_steps = self.normalizer.normalize_steps(raw_steps)
        return {
            "problem": problem,
            "ocr_text": text,
            "solution": result.get("solution"),
            "type": result.get("type"),
            "raw_steps": raw_steps,
            "normalized_steps": norm_steps,
        }