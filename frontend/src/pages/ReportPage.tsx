import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { PaperDetail, PaperStatistics } from '../types';
import { Sidebar } from '../components/layout/Sidebar';
import { Download, FileCheck } from 'lucide-react';


export const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [stats, setStats] = useState<PaperStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {

    if (!id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [paperData, statsData] = await Promise.all([
          api.getPaper(id),
          api.getPaperStatistics(id),
        ]);
        setPaper(paperData);
        setStats(statsData);
      } catch {
        setError('Failed to load report data. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (!paper && loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Preparing integrity report preview...
      </div>
    );
  }

  const downloadUrl = id ? api.getReportDownloadUrl(id) : '#';

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper || undefined} />

      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-4xl mx-auto overflow-y-auto">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <FileCheck className="w-6 h-6 text-brand-400" />
              <span>Research Paper Integrity Report</span>
            </h1>
            <p className="text-xs text-slate-400">
              Downloadable audit dossier containing complete multi-source verification findings
            </p>
          </div>

          <a
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-lg shadow-brand-600/30 transition"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>

        {/* Paper Report Dossier Preview Card */}
        <a className="text-brand-300 text-sm underline" href={`${downloadUrl}?format=json`}>Download full evidence as JSON</a>
        {paper && stats && (
          <div className="glass-card rounded-3xl p-8 border border-slate-700/80 shadow-2xl space-y-8 bg-slate-900/60">
            {/* Report Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">
                    RG
                  </div>
                  <span className="text-lg font-bold text-white tracking-tight">
                    ResearchGuard Audit Report
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Automated Multi-Database Verification • OpenAlex • Crossref • Semantic Scholar
                </p>
              </div>

              <div className="text-right text-xs text-slate-400">
                <div>Analysis updated: {paper.updated_at?.slice(0, 10)}</div>
                <div className="text-emerald-400 font-semibold">Status: Completed</div>
              </div>
            </div>

            {/* Paper Title & Metadata */}
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white">{paper.title || paper.filename}</h2>
              <div className="text-xs text-slate-300">
                <strong>Authors:</strong>{' '}
                {paper.authors && paper.authors.length > 0 ? paper.authors.join(', ') : 'Unspecified'}
              </div>
              <div className="text-xs text-slate-400">
                <strong>Venue:</strong> {paper.venue || paper.journal || paper.conference || 'N/A'} •{' '}
                <strong>Year:</strong> {paper.publication_year || 'N/A'} •{' '}
                <strong>DOI:</strong> {paper.doi || 'None'}
              </div>
            </div>

            {/* Health Score Summary */}
            <div className="p-6 rounded-2xl bg-slate-850/80 border border-slate-700/60 flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="space-y-2 text-center sm:text-left">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  ResearchGuard Reference Health Score
                </div>
                <div className="text-4xl font-extrabold text-brand-400">
                  {paper.health_rating === 'Inconclusive' ? 'Incomplete' : <>{Math.round(paper.health_score)} <span className="text-lg text-slate-400">/ 100</span></>}
                </div>
                <div className="text-xs text-slate-300">
                  Rating: <strong className="text-emerald-400">{paper.health_rating}</strong>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-slate-400 text-[10px] uppercase">References</div>
                  <div className="text-lg font-bold text-white">{stats.total_references}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-slate-400 text-[10px] uppercase">Verified</div>
                  <div className="text-lg font-bold text-emerald-400">{stats.verified_count}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-slate-400 text-[10px] uppercase">Issues</div>
                  <div className="text-lg font-bold text-amber-400">{stats.metadata_issues_count}</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-slate-400 text-[10px] uppercase">Coverage</div>
                  <div className="text-lg font-bold text-brand-400">{stats.citation_coverage_pct}%</div>
                </div>
              </div>
            </div>

            {/* AI Executive Summary Preview */}
            {paper.ai_summary && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  AI Executive Summary
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-4 rounded-xl border border-slate-800">
                  {paper.ai_summary}
                </p>
              </div>
            )}

            {/* Academic Disclaimer Callout */}
            <div className="space-y-2 text-xs text-slate-300">
              <h3 className="font-bold">Score components</h3>
              {Object.entries(paper.score_breakdown || {}).map(([key, value]) => <div key={key}>{key.replaceAll('_', ' ')}: {Number(value).toFixed(1)}</div>)}
              <p className="text-slate-400">Verification 40 points; metadata 20; coverage 15; consistency 15; hygiene 10. Inconclusive checks reduce evidence coverage. Abstract relevance does not change the score. This is an aid for review, not an academic integrity certification.</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40 text-[11px] text-slate-400 space-y-1">
              <strong className="text-slate-300">Academic Disclaimer:</strong> ResearchGuard provides automated metadata and semantic verification based on available scholarly databases. A 'Not Found' status does not prove a publication is fabricated. All findings should be reviewed by a human researcher before making academic determinations.
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
