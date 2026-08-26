@echo off
echo ========================================================
echo   Starting PabbleOCR Offline Studio
echo ========================================================

start cmd /k "python run_server.py"
start cmd /k "cd frontend && npm run dev"

echo.
echo FastAPI API is running at: http://127.0.0.1:8000/docs
echo Vite Frontend is running at: http://localhost:5173
echo.
