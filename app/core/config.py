import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

MODELS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

class Settings(BaseModel):
    app_name: str = "AirDoc Studio"
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8000
    use_gpu: bool = False
    lang: str = "en"
    models_dir: str = str(MODELS_DIR)
    uploads_dir: str = str(UPLOADS_DIR)
    outputs_dir: str = str(OUTPUTS_DIR)

settings = Settings()
