import os
import json
import pandas as pd
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

class ResultExporters:
    @staticmethod
    def to_json_file(data: Dict[str, Any], output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_path

    @staticmethod
    def to_txt_file(data: Dict[str, Any], output_path: str):
        text = data.get("raw_text", "")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path

    @staticmethod
    def to_searchable_pdf(image_path: str, ocr_data: Dict[str, Any], output_pdf_path: str):
        """Creates a PDF with the original image and an invisible selectable text layer."""
        img = Image.open(image_path)
        img_w, img_h = img.size

        c = canvas.Canvas(output_pdf_path, pagesize=(img_w, img_h))
        
        # Draw background image
        c.drawImage(image_path, 0, 0, width=img_w, height=img_h)

        # Draw invisible text over image
        # ReportLab coordinate system has (0,0) at bottom-left, while image coords are top-left
        c.setFillColorRGB(0, 0, 0, alpha=0.0) # Transparent

        for line in ocr_data.get("lines", []):
            text = line.get("text", "")
            bbox = line.get("bbox", [0, 0, 10, 10]) # x, y, w, h
            x, y, w, h = bbox
            
            # Convert y coordinate to PDF space
            pdf_y = img_h - (y + h)
            
            # Approximate font size
            font_size = max(6, int(h * 0.85))
            c.setFont("Helvetica", font_size)
            c.drawString(x, pdf_y + 2, text)

        c.save()
        return output_pdf_path

    @staticmethod
    def to_excel_table(rows: List[List[str]], output_path: str):
        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False, header=False)
        return output_path

    @staticmethod
    def to_csv_table(rows: List[List[str]], output_path: str):
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, header=False, encoding="utf-8-sig")
        return output_path
