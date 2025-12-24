import re
from typing import Union, Optional, Dict, Any
from PIL import Image
import numpy as np
import cv2
import torch
import torchvision.transforms as transforms
from torch import nn

from _math_engine import MathSolver, StepExtractor, StepNormalizer
from .preprocessing import Preprocessor


class MathTextDetectionModel(nn.Module):
    """Simple CNN for math region detection in images."""
    
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(64, 2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class OCRProcessor:
    """Convert images to math problem text via PyTorch + preprocessing and run the math engine."""

    def __init__(self, tesseract_lang: str = "eng", device: str = "cpu", use_pytorch: bool = True):
        self.solver = MathSolver()
        self.extractor = StepExtractor()
        self.normalizer = StepNormalizer()
        self.tesseract_lang = tesseract_lang
        self.device = torch.device(device)
        self.use_pytorch = use_pytorch
        
        if use_pytorch:
            self.detection_model = MathTextDetectionModel().to(self.device)
            self.detection_model.eval()
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                    std=[0.229, 0.224, 0.225])
            ])

    def _clean_ocr_text(self, text: str) -> str:
        """Clean and normalize OCR output text."""
        text = text.replace("×", "*").replace("−", "-").replace("—", "-")
        text = text.replace("•", "*").replace("÷", "/")
        text = re.sub(r"[^0-9A-Za-z=+\-*/^().,xXyY\s\\sqrt\\pi]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def detect_math_regions(self, source: Union[str, bytes, Image.Image, np.ndarray]) -> Dict[str, Any]:
        """Use PyTorch model to detect math regions in image."""
        img = Preprocessor.read_image(source)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) if isinstance(img, np.ndarray) else img
        
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.detection_model(tensor)
            probs = torch.softmax(logits, dim=1)
            is_math = probs[0, 1].item()
        
        return {
            "is_math": is_math > 0.5,
            "confidence": float(is_math),
            "image": img
        }

    def extract_text_pytorch(self, img: np.ndarray) -> str:
        """Extract text using preprocessing + pytesseract."""
        try:
            import pytesseract
            pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            raw = pytesseract.image_to_string(pil, lang=self.tesseract_lang, config="--psm 6")
            return self._clean_ocr_text(raw)
        except ImportError:
            raise ImportError("pytesseract required; install via: pip install pytesseract")

    def extract_problem(self, text: str) -> Optional[str]:
        """Extract first math problem from OCR text."""
        eq = re.search(r"([^\n=]+\=[^\n=]+)", text)
        if eq:
            return eq.group(1).strip()
        for line in (l.strip() for l in text.splitlines() if l.strip()):
            if re.search(r"[0-9xyXYZ()=+\-*/^]", line):
                return line
        return None

    def solve_image(self, source: Union[str, bytes, Image.Image, np.ndarray]) -> Dict[str, Any]:
        """Detect math region, extract text, and solve."""
        detection = self.detect_math_regions(source)
        if not detection["is_math"]:
            raise ValueError(f"No math content detected (confidence: {detection['confidence']:.2f})")
        
        img = detection["image"]
        clean_img = Preprocessor.clean_for_ocr(img)
        text = self.extract_text_pytorch(clean_img)
        problem = self.extract_problem(text)
        
        if not problem:
            raise ValueError("No math problem detected in OCR output.")
        
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
            "math_confidence": detection["confidence"],
        }

    def load_model_weights(self, checkpoint_path: str) -> None:
        """Load pretrained detection model weights."""
        self.detection_model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.detection_model.eval()

    def save_model_weights(self, checkpoint_path: str) -> None:
        """Save detection model weights."""
        torch.save(self.detection_model.state_dict(), checkpoint_path)