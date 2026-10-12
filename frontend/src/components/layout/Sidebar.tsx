import React from 'react';
import { NavLink, useParams, Link } from 'react-router-dom';
import { LayoutDashboard, FileText, BookmarkCheck, Quote, AlertTriangle, Download, ArrowLeft } from 'lucide-react';
import { PaperDetail } from '../../types';

interface SidebarProps {
  paper?: PaperDetail;
}

export const Sidebar: React.FC<SidebarProps> = ({ paper }) => {
  const { id } = useParams<{ id: string }>();
  const paperId = id || paper?.id;

  const navItems = [
    {
      to: `/papers/${paperId}`,
      end: true,
      label: 'Overview',
      icon: LayoutDashboard,
    },
    {
      to: `/papers/${paperId}/metadata`,
      label: 'Paper Information',
      icon: FileText,
    },
    {
      to: `/papers/${paperId}/references`,
      label: 'References',
      icon: BookmarkCheck,
      badge: paper ? String(paper.total_references || (paper as any).references?.length || '') : undefined,
    },
    {
      to: `/papers/${paperId}/citations`,
      label: 'Citation Contexts',
      icon: Quote,
    },
    {
      to: `/papers/${paperId}/issues`,
      label: 'Integrity Issues',
      icon: AlertTriangle,
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    },
    {
      to: `/papers/${paperId}/report`,
      label: 'Integrity Report',
      icon: Download,
    },
  ];

  return (
    <aside className="w-40 md:w-64 flex-shrink-0 border-r border-slate-800 bg-[#0b0f19]/60 flex flex-col justify-between p-3 md:p-4 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
      <div className="space-y-4">
        {paper?.paper_stats?.demo && <p className="text-xs text-amber-300">Demonstration: curated sample data. Results are not live verification.</p>}
        {/* Back Link */}
        <Link
          to="/papers"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>All Analyzed Papers</span>
        </Link>

        {/* Paper Mini Header */}
        {paper && (
          <div className="p-3 rounded-xl bg-slate-850/80 border border-slate-700/60 shadow-sm space-y-2">
            <h3 className="text-xs font-semibold text-white line-clamp-2 leading-relaxed" title={paper.title}>
              {paper.title || paper.filename}
            </h3>
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-700/40">
              <span>Score:</span>
              <span className={`font-bold ${paper.health_score >= 85 ? 'text-emerald-400' : paper.health_score >= 70 ? 'text-blue-400' : 'text-amber-400'}`}>
                {paper.health_rating === 'Inconclusive' ? 'Incomplete' : `${Math.round(paper.health_score)}/100`}
              </span>
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold border border-slate-700">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer / Database Badges */}
      <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Scholarly Providers Configured
        </div>
        <div className="flex flex-wrap gap-1 text-[10px]">
          <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> OpenAlex
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Crossref
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Semantic Scholar
          </span>
        </div>
      </div>
    </aside>
  );
};
