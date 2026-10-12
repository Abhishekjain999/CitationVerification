import React from 'react';
import { PaperDetail } from '../../types';
import { BookOpen, Calendar, Building, ExternalLink, Users, Sparkles, Lock, Unlock, Bookmark } from 'lucide-react';

interface PaperInfoCardProps {
  paper: PaperDetail;
}

export const PaperInfoCard: React.FC<PaperInfoCardProps> = ({ paper }) => {
  const venue = paper.venue || paper.journal || paper.conference || 'Unspecified Venue';
  const authorList = paper.authors && paper.authors.length > 0 ? paper.authors : ['Author(s) not listed'];

  return (
    <div className="space-y-6">
      {/* Main Metadata Banner */}
      <div className="glass-card rounded-2xl p-6 border border-slate-700/60 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-brand-600/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

        <div className="flex flex-wrap items-center gap-2 mb-3">
          {paper.article_type && (
            <span className="px-2.5 py-1 rounded-full bg-brand-500/10 text-brand-300 text-xs font-semibold border border-brand-500/20">
              {paper.article_type}
            </span>
          )}
          {paper.open_access ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
              <Unlock className="w-3 h-3" /> Open Access
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 text-xs font-medium border border-slate-700">
              <Lock className="w-3 h-3" /> Subscription
            </span>
          )}
          {paper.publication_year && (
            <span className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700">
              {paper.publication_year}
            </span>
          )}
        </div>

        <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight leading-snug">
          {paper.title || paper.filename}
        </h1>

        {/* Authors */}
        <div className="mt-4 flex items-start gap-2.5 text-sm text-slate-300">
          <Users className="w-4 h-4 text-brand-400 mt-1 flex-shrink-0" />
          <div className="flex flex-wrap gap-x-2 gap-y-1">
            {authorList.map((author, idx) => (
              <span key={idx} className="font-medium text-slate-200">
                {typeof author === 'string' ? author : (author as any).name}
                {idx < authorList.length - 1 ? ',' : ''}
              </span>
            ))}
            {paper.corresponding_author && (
              <span className="text-xs text-brand-300 ml-1">
                (Corr: {paper.corresponding_author})
              </span>
            )}
          </div>
        </div>

        {/* Publication Metadata Grid */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs text-slate-300 border-t border-slate-800/80 pt-4">
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/40">
            <Building className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Venue / Journal</div>
              <div className="font-medium text-white truncate" title={venue}>{venue}</div>
            </div>
          </div>

          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/40">
            <Calendar className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Date & Year</div>
              <div className="font-medium text-white">
                {paper.publication_date || paper.publication_year || 'Unspecified'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/40">
            <Bookmark className="w-4 h-4 text-slate-400 flex-shrink-0" />
            <div className="truncate">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">DOI / Identifier</div>
              {paper.doi ? (
                <a
                  href={paper.url || `https://doi.org/${paper.doi}`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-medium text-brand-400 hover:text-brand-300 flex items-center gap-1 truncate"
                >
                  <span className="truncate">{paper.doi}</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
              ) : (
                <span className="text-slate-400">No DOI detected</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* AI Summary Card */}
      {paper.ai_summary && (
        <div className="glass-card rounded-2xl p-5 border border-indigo-500/30 bg-indigo-950/20 shadow-lg">
          <div className="flex items-center gap-2 text-indigo-300 font-semibold text-sm mb-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>AI Executive Summary</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed">
            {paper.ai_summary}
          </p>
        </div>
      )}

      {/* Abstract */}
      {paper.abstract && (
        <div className="glass-card rounded-2xl p-6 border border-slate-700/60 space-y-2">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-brand-400" />
            <span>Abstract</span>
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
            {paper.abstract}
          </p>
        </div>
      )}

      {/* Keywords */}
      {paper.keywords && paper.keywords.length > 0 && (
        <div className="glass-card rounded-2xl p-5 border border-slate-700/60 space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Keywords & Research Concepts
          </h3>
          <div className="flex flex-wrap gap-2">
            {paper.keywords.map((kw, idx) => (
              <span
                key={idx}
                className="px-3 py-1 rounded-lg bg-slate-800/80 text-slate-200 text-xs font-medium border border-slate-700 hover:border-brand-500/50 hover:bg-slate-800 transition"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
