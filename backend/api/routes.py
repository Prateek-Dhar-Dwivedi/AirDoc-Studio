import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from ..core.config import settings
from ..core.engine import get_ocr_engine
from ..exporters.exporter import ResultExporters

app = FastAPI(
    title="AirDoc Studio API",
    description="High performance, air-gapped, offline OCR and layout extraction server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_CACHE = {}

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "AirDoc Studio", "offline_ready": True, "gpu_enabled": settings.use_gpu}

@app.post("/api/ocr")
async def process_ocr(
    file: UploadFile = File(...),
    lang: str = Form("en"),
    use_gpu: bool = Form(False),
    deskew: bool = Form(True),
    enhance: bool = Form(True),
    binarize: bool = Form(False)
):
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        task_id = str(uuid.uuid4())
        save_name = f"{task_id}_{file.filename}"
        save_path = os.path.join(settings.uploads_dir, save_name)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        engine = get_ocr_engine(lang=lang, use_gpu=use_gpu)

        if file_ext in [".pdf"]:
            pages_result = engine.extract_from_pdf(save_path, deskew=deskew, enhance=enhance)
            data = {
                "task_id": task_id,
                "file_name": file.filename,
                "file_type": "pdf",
                "file_url": f"/api/files/{save_name}",
                "pages": pages_result,
                "total_pages": len(pages_result)
            }
        else:
            result = engine.extract_from_image(save_path, deskew=deskew, enhance=enhance, binarize=binarize)
            data = {
                "task_id": task_id,
                "file_name": file.filename,
                "file_type": "image",
                "file_url": f"/api/files/{save_name}",
                **result
            }

        RESULTS_CACHE[task_id] = {
            "save_path": save_path,
            "data": data
        }

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(settings.uploads_dir, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(settings.outputs_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/api/export/{task_id}/{export_type}")
async def export_result(task_id: str, export_type: str):
    if task_id not in RESULTS_CACHE:
        raise HTTPException(status_code=404, detail="Task result expired or not found")

    item = RESULTS_CACHE[task_id]
    data = item["data"]
    orig_path = item["save_path"]

    out_name = f"export_{task_id}.{export_type}"
    out_path = os.path.join(settings.outputs_dir, out_name)

    if export_type == "json":
        ResultExporters.to_json_file(data, out_path)
    elif export_type == "txt":
        ResultExporters.to_txt_file(data, out_path)
    elif export_type == "pdf":
        if data.get("file_type") == "image":
            ResultExporters.to_searchable_pdf(orig_path, data, out_path)
        else:
            return FileResponse(orig_path, filename=f"searchable_{data.get('file_name', 'doc.pdf')}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format {export_type}")

    return FileResponse(out_path, filename=f"airdoc_result_{task_id[:8]}.{export_type}")

# Mount static frontend build if present (for Hugging Face & Docker production)
dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
