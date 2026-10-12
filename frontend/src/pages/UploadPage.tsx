import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, Sparkles, X, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    setSelectedFile(null);
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Invalid file format. Please upload an academic research paper in PDF format (.pdf).');
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds the 50 MB limit.');
      return;
    }
    setSelectedFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setError(null);
      const paper = await api.uploadPaper(selectedFile);
      // Navigate to Processing screen
      navigate(`/papers/${paper.id}/processing`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload paper. Please try again.');
      setIsUploading(false);
    }
  };

  const handleLoadDemo = async () => {
    try {
      setLoadingDemo(true);
      const demo = await api.loadDemoPaper();
      navigate(`/papers/${demo.id}`);
    } catch {
      setError('Failed to initialize demo dataset.');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Upload Research Paper
        </h1>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          Upload your PDF manuscript or publication to analyze citations, verify references against OpenAlex, Crossref & Semantic Scholar, and generate an integrity score.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 animate-in fade-in duration-150">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Choose a PDF research paper"
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInputRef.current?.click(); } }}
        className={`glass-card rounded-3xl p-10 border-2 border-dashed transition-all duration-200 cursor-pointer text-center space-y-4 ${
          isDragging
            ? 'border-brand-400 bg-brand-600/10 scale-[1.01]'
            : selectedFile
            ? 'border-emerald-500/50 bg-emerald-950/10'
            : 'border-slate-700 hover:border-slate-500 bg-slate-900/40'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center mx-auto shadow-inner">
          <Upload className="w-8 h-8" />
        </div>

        <div className="space-y-1">
          <p className="text-base font-bold text-white">
            {selectedFile ? selectedFile.name : 'Drop your research paper PDF here'}
          </p>
          <p className="text-xs text-slate-400">
            {selectedFile
              ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze`
              : 'or click to browse from your device'}
          </p>
        </div>

        <div className="flex items-center justify-center gap-4 text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 max-w-sm mx-auto">
          <span>Format: <strong>PDF only</strong></span>
          <span>•</span>
          <span>Max file size: <strong>50 MB</strong></span>
        </div>
      </div>

      {/* Selected File Card & Submit CTA */}
      {selectedFile && (
        <div className="glass-card rounded-2xl p-5 border border-slate-700 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-brand-600/20 text-brand-400 border border-brand-500/30">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-white line-clamp-1">{selectedFile.name}</div>
                <div className="text-xs text-slate-400">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </div>
              </div>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelectedFile(null);
              }}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={handleUploadAndAnalyze}
            disabled={isUploading}
            className="w-full py-3.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-brand-600/30 transition disabled:opacity-50"
          >
            {isUploading ? (
              <span>Uploading & Initializing...</span>
            ) : (
              <>
                <span>Analyze Paper & Verify References</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      )}

      {/* Demo Section */}
      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start gap-1.5 text-xs font-bold text-amber-400">
            <Sparkles className="w-4 h-4" />
            <span>Instant Demo Dataset</span>
          </div>
          <p className="text-xs text-slate-400">
            Explore a pre-loaded paper containing real-world citations, metadata issues, critical DOI mismatches, and orphan references.
          </p>
        </div>

        <button
          onClick={handleLoadDemo}
          disabled={loadingDemo}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 text-xs font-semibold whitespace-nowrap transition disabled:opacity-50"
        >
          {loadingDemo ? 'Loading...' : 'Launch Demo Paper'}
        </button>
      </div>
    </div>
  );
};
