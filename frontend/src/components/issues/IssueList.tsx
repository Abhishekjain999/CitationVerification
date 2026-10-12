import React, { useState } from 'react';
import { PaperIssue } from '../../types';
import { SeverityBadge } from '../common/StatusBadge';
import { AlertOctagon, AlertTriangle, Info, ChevronRight } from 'lucide-react';

interface IssueListProps {
  issues: PaperIssue[];
  onSelectReference?: (refId: string) => void;
}

export const IssueList: React.FC<IssueListProps> = ({ issues, onSelectReference }) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const filteredIssues = issues.filter((iss) => {
    if (severityFilter === 'ALL') return true;
    return iss.severity === severityFilter;
  });

  const criticalCount = issues.filter((i) => i.severity === 'CRITICAL').length;
  const warningCount = issues.filter((i) => i.severity === 'WARNING').length;
  const infoCount = issues.filter((i) => i.severity === 'INFO').length;

  return (
    <div className="space-y-6">
      {/* Severity Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setSeverityFilter('ALL')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
            severityFilter === 'ALL'
              ? 'bg-brand-600 text-white shadow-md'
              : 'bg-slate-850 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>All Issues</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">
            {issues.length}
          </span>
        </button>

        <button
          onClick={() => setSeverityFilter('CRITICAL')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
            severityFilter === 'CRITICAL'
              ? 'bg-red-600 text-white shadow-md'
              : 'bg-slate-850 text-red-400 hover:bg-red-500/10 border border-slate-800'
          }`}
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span>Critical</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-red-950 text-red-300 border border-red-800/40">
            {criticalCount}
          </span>
        </button>

        <button
          onClick={() => setSeverityFilter('WARNING')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
            severityFilter === 'WARNING'
              ? 'bg-amber-600 text-white shadow-md'
              : 'bg-slate-850 text-amber-400 hover:bg-amber-500/10 border border-slate-800'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Warnings</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-950 text-amber-300 border border-amber-800/40">
            {warningCount}
          </span>
        </button>

        <button
          onClick={() => setSeverityFilter('INFO')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1.5 ${
            severityFilter === 'INFO'
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-slate-850 text-blue-400 hover:bg-blue-500/10 border border-slate-800'
          }`}
        >
          <Info className="w-3.5 h-3.5" />
          <span>Info / Hygiene</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-blue-950 text-blue-300 border border-blue-800/40">
            {infoCount}
          </span>
        </button>
      </div>

      {/* Issues List */}
      {filteredIssues.length === 0 ? (
        <div className="p-8 text-center glass-card rounded-2xl border border-slate-800 space-y-2">
          <p className="text-slate-400 text-sm">No issues detected in this category.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredIssues.map((issue) => {
            const isCritical = issue.severity === 'CRITICAL';
            const isWarning = issue.severity === 'WARNING';

            const cardBorder = isCritical
              ? 'border-red-500/30 hover:border-red-500/50 bg-red-950/10'
              : isWarning
              ? 'border-amber-500/30 hover:border-amber-500/50 bg-amber-950/10'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40';

            return (
              <div
                key={issue.id}
                className={`glass-card rounded-2xl p-5 border transition-all duration-200 shadow-md ${cardBorder} space-y-3`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      <SeverityBadge severity={issue.severity} size="sm" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white tracking-tight">
                        {issue.title}
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed mt-1">
                        {issue.description}
                      </p>
                    </div>
                  </div>

                  {issue.reference_id && onSelectReference && (
                    <button
                      onClick={() => onSelectReference(issue.reference_id!)}
                      className="px-2.5 py-1 rounded-lg bg-slate-850 hover:bg-slate-800 text-xs font-medium text-brand-300 border border-slate-700 flex items-center gap-1 transition flex-shrink-0"
                    >
                      <span>View Ref #{issue.reference_number || ''}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Details Breakdown if available */}
                {issue.details && Object.keys(issue.details).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                    {issue.details.field && (
                      <div>
                        <strong className="text-slate-300">Mismatch Field:</strong> {issue.details.field}
                      </div>
                    )}
                    {issue.details.reference_value && (
                      <div>
                        <strong className="text-slate-300">Reference Specified:</strong> {issue.details.reference_value}
                      </div>
                    )}
                    {issue.details.db_value && (
                      <div>
                        <strong className="text-slate-300">Scholarly Database:</strong> {issue.details.db_value}
                      </div>
                    )}
                    {issue.details.resolved_title && (
                      <div>
                        <strong className="text-slate-300">DOI Target Work:</strong> {issue.details.resolved_title}
                      </div>
                    )}
                    {issue.details.sentence && (
                      <div className="italic text-slate-300 font-serif">
                        "{issue.details.sentence}"
                      </div>
                    )}
                    {issue.details.recommended_action && <p><strong>Recommended action:</strong> {issue.details.recommended_action}</p>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
