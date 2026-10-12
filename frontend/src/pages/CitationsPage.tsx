import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { PaperDetail, CitationOccurrence } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { CitationContextCard } from '../components/citations/CitationContextCard';
import { Quote } from 'lucide-react';

export const CitationsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [citations, setCitations] = useState<CitationOccurrence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {

    if (!id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [paperData, citationsData] = await Promise.all([
          api.getPaper(id),
          api.getPaperCitations(id),
        ]);
        setPaper(paperData);
        setCitations(citationsData);
      } catch {
        setError('Failed to load citation occurrences. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const filteredCitations = citations.filter((c) => {
    if (statusFilter === 'ALL') return true;
    return c.semantic_status === statusFilter;
  });

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (!paper && loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Loading citation contexts...
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper || undefined} />

      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-6xl mx-auto overflow-y-auto">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <Quote className="w-6 h-6 text-brand-400" />
              <span>In-Text Citation Contexts</span>
            </h1>
            <p className="text-xs text-slate-400">
              Citation contexts and preliminary relevance to retrieved abstracts. Similarity does not establish claim support.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
            {['ALL', 'STRONGLY RELATED', 'RELATED', 'WEAKLY RELATED', 'LOW RELEVANCE', 'INSUFFICIENT EVIDENCE'].map(
              (st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition ${
                    statusFilter === st
                      ? 'bg-brand-600 text-white shadow-md'
                      : 'bg-slate-850 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {st === 'ALL' ? 'All Claims' : st}
                </button>
              )
            )}
          </div>
        </div>

        {/* Citations List */}
        {filteredCitations.length === 0 ? (
          <div className="p-8 text-center glass-card rounded-2xl border border-slate-800 space-y-2">
            <p className="text-slate-400 text-sm">No citation occurrences found for this filter.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredCitations.map((cit) => (
              <CitationContextCard key={cit.id} citation={cit} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
