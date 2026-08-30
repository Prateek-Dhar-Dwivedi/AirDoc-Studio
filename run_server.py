import uvicorn
from backend.api.routes import app
from backend.core.config import settings

if __name__ == "__main__":
    print(f"Starting PabbleOCR server at http://{settings.host}:{settings.port}")
    uvicorn.run("backend.api.routes:app", host=settings.host, port=settings.port, reload=True)
