import React from 'react';
import { CitationOccurrence } from '../../types';
import { Quote, CheckCircle2, AlertCircle, HelpCircle, ShieldCheck, Sparkles } from 'lucide-react';

interface CitationContextCardProps {
  citation: CitationOccurrence;
}

export const CitationContextCard: React.FC<CitationContextCardProps> = ({ citation }) => {
  const status = citation.semantic_status;
  const score = Math.round(citation.semantic_relevance_score || 0);

  let statusBg = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = HelpCircle;

  if (status === 'STRONGLY RELATED') {
    statusBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    Icon = CheckCircle2;
  } else if (status === 'RELATED') {
    statusBg = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    Icon = ShieldCheck;
  } else if (status === 'WEAKLY RELATED') {
    statusBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = AlertCircle;
  } else if (status === 'LOW RELEVANCE') {
    statusBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    Icon = AlertCircle;
  }

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4 hover:border-slate-700 transition shadow-lg">
      {/* Card Header: Marker, Section, Page */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg bg-brand-600/20 text-brand-300 text-xs font-bold border border-brand-500/30">
            Citation {citation.citation_marker}
          </span>
          <span className="text-xs text-slate-400">
            Page {citation.page_number} • <strong className="text-slate-200">{citation.section}</strong>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <span>Preliminary Relevance:</span>
            <span className="font-bold text-brand-300">{status === 'INSUFFICIENT EVIDENCE' ? 'Not assessed' : `${score}%`}</span>
          </div>
          <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${statusBg}`}>
            <Icon className="w-3.5 h-3.5" />
            <span>{status}</span>
          </span>
        </div>
      </div>

      {/* Claim Sentence */}
      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
        <div className="flex items-center gap-1.5 text-[10px] uppercase font-bold text-slate-400 tracking-wider">
          <Quote className="w-3.5 h-3.5 text-brand-400" />
          <span>In-Text Claim Context</span>
        </div>
        <p className="text-xs text-slate-200 leading-relaxed font-serif italic">
          "{citation.sentence}"
        </p>
      </div>

      {/* Referenced Paper Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl bg-slate-850/60 border border-slate-700/50 text-xs text-slate-300">
        <div className="space-y-0.5">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Cited Reference</span>
          <div className="font-medium text-white line-clamp-1">
            {citation.reference_title || 'Reference entry in bibliography'}
          </div>
          {citation.reference_authors && (
            <div className="text-[11px] text-slate-400 truncate">
              {citation.reference_authors.join(', ')} ({citation.reference_year || 'Year unspecified'})
            </div>
          )}
        </div>
      </div>

      {/* Semantic Entailment Explanation */}
      {citation.explanation && (
        <div className="flex items-start gap-2 text-xs text-slate-400 bg-slate-900/40 p-3 rounded-lg border border-slate-800/80">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="text-slate-300">Semantic Assessment:</strong> {citation.explanation}
          </p>
        </div>
      )}
    </div>
  );
};
