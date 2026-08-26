import uvicorn
from app.api.routes import app
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting PabbleOCR server at http://{settings.host}:{settings.port}")
    uvicorn.run("app.api.routes:app", host=settings.host, port=settings.port, reload=True)
