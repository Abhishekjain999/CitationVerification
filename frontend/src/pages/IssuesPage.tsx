import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { PaperDetail, PaperIssue } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { IssueList } from '../components/issues/IssueList';
import { AlertTriangle } from 'lucide-react';

export const IssuesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [issues, setIssues] = useState<PaperIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {

    if (!id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [paperData, issuesData] = await Promise.all([
          api.getPaper(id),
          api.getPaperIssues(id),
        ]);
        setPaper(paperData);
        setIssues(issuesData);
      } catch {
        setError('Failed to load issues. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleSelectReference = (refId: string) => {
    navigate(`/papers/${id}/references?reference=${encodeURIComponent(refId)}`);
  };

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (!paper && loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Loading integrity issues...
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper || undefined} />

      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-6xl mx-auto overflow-y-auto">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-amber-400" />
            <span>Integrity & Reference Inconsistencies</span>
          </h1>
          <p className="text-xs text-slate-400">
            Detected DOI mismatches, year/venue discrepancies, unindexed works, duplicate bibliography entries, and orphan citations
          </p>
        </div>

        <IssueList issues={issues} onSelectReference={handleSelectReference} />
      </main>
    </div>
  );
};
