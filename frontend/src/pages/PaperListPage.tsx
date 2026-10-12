import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { PaperSummary } from '../types';
import { FileText, Upload, Sparkles, Trash2, Search, AlertTriangle } from 'lucide-react';

export const PaperListPage: React.FC = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<PaperSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [loadingDemo, setLoadingDemo] = useState(false);

  const fetchPapers = async () => {
    try {
      setLoading(true);
      const data = await api.listPapers();
      setPapers(data);
    } catch {
      setError('Failed to load papers. Please check the backend connection and retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Loading state reflects the asynchronous API fetch.
    // eslint-disable-next-line react/set-state-in-effect
    fetchPapers();
  }, []);

  const handleDelete = async (e: React.MouseEvent, paperId: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (window.confirm('Are you sure you want to delete this paper analysis?')) {
      try {
        await api.deletePaper(paperId);
        setPapers((prev) => prev.filter((p) => p.id !== paperId));
      } catch {
        setError('Failed to delete paper. Please check the backend connection and retry.');
      }
    }
  };

  const handleLoadDemo = async () => {
    try {
      setLoadingDemo(true);
      const demo = await api.loadDemoPaper();
      navigate(`/papers/${demo.id}`);
    } catch {
      setError('Failed to load demo. Please check the backend connection and retry.');
    } finally {
      setLoadingDemo(false);
    }
  };

  const filtered = papers.filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    const tMatch = p.title && p.title.toLowerCase().includes(q);
    const fMatch = p.filename.toLowerCase().includes(q);
    const aMatch = p.authors && p.authors.some((a) => String(a).toLowerCase().includes(q));
    return tMatch || fMatch || aMatch;
  });

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Analyzed Research Papers
          </h1>
          <p className="text-xs text-slate-400">
            Repository of analyzed manuscripts, reference rosters, and integrity scores
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleLoadDemo}
            disabled={loadingDemo}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>{loadingDemo ? 'Loading...' : 'Load Demo Paper'}</span>
          </button>

          <Link
            to="/upload"
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-brand-600/30 transition"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload New PDF</span>
          </Link>
        </div>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Filter papers by title, author, or filename..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-slate-850 border border-slate-700/60 rounded-xl text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500"
        />
      </div>

      {/* Papers Table */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading papers roster...</div>
      ) : filtered.length === 0 ? (
        <div className="glass-card rounded-2xl p-10 text-center border border-slate-800 space-y-3">
          <FileText className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No research papers found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Upload your first research paper PDF or launch the sample demo paper to get started.
          </p>
          <div className="pt-2 flex justify-center gap-3">
            <Link
              to="/upload"
              className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold"
            >
              Upload PDF
            </Link>
            <button
              onClick={handleLoadDemo}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
            >
              Try Demo Paper
            </button>
          </div>
        </div>
      ) : (
        <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Research Paper Title</th>
                <th className="py-3.5 px-4">Publication Info</th>
                <th className="py-3.5 px-4 text-center">References</th>
                <th className="py-3.5 px-4 text-center">Issues</th>
                <th className="py-3.5 px-4 text-center">Health Score</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((paper) => {
                const score = Math.round(paper.health_score || 0);

                return (
                  <tr
                    key={paper.id}
                    onClick={() => navigate(`/papers/${paper.id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3.5 px-4 space-y-1 max-w-md">
                      <div className="font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-1">
                        {paper.title || paper.filename}
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">
                        {paper.authors && paper.authors.length > 0
                          ? paper.authors.join(', ')
                          : 'Authors unspecified'}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-400">
                      <div>{paper.journal || paper.conference || '—'}</div>
                      <div className="text-[10px]">{paper.publication_year || ''}</div>
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span className="font-bold text-slate-200">{paper.total_references}</span>
                      <span className="text-[10px] text-slate-400 block">
                        ({paper.verified_references} verified)
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      {paper.issue_count > 0 ? (
                        <span className="inline-flex items-center gap-1 text-amber-400 font-bold">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>{paper.issue_count}</span>
                        </span>
                      ) : (
                        <span className="text-emerald-400 font-bold">0</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-full font-extrabold text-xs ${
                          score >= 85
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : score >= 70
                            ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
                            : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {paper.health_rating === 'Inconclusive' ? 'Incomplete' : `${score}/100`}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/papers/${paper.id}`}
                          className="px-3 py-1.5 rounded-lg bg-brand-600/20 text-brand-300 hover:bg-brand-600 hover:text-white transition font-medium"
                        >
                          View
                        </Link>
                        <button
                          onClick={(e) => handleDelete(e, paper.id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-slate-800 transition"
                          title="Delete Paper"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
