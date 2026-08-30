import cv2
import numpy as np
from PIL import Image
from typing import Tuple

class ImagePreprocessor:
    @staticmethod
    def read_image(image_path: str) -> np.ndarray:
        # Supports unicode paths on Windows safely
        img_array = np.fromfile(image_path, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Unable to read image at {image_path}")
        return img

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Detect text angle using Hough Lines / MinAreaRect and rotate back."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 50:
            return image

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # If angle is negligible, skip
        if abs(angle) < 0.5 or abs(angle) > 45:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) on luminance channel."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    @staticmethod
    def denoise_and_binarize(image: np.ndarray) -> np.ndarray:
        """Adaptive binarization for tough / dark document scans."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        binarized = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
        )
        return cv2.cvtColor(binarized, cv2.COLOR_GRAY2BGR)

    @classmethod
    def process_pipeline(cls, image_path: str, deskew: bool = True, enhance: bool = True, binarize: bool = False) -> np.ndarray:
        img = cls.read_image(image_path)
        if deskew:
            img = cls.deskew(img)
        if enhance and not binarize:
            img = cls.enhance_contrast(img)
        if binarize:
            img = cls.denoise_and_binarize(img)
        return img
