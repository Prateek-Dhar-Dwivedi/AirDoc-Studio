import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Upload, FileText, Download, 
  ZoomIn, ZoomOut, RotateCw, 
  Sliders, Copy, Check, Eye, Cpu, ShieldCheck, Sparkles 
} from 'lucide-react';

interface OCRLine {
  text: string;
  confidence: number;
  bbox: [number, number, number, number];
  polygon: [[number, number], [number, number], [number, number], [number, number]];
}

interface OCRResult {
  task_id: string;
  file_name: string;
  file_type: 'image' | 'pdf';
  file_url: string;
  dimensions?: { width: number; height: number };
  lines?: OCRLine[];
  raw_text?: string;
  pages?: Array<{
    page: number;
    dimensions: { width: number; height: number };
    lines: OCRLine[];
    raw_text: string;
  }>;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OCRResult | null>(null);
  const [selectedLine, setSelectedLine] = useState<OCRLine | null>(null);
  const [copied, setCopied] = useState(false);
  
  // Settings
  const [lang, setLang] = useState('en');
  const [deskew, setDeskew] = useState(true);
  const [enhance, setEnhance] = useState(true);
  const [binarize, setBinarize] = useState(false);
  const [useGpu, setUseGpu] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [showBBoxes, setShowBBoxes] = useState(true);
  const [activePage, setActivePage] = useState(1);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setResult(null);
      setSelectedLine(null);
      setPreviewUrl(URL.createObjectURL(selected));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      setResult(null);
      setSelectedLine(null);
      setPreviewUrl(URL.createObjectURL(selected));
    }
  };

  const runOCR = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang', lang);
    formData.append('use_gpu', String(useGpu));
    formData.append('deskew', String(deskew));
    formData.append('enhance', String(enhance));
    formData.append('binarize', String(binarize));

    try {
      const resp = await axios.post<OCRResult>('/api/ocr', formData);
      setResult(resp.data);
      if (resp.data.file_type === 'pdf') {
        setActivePage(1);
      }
    } catch (err: any) {
      alert('OCR Failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const currentLines = result?.file_type === 'pdf' 
    ? (result.pages?.find(p => p.page === activePage)?.lines || [])
    : (result?.lines || []);

  const currentRawText = result?.file_type === 'pdf'
    ? (result.pages?.find(p => p.page === activePage)?.raw_text || '')
    : (result?.raw_text || '');

  // Render canvas with image & bounding boxes
  useEffect(() => {
    if (!previewUrl || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.src = previewUrl;
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);

      if (showBBoxes && currentLines.length > 0) {
        currentLines.forEach((line) => {
          const isSelected = selectedLine?.text === line.text;
          const [x, y, w, h] = line.bbox;

          ctx.strokeStyle = isSelected ? '#38bdf8' : 'rgba(99, 102, 241, 0.8)';
          ctx.lineWidth = isSelected ? 4 : 2;
          ctx.fillStyle = isSelected ? 'rgba(56, 189, 248, 0.25)' : 'rgba(99, 102, 241, 0.15)';

          ctx.beginPath();
          ctx.rect(x, y, w, h);
          ctx.fill();
          ctx.stroke();

          // Confidence badge
          ctx.fillStyle = '#6366f1';
          ctx.fillRect(x, Math.max(0, y - 16), 36, 14);
          ctx.fillStyle = '#ffffff';
          ctx.font = '10px monospace';
          const confPercent = Math.round(line.confidence * 100);
          ctx.fillText(confPercent + '%', x + 4, Math.max(10, y - 5));
        });
      }
    };
  }, [previewUrl, currentLines, showBBoxes, selectedLine]);

  const copyText = () => {
    navigator.clipboard.writeText(currentRawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = (type: string) => {
    if (!result) return;
    window.open('/api/export/' + result.task_id + '/' + type, '_blank');
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-wide bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              AirDoc Studio
            </h1>
            <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> 100% Offline & Private
            </span>
          </div>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/50 text-xs">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="text-slate-400">Engine:</span>
            <span className="font-semibold text-slate-200">PP-OCRv4</span>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/30 transition cursor-pointer"
          >
            <Upload className="w-4 h-4" /> Open Document
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.pdf"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Controls */}
        <aside className="w-80 border-r border-slate-800 bg-slate-900/40 flex flex-col justify-between p-4 overflow-y-auto shrink-0 space-y-6">
          <div className="space-y-5">
            <div>
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-indigo-400" /> Settings & Pipeline
              </h2>

              {/* Language */}
              <div className="space-y-1.5 mb-4">
                <label className="text-xs text-slate-300 font-medium">Recognition Language</label>
                <select
                  value={lang}
                  onChange={(e) => setLang(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="en">English (PP-OCRv4)</option>
                  <option value="ch">Chinese & English</option>
                  <option value="french">French</option>
                  <option value="german">German</option>
                  <option value="korean">Korean</option>
                  <option value="japan">Japanese</option>
                  <option value="es">Spanish</option>
                </select>
              </div>

              {/* Preprocessing Toggles */}
              <div className="space-y-2.5">
                <label className="text-xs text-slate-400 font-medium">Computer Vision Preprocessing</label>
                <label className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/40 border border-slate-800 hover:border-slate-700 cursor-pointer">
                  <span className="text-xs text-slate-300">Auto-Deskew (Rotate)</span>
                  <input
                    type="checkbox"
                    checked={deskew}
                    onChange={(e) => setDeskew(e.target.checked)}
                    className="accent-indigo-500 rounded w-4 h-4 cursor-pointer"
                  />
                </label>

                <label className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/40 border border-slate-800 hover:border-slate-700 cursor-pointer">
                  <span className="text-xs text-slate-300">Contrast Boost (CLAHE)</span>
                  <input
                    type="checkbox"
                    checked={enhance}
                    onChange={(e) => setEnhance(e.target.checked)}
                    className="accent-indigo-500 rounded w-4 h-4 cursor-pointer"
                  />
                </label>

                <label className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/40 border border-slate-800 hover:border-slate-700 cursor-pointer">
                  <span className="text-xs text-slate-300">Adaptive Binarization</span>
                  <input
                    type="checkbox"
                    checked={binarize}
                    onChange={(e) => setBinarize(e.target.checked)}
                    className="accent-indigo-500 rounded w-4 h-4 cursor-pointer"
                  />
                </label>
              </div>
            </div>

            {/* GPU Acceleration */}
            <div className="pt-2 border-t border-slate-800/80">
              <label className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/40 border border-slate-800 hover:border-slate-700 cursor-pointer">
                <div>
                  <div className="text-xs text-slate-200 font-medium">NVIDIA GPU (CUDA)</div>
                  <div className="text-[10px] text-slate-400">Accelerate deep learning</div>
                </div>
                <input
                  type="checkbox"
                  checked={useGpu}
                  onChange={(e) => setUseGpu(e.target.checked)}
                  className="accent-indigo-500 rounded w-4 h-4 cursor-pointer"
                />
              </label>
            </div>
          </div>

          {/* Action Trigger */}
          <div className="space-y-3">
            <button
              onClick={runOCR}
              disabled={!file || loading}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-lg bg-gradient-to-r from-indigo-500 to-cyan-500 text-white hover:opacity-95 shadow-indigo-500/25 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin" /> Processing Offline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Run Offline OCR
                </>
              )}
            </button>
          </div>
        </aside>

        {/* Center: Canvas / Document Viewer */}
        <main
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="flex-1 bg-slate-950 flex flex-col relative overflow-hidden"
        >
          {/* Canvas Floating Toolbar */}
          <div className="absolute top-4 left-6 z-10 flex items-center gap-2 bg-slate-900/90 backdrop-blur border border-slate-800 px-3 py-1.5 rounded-xl shadow-xl">
            <button
              onClick={() => setZoom((z) => Math.min(z + 0.2, 3))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono text-slate-300 w-12 text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-slate-800 mx-1" />
            <button
              onClick={() => setShowBBoxes(!showBBoxes)}
              className="px-2.5 py-1 text-xs rounded font-medium flex items-center gap-1.5 transition text-slate-400 hover:bg-slate-800"
            >
              <Eye className="w-3.5 h-3.5" /> Bounding Boxes
            </button>
          </div>

          {/* Document Area */}
          <div className="flex-1 overflow-auto flex items-center justify-center p-8">
            {!previewUrl ? (
              <div 
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center justify-center border-2 border-dashed border-slate-800 hover:border-indigo-500/50 bg-slate-900/20 rounded-2xl p-12 max-w-md text-center transition cursor-pointer group"
              >
                <div className="p-4 rounded-full bg-slate-900 border border-slate-800 text-indigo-400 group-hover:scale-110 transition mb-4">
                  <Upload className="w-8 h-8" />
                </div>
                <h3 className="text-sm font-semibold text-slate-200 mb-1">
                  Drag & Drop Document or Scanned Image
                </h3>
                <p className="text-xs text-slate-400">
                  Supports PNG, JPG, WEBP, TIFF, and multi-page PDF files
                </p>
              </div>
            ) : (
              <div
                style={{ transform: 'scale(' + zoom + ')', transformOrigin: 'center center' }}
                className="transition-transform duration-100 shadow-2xl rounded-lg overflow-hidden border border-slate-800 bg-black/40"
              >
                <canvas ref={canvasRef} className="max-w-none block" />
              </div>
            )}
          </div>
        </main>

        {/* Right Sidebar: Extracted Text & Export */}
        <aside className="w-96 border-l border-slate-800 bg-slate-900/40 flex flex-col justify-between shrink-0">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-cyan-400" /> Extracted Text
              </h2>
              {currentLines.length > 0 && (
                <span className="text-[11px] text-slate-400 font-mono">
                  {currentLines.length} text segments detected
                </span>
              )}
            </div>
            {currentRawText && (
              <button
                onClick={copyText}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center gap-1 text-xs cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            )}
          </div>

          {/* Results List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {!result ? (
              <div className="text-center py-16 text-slate-500 text-xs">
                Upload a document and click "Run Offline OCR" to inspect extracted tokens.
              </div>
            ) : (
              <div className="space-y-2">
                {currentLines.map((line, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedLine(line)}
                    className="p-2.5 rounded-xl border text-xs cursor-pointer transition bg-slate-800/40 border-slate-800 hover:border-slate-700"
                  >
                    <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                      <span className="font-mono">#{idx + 1}</span>
                      <span className="font-mono text-emerald-400">
                        {Math.round(line.confidence * 100)}% conf
                      </span>
                    </div>
                    <div className="text-slate-100 font-medium leading-relaxed select-all">
                      {line.text}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Export Center */}
          <div className="p-4 border-t border-slate-800 bg-slate-900/60 space-y-2">
            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Export Outputs
            </h3>
            <div className="grid grid-cols-3 gap-2">
              <button
                disabled={!result}
                onClick={() => handleExport('txt')}
                className="flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-semibold text-slate-200 border border-slate-700/50 transition cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> TXT
              </button>
              <button
                disabled={!result}
                onClick={() => handleExport('json')}
                className="flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-semibold text-slate-200 border border-slate-700/50 transition cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> JSON
              </button>
              <button
                disabled={!result}
                onClick={() => handleExport('pdf')}
                className="flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 transition cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> PDF (OCR)
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
