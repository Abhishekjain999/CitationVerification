import React from 'react';
import { AlertCircle, X, Shield } from 'lucide-react';

interface DisclaimerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DisclaimerModal: React.FC<DisclaimerModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-card rounded-2xl max-w-lg w-full p-6 border border-slate-700 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 text-amber-400 mb-4">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Academic Verification Disclaimer</h3>
            <p className="text-xs text-slate-400">Important guidance on interpreting ResearchGuard results</p>
          </div>
        </div>

        <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
          <p>
            <strong className="text-white">ResearchGuard</strong> provides automated metadata and semantic reference verification by querying publicly accessible scholarly graphs (OpenAlex, Crossref, and Semantic Scholar).
          </p>
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 space-y-2">
            <p className="font-semibold text-amber-300 flex items-center gap-1.5">
              <Shield className="w-4 h-4" /> Academic Integrity Rule:
            </p>
            <p>
              A <em>"Not Found"</em> status does <strong>NOT</strong> prove that a research paper is fabricated. Scholarly indexes have varied coverage, embargo periods, and indexing criteria.
            </p>
            <p>
              Semantic support scores represent computational similarity and entailment estimates, not definitive scientific validation.
            </p>
          </div>
          <p className="text-xs text-slate-400">
            Results should always be reviewed by a qualified researcher or peer reviewer before making academic, publication, or misconduct-related determinations.
          </p>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition shadow-lg shadow-brand-600/20"
          >
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
};
