import os
import pymupdf as fitz
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from paddleocr import PaddleOCR
from .config import settings
from .preprocessor import ImagePreprocessor

class OCREngine:
    _instance = None
    
    def __init__(self, lang: str = "en", use_gpu: bool = False):
        self.lang = lang
        self.use_gpu = use_gpu
        self._init_ocr()

    def _init_ocr(self):
        """Initialize PaddleOCR PP-OCRv4."""
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=self.lang,
            use_gpu=self.use_gpu,
            show_log=False
        )

    def extract_from_image(
        self, 
        image_input: Any, 
        deskew: bool = True, 
        enhance: bool = True, 
        binarize: bool = False
    ) -> Dict[str, Any]:
        """
        Process single image array or path.
        Returns detailed bounding boxes, texts, confidence, and dimensions.
        """
        if isinstance(image_input, str):
            img = ImagePreprocessor.process_pipeline(
                image_input, deskew=deskew, enhance=enhance, binarize=binarize
            )
        else:
            img = image_input

        h, w = img.shape[:2]
        raw_result = self.ocr.ocr(img, cls=True)

        lines = []
        full_text_list = []

        if raw_result and isinstance(raw_result, list) and len(raw_result) > 0 and raw_result[0] is not None:
            for item in raw_result[0]:
                bbox = item[0]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                text, score = item[1]
                
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                lines.append({
                    "text": text,
                    "confidence": round(float(score), 4),
                    "polygon": bbox,
                    "bbox": [round(min_x, 1), round(min_y, 1), round(max_x - min_x, 1), round(max_y - min_y, 1)],
                    "center": [round((min_x + max_x) / 2, 1), round((min_y + max_y) / 2, 1)]
                })
                full_text_list.append(text)

        return {
            "dimensions": {"width": w, "height": h},
            "lines_count": len(lines),
            "lines": lines,
            "raw_text": "\n".join(full_text_list)
        }

    def extract_from_pdf(
        self, 
        pdf_path: str, 
        dpi: int = 200, 
        deskew: bool = True, 
        enhance: bool = False
    ) -> List[Dict[str, Any]]:
        doc = fitz.open(pdf_path)
        pages_result = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            page_ocr = self.extract_from_image(img, deskew=deskew, enhance=enhance)
            page_ocr["page"] = page_num + 1
            pages_result.append(page_ocr)

        doc.close()
        return pages_result

_ocr_instance: Optional[OCREngine] = None

def get_ocr_engine(lang: str = "en", use_gpu: bool = False) -> OCREngine:
    global _ocr_instance
    if _ocr_instance is None or _ocr_instance.lang != lang or _ocr_instance.use_gpu != use_gpu:
        _ocr_instance = OCREngine(lang=lang, use_gpu=use_gpu)
    return _ocr_instance
