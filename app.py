import os
import sys
import tempfile
from PIL import Image
import cv2
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from app.core.engine import get_ocr_engine
from app.exporters.exporter import ResultExporters

def process_document(image_input, lang, deskew, enhance, binarize):
    if image_input is None:
        return None, "Please upload an image first.", None, None

    engine = get_ocr_engine(lang=lang, use_gpu=False)
    
    # Run OCR Pipeline
    res = engine.extract_from_image(image_input, deskew=deskew, enhance=enhance, binarize=binarize)
    
    # Draw interactive bounding boxes on the image
    annotated_img = np.array(image_input)
    if len(annotated_img.shape) == 2:
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_GRAY2RGB)
    elif annotated_img.shape[2] == 4:
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_RGBA2RGB)

    for line in res.get("lines", []):
        x, y, w, h = [int(v) for v in line["bbox"]]
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (99, 102, 241), 2)
        cv2.putText(
            annotated_img, 
            f"{int(line['confidence']*100)}%", 
            (x, max(15, y - 5)), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.4, 
            (56, 189, 248), 
            1
        )

    # Prepare export files
    temp_dir = tempfile.mkdtemp()
    json_path = os.path.join(temp_dir, "ocr_result.json")
    txt_path = os.path.join(temp_dir, "extracted_text.txt")
    
    ResultExporters.to_json_file(res, json_path)
    ResultExporters.to_txt_file(res, txt_path)
    
    return annotated_img, res.get("raw_text", ""), json_path, txt_path

with gr.Blocks(title="AirDoc Studio") as demo:
    gr.Markdown(
        """
        # 📄 AirDoc Studio
        ### 🔒 100% Offline & Private AI Document Extraction Studio (Powered by PaddleOCR PP-OCRv4)
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="numpy", label="Upload Scanned Document or Image")
            
            with gr.Accordion("⚙️ Preprocessing & Engine Options", open=True):
                lang_choice = gr.Dropdown(
                    choices=["en", "ch", "french", "german", "korean", "japan", "es"],
                    value="en",
                    label="Language"
                )
                deskew_toggle = gr.Checkbox(value=True, label="Auto-Deskew (Rotate)")
                enhance_toggle = gr.Checkbox(value=True, label="Contrast Boost (CLAHE)")
                binarize_toggle = gr.Checkbox(value=False, label="Adaptive Binarization")
            
            run_btn = gr.Button("🚀 Extract Text (PP-OCRv4)", variant="primary", size="lg")

        with gr.Column(scale=2):
            output_image = gr.Image(label="Annotated Document with Bounding Boxes")
            output_text = gr.Textbox(label="Extracted Text", lines=8, show_copy_button=True)
            
            with gr.Row():
                json_download = gr.File(label="Download JSON")
                txt_download = gr.File(label="Download TXT")

    run_btn.click(
        fn=process_document,
        inputs=[input_image, lang_choice, deskew_toggle, enhance_toggle, binarize_toggle],
        outputs=[output_image, output_text, json_download, txt_download],
        api_name=False
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
