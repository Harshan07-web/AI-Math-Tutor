import sys
import os
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _vision.ocr import OCRProcessor

ocr = OCRProcessor()
image = np.array(Image.open("tests/sample.jpg").convert("RGB"))
latex_output = ocr.image_to_latex(image)
print("LaTeX Output:", latex_output)
