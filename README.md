---
title: AirDoc Studio
emoji: 📄
colorFrom: indigo
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

# AirDoc Studio

Air-Gapped, 100% Offline, High-Performance OCR & Document Intelligence Studio powered by PaddleOCR (PP-OCRv4), FastAPI, Vite, React, and Tailwind CSS.

## Key Highlights

- **100% Offline & Air-Gapped**: Zero cloud telemetry, zero external network dependency during inference. Your sensitive documents stay strictly local.
- **Ultra-Fast Vite + React Frontend**: Instant load times with hardware-accelerated HTML5 Canvas (60fps smooth pan & zoom, bounding-box hover/selection, confidence overlays).
- **PaddleOCR Deep Learning Core**: Powered by state-of-the-art PP-OCRv4 detection and recognition.
- **Computer Vision Preprocessing Pipeline**:
  - Auto-Deskewing (Hough & MinAreaRect angle rectification)
  - Contrast Enhancement (CLAHE on luminance channel)
  - Adaptive Binarization (Otsu & Gaussian thresholding)
- **Multi-Page PDF & Image Support**: Direct ingestion of PDF, PNG, JPG, WEBP, and TIFF scans.
- **Export Hub**:
  - Searchable PDF (Invisible selectable OCR text layer injected over original scan)
  - Structured JSON (Bounding boxes [x, y, w, h], line geometry, and confidence metrics)
  - Formatted Plain Text (TXT)

## Quick Start Guide

### Option 1: One-Click Launcher (Windows)
Double-click start.bat in the root folder.

### Option 2: Manual Setup

#### 1. Clone the repository
`ash
git clone https://github.com/Prateek-Dhar-Dwivedi/AirDoc-Studio.git
cd AirDoc-Studio
`

#### 2. Install Backend Dependencies
`ash
python -m pip install -r requirements.txt
`

#### 3. Run FastAPI Backend
`ash
python run_server.py
`
API & OpenAPI Interactive Documentation: http://127.0.0.1:8000/docs

#### 4. Run Vite Frontend
`ash
cd frontend
npm install
npm run dev
`
Frontend Web Studio: http://localhost:5173

## License
MIT
