import React, { useCallback, useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { PaperDetail, ReferenceDetail, PaperStatistics } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { ReferenceFilterBar } from '../components/references/ReferenceFilterBar';
import { ReferenceTable } from '../components/references/ReferenceTable';
import { ReferenceDetailModal } from '../components/references/ReferenceDetailModal';

export const ReferencesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [query, setQuery] = useSearchParams();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [references, setReferences] = useState<ReferenceDetail[]>([]);
  const [stats, setStats] = useState<PaperStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('number');

  const fetchReferences = useCallback(async () => {

    if (!id) return;
    try {
      setLoading(true);
      const [paperData, refsData, statsData] = await Promise.all([
        api.getPaper(id),
        api.getPaperReferences(id, {
          status: statusFilter,
          search,
          sort_by: sortBy,
        }),
        api.getPaperStatistics(id),
      ]);
      setPaper(paperData);
      setReferences(refsData);
      setStats(statsData);
    } catch {
      setError('Failed to load references. Please check the backend connection and retry.');
    } finally {
      setLoading(false);
    }
  }, [id, statusFilter, search, sortBy]);

  useEffect(() => {
    // Data fetches update loading state while synchronizing with the API.
    // eslint-disable-next-line react/set-state-in-effect
    fetchReferences();
  }, [fetchReferences]);

  const handleReferenceUpdated = (updatedRef: ReferenceDetail) => {
    setReferences((prev) =>
      prev.map((r) => (r.id === updatedRef.id ? updatedRef : r))
    );
    if (id) Promise.all([api.getPaper(id), api.getPaperStatistics(id)]).then(([p, s]) => { setPaper(p); setStats(s); });
  };

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (!paper && loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Loading references roster...
      </div>
    );
  }

  const counts: Record<string, number> = stats
    ? {
        ALL: stats.total_references,
        VERIFIED: stats.verified_count,
        METADATA_ISSUES: stats.metadata_issues_count,
        POSSIBLE_MATCH: stats.possible_matches_count,
        NOT_FOUND: stats.not_found_count,
        INVALID_DOI: stats.invalid_doi_count,
        DUPLICATE: stats.duplicates_count,
      }
    : {};

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper || undefined} />
      <ReferenceDetailModal reference={references.find(r => r.id === query.get('reference')) || null} onClose={() => setQuery({})} onUpdated={handleReferenceUpdated} />

      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-6xl mx-auto overflow-y-auto">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Reference Verification Roster
          </h1>
          <p className="text-xs text-slate-400">
            Every reference parsed from the paper cross-examined across OpenAlex, Crossref, and Semantic Scholar
          </p>
        </div>

        {/* Filter and Search Bar */}
        <ReferenceFilterBar
          search={search}
          onSearchChange={setSearch}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          sortBy={sortBy}
          onSortByChange={setSortBy}
          counts={counts}
        />

        {/* Reference Table */}
        <ReferenceTable
          references={references}
          onReferenceUpdated={handleReferenceUpdated}
        />
      </main>
    </div>
  );
};
