import React, { useState } from 'react';
import { ReferenceDetail } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { ChevronRight, Check, X, AlertTriangle } from 'lucide-react';
import { ReferenceDetailModal } from './ReferenceDetailModal';

interface ReferenceTableProps {
  references: ReferenceDetail[];
  onReferenceUpdated?: (updatedRef: ReferenceDetail) => void;
}

export const ReferenceTable: React.FC<ReferenceTableProps> = ({
  references,
  onReferenceUpdated,
}) => {
  const [selectedRef, setSelectedRef] = useState<ReferenceDetail | null>(null);

  if (!references || references.length === 0) {
    return (
      <div className="p-8 text-center glass-card rounded-2xl border border-slate-800 space-y-2">
        <p className="text-slate-400 text-sm">No references match the active filter or search criteria.</p>
      </div>
    );
  }

  return (
    <>
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4 w-12 text-center">#</th>
                <th className="py-3.5 px-4 min-w-[280px]">Reference / Matched Work</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-center">Confidence</th>
                <th className="py-3.5 px-4 text-center">Title Sim</th>
                <th className="py-3.5 px-4 text-center">Author Sim</th>
                <th className="py-3.5 px-4 text-center">Year</th>
                <th className="py-3.5 px-4 text-center">DOI</th>
                <th className="py-3.5 px-4 w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {references.map((ref) => {
                const ver = ref.verification_result;
                const status = ver?.status || 'NOT FOUND';
                const confidence = Math.round(ver?.confidence || 0);
                const titleSim = Math.round((ver?.title_similarity || 0) * 100);
                const authorSim = Math.round((ver?.author_similarity || 0) * 100);
                const displayTitle = ver?.matched_title || ref.title || ref.raw_text;

                return (
                  <tr
                    key={ref.id}
                    onClick={() => setSelectedRef(ref)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3.5 px-4 text-center font-bold text-slate-400 group-hover:text-brand-300">
                      [{ref.reference_number}]
                    </td>

                    <td className="py-3.5 px-4 space-y-1">
                      <div className="font-semibold text-slate-100 group-hover:text-brand-300 transition-colors line-clamp-1">
                        {displayTitle}
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1 font-mono">
                        {ref.raw_text}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <StatusBadge status={status} size="sm" />
                    </td>

                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      <div className="flex flex-col items-center">
                        <span className="font-bold text-slate-200">{confidence}%</span>
                        <div className="w-12 h-1 bg-slate-800 rounded-full overflow-hidden mt-1">
                          <div
                            className={`h-full ${
                              confidence >= 85
                                ? 'bg-emerald-500'
                                : confidence >= 60
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${confidence}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-center font-medium">
                      {ver ? `${titleSim}%` : '—'}
                    </td>

                    <td className="py-3.5 px-4 text-center font-medium">
                      {ver ? `${authorSim}%` : '—'}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      {ver ? (
                        ver.year_match ? (
                          <span className="inline-flex items-center text-emerald-400 font-bold" title="Year Matches">
                            <Check className="w-4 h-4" />
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-amber-400 font-bold" title="Year Mismatch">
                            <AlertTriangle className="w-4 h-4" />
                          </span>
                        )
                      ) : (
                        '—'
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      {ref.doi ? (
                        ver?.doi_match ? (
                          <span className="inline-flex items-center text-emerald-400 font-bold" title="DOI Matches Record">
                            <Check className="w-4 h-4" />
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-rose-400 font-bold" title="DOI Mismatch or Invalid">
                            <X className="w-4 h-4" />
                          </span>
                        )
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-right text-slate-500 group-hover:text-slate-200">
                      <ChevronRight className="w-4 h-4" />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRef && (
        <ReferenceDetailModal
          reference={selectedRef}
          onClose={() => setSelectedRef(null)}
          onUpdated={(updated) => {
            setSelectedRef(updated);
            if (onReferenceUpdated) {
              onReferenceUpdated(updated);
            }
          }}
        />
      )}
    </>
  );
};
