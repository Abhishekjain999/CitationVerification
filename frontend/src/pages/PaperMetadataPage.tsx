import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { PaperDetail } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { PaperInfoCard } from '../components/paper/PaperInfoCard';

export const PaperMetadataPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {

    if (!id) return;
    const fetchPaper = async () => {
      try {
        setLoading(true);
        const data = await api.getPaper(id);
        setPaper(data);
      } catch {
        setError('Failed to load paper info. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchPaper();
  }, [id]);

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (!paper && loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Loading paper information...
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper || undefined} />

      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-5xl mx-auto overflow-y-auto">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Paper Information & Extracted Metadata
          </h1>
          <p className="text-xs text-slate-400">
            Comprehensive paper properties, authors, sections, abstract, and generated summary
          </p>
        </div>

        {paper && <PaperInfoCard paper={paper} />}
      </main>
    </div>
  );
};
