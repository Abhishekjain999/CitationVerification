import React, { useState } from 'react';
import { ReferenceDetail } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { X, ExternalLink, RefreshCw, Database, BookOpen, Quote, ShieldCheck } from 'lucide-react';
import { api } from '../../services/api';

interface ReferenceDetailModalProps {
  reference: ReferenceDetail | null;
  onClose: () => void;
  onUpdated?: (updatedRef: ReferenceDetail) => void;
}

export const ReferenceDetailModal: React.FC<ReferenceDetailModalProps> = ({
  reference,
  onClose,
  onUpdated,
}) => {
  const [reverifying, setReverifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!reference) return null;

  const ver = reference.verification_result;
  const mismatches = ver?.metadata_mismatches || [];

  const handleReverify = async () => {
    try {
      setReverifying(true);
      setError(null);
      const updated = await api.reverifyReference(reference.id);
      if (onUpdated) {
        onUpdated(updated);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Re-verification failed. Please retry.');
    } finally {
      setReverifying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-card rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden relative">
        {error && <p role="alert" className="p-3 text-red-300 text-sm">{error}</p>}
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/30 text-brand-300 flex items-center justify-center font-bold text-sm">
              #{reference.reference_number}
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">Reference Verification Record</h3>
                {ver && <StatusBadge status={ver.status} size="sm" />}
              </div>
              <p className="text-xs text-slate-400">
                Confidence:{' '}
                <strong className="text-brand-300">{ver?.confidence || 0}%</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleReverify}
              disabled={reverifying}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 flex items-center gap-1.5 transition disabled:opacity-50"
              title="Re-query Scholarly Databases"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reverifying ? 'animate-spin' : ''}`} />
              <span>{reverifying ? 'Searching...' : 'Re-Verify'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Original Reference Citation */}
          <div className="p-4 rounded-xl bg-slate-850/80 border border-slate-700/60 space-y-2">
            <div className="flex items-center gap-2 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
              <Quote className="w-3.5 h-3.5 text-brand-400" />
              <span>Original Reference Text in Uploaded Paper</span>
            </div>
            <p className="text-slate-100 font-mono text-xs leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {reference.raw_text}
            </p>
          </div>

          {/* Explanation Banner */}
          {ver?.explanation && (
            <div
              className={`p-4 rounded-xl border flex items-start gap-3 ${
                ver.status === 'VERIFIED'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                  : ver.status.includes('METADATA')
                  ? 'bg-amber-500/10 border-amber-500/20 text-amber-300'
                  : ver.status === 'INVALID DOI'
                  ? 'bg-red-500/15 border-red-500/30 text-red-300'
                  : 'bg-slate-800/60 border-slate-700/60 text-slate-300'
              }`}
            >
              <ShieldCheck className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <div className="font-bold text-sm">System Verification Finding</div>
                <p className="leading-relaxed text-xs">{ver.explanation}</p>
              </div>
            </div>
          )}

          {/* Side-by-Side Comparison: Parsed from PDF vs Retrieved from Databases */}
          {mismatches.length > 0 && <div className="p-4 rounded-xl bg-amber-950/20 text-amber-200 space-y-2">{mismatches.map((m, i) => <p key={i}><strong>{m.field}:</strong> {m.reference_value} → {m.db_value}. {m.explanation}</p>)}</div>}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Parsed Metadata */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h4 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-800">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                <span>Extracted from Reference</span>
              </h4>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Title</span>
                  <span className="font-medium text-slate-200">{reference.title || '—'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Authors</span>
                  <span className="font-medium text-slate-200">
                    {reference.authors && reference.authors.length > 0
                      ? reference.authors.join(', ')
                      : '—'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">Year</span>
                    <span className="font-medium text-slate-200">{reference.year || '—'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">DOI</span>
                    <span className="font-medium text-slate-200 truncate">{reference.doi || '—'}</span>
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Venue</span>
                  <span className="font-medium text-slate-200">
                    {reference.venue || reference.journal || reference.conference || '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Retrieved Scholarly Metadata */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h4 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-800">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                <span>Retrieved Scholarly Record</span>
              </h4>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Title</span>
                  <span className="font-medium text-emerald-300">
                    {ver?.matched_title || 'No record matched'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Authors</span>
                  <span className="font-medium text-slate-200">
                    {ver?.matched_authors && ver.matched_authors.length > 0
                      ? ver.matched_authors.join(', ')
                      : '—'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">Year</span>
                    <span className="font-medium text-slate-200">{ver?.matched_year || '—'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-semibold">DOI</span>
                    {ver?.matched_doi ? (
                      <a
                        href={ver.matched_url || `https://doi.org/${ver.matched_doi}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand-400 hover:underline flex items-center gap-1 truncate"
                      >
                        <span className="truncate">{ver.matched_doi}</span>
                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                    ) : (
                      '—'
                    )}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-semibold">Venue / Publisher</span>
                  <span className="font-medium text-slate-200">
                    {ver?.matched_venue || ver?.matched_publisher || '—'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Metric Comparison Gauges */}
          {ver && (
            <div className="p-4 rounded-xl bg-slate-850/60 border border-slate-700/60 space-y-3">
              <h4 className="font-bold text-white text-xs uppercase tracking-wider">
                Multi-Dimensional Similarity Evaluation
              </h4>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-center">
                  <div className="text-[10px] text-slate-400 uppercase">Title Match</div>
                  <div className="text-lg font-bold text-brand-300">
                    {Math.round((ver.title_similarity || 0) * 100)}%
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-center">
                  <div className="text-[10px] text-slate-400 uppercase">Author Match</div>
                  <div className="text-lg font-bold text-brand-300">
                    {Math.round((ver.author_similarity || 0) * 100)}%
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-center">
                  <div className="text-[10px] text-slate-400 uppercase">Year Verification</div>
                  <div className={`text-lg font-bold ${ver.year_match ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {ver.year_match ? '✓ Match' : '✗ Mismatch'}
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-center">
                  <div className="text-[10px] text-slate-400 uppercase">DOI Status</div>
                  <div className={`text-sm font-bold ${ver.doi_status === 'MATCH' ? 'text-emerald-400' : ver.doi_status === 'MISMATCH' ? 'text-red-400' : 'text-slate-400'}`}>
                    {ver.doi_status}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Sources Confirmed */}
          {ver?.verification_sources && ver.verification_sources.length > 0 && (
            <div className="flex items-center gap-2 pt-2">
              <span className="text-slate-400 text-xs">Scholarly confirmations:</span>
              <div className="flex gap-1.5">
                {ver.verification_sources.map((src, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium"
                  >
                    {src}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
