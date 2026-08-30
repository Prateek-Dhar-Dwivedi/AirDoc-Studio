import os
import sys
import uvicorn
import gradio as gr

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.api.routes import app as fastapi_app

# Create a clean backend landing page for Hugging Face
with gr.Blocks(title="AirDoc Studio Backend") as demo:
    gr.Markdown(
        """
        # 📄 AirDoc Studio Backend Service
        ### 🔒 100% Private AI Document Extraction API (PP-OCRv4)
        - The frontend is deployed on Vercel.
        - The API endpoints are running successfully in the background.
        """
    )

# Mount our FastAPI app (with the OCR endpoints) on the Gradio app
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)
