import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BookmarkCheck, AlertTriangle, Quote, Users, Building, Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { PaperDetail, PaperStatistics, PaperIssue } from '../types';
import { HealthGauge } from '../components/common/HealthGauge';
import { ScoreCard } from '../components/common/ScoreCard';
import { VerificationChart } from '../components/charts/VerificationChart';
import { ConfidenceChart, SourceDistributionChart } from '../components/charts/ConfidenceChart';
import { SeverityBadge } from '../components/common/StatusBadge';
import { Sidebar } from '../components/layout/Sidebar';

export const DashboardPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [stats, setStats] = useState<PaperStatistics | null>(null);
  const [issues, setIssues] = useState<PaperIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {

    if (!id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [paperData, statsData, issuesData] = await Promise.all([
          api.getPaper(id),
          api.getPaperStatistics(id),
          api.getPaperIssues(id),
        ]);
        setPaper(paperData);
        setStats(statsData);
        setIssues(issuesData);
      } catch {
        setError('Failed to load dashboard data. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  if (loading || !paper || !stats) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center text-xs text-slate-400">
        Loading paper integrity dashboard...
      </div>
    );
  }

  const venue = paper.venue || paper.journal || paper.conference || 'Academic Venue';

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar paper={paper} />

      <main className="flex-1 p-6 md:p-8 space-y-8 max-w-6xl mx-auto overflow-y-auto">
        {paper.processing_status === 'processing' && <p role="status" className="p-4 text-brand-200">Reanalysis is in progress. <Link className="underline" to={`/papers/${paper.id}/processing`}>View live progress</Link>. Previous results should not be used.</p>}
        {(paper.health_rating === 'Inconclusive' || (paper.paper_stats.verification_limitations?.length || 0) > 0) && <div role="status" className="p-4 rounded-xl border border-amber-600/40 text-amber-200 text-sm space-y-2"><p>Verification has limitations. Missing provider results do not indicate poor integrity or fabricated references.</p><p>Confirmed reference coverage: {paper.paper_stats.verification_coverage_pct ?? 0}%.</p>{paper.paper_stats.verification_limitations?.map(message => <p key={message}>{message}</p>)}</div>}
        {/* Paper Header Banner */}
        <div className="glass-card rounded-3xl p-6 border border-slate-700/60 shadow-xl relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-brand-500/10 text-brand-300 text-xs font-semibold border border-brand-500/20">
                {paper.article_type || 'Research Paper'}
              </span>
              {paper.publication_year && (
                <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700">
                  {paper.publication_year}
                </span>
              )}
              {paper.open_access && (
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
                  Open Access
                </span>
              )}
            </div>

            <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight leading-snug">
              {paper.title || paper.filename}
            </h1>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-300 pt-1">
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-brand-400" />
                <span>
                  {paper.authors && paper.authors.length > 0
                    ? paper.authors.slice(0, 3).join(', ') + (paper.authors.length > 3 ? ' et al.' : '')
                    : 'Authors unspecified'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-slate-400" />
                <span className="truncate max-w-[200px]">{venue}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 flex-shrink-0">
            <HealthGauge
              score={paper.health_score}
              rating={paper.processing_status === 'processing' ? 'Pending' : paper.health_rating}
              size="md"
            />
          </div>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <ScoreCard
            title="Total References"
            value={stats.total_references}
            subtitle={`${stats.verified_count} verified records`}
            icon={BookmarkCheck}
            variant="blue"
          />
          <ScoreCard
            title="Verified References"
            value={stats.verified_count}
            subtitle={`${Math.round((stats.verified_count / Math.max(stats.total_references, 1)) * 100)}% verification rate`}
            icon={CheckCircle2}
            variant="emerald"
          />
          <ScoreCard
            title="Metadata Issues"
            value={stats.metadata_issues_count}
            subtitle="Year/venue/author mismatches"
            icon={AlertTriangle}
            variant="amber"
          />
          <ScoreCard
            title="Citation Coverage"
            value={`${stats.citation_coverage_pct}%`}
            subtitle={`${stats.orphan_citations_count} orphan citations detected`}
            icon={Quote}
            variant={stats.citation_coverage_pct >= 85 ? 'emerald' : 'amber'}
          />
        </div>

        {/* AI Executive Summary */}
        {paper.ai_summary && (
          <div className="glass-card rounded-2xl p-5 border border-indigo-500/30 bg-indigo-950/20 shadow-lg space-y-2">
            <div className="flex items-center gap-2 text-indigo-300 font-bold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>AI Executive Paper Summary</span>
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {paper.ai_summary}
            </p>
          </div>
        )}

        {/* Visual Analytics Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Verification Breakdown Donut */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Verification Status Breakdown
              </h3>
            </div>
            <VerificationChart stats={stats} />
          </div>

          {/* Confidence Distribution Bar */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Confidence Distribution
              </h3>
            </div>
            <ConfidenceChart stats={stats} />
          </div>

          {/* Scholarly Sources Confirmed */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Scholarly Database Records
              </h3>
            </div>
            <SourceDistributionChart stats={stats} />
          </div>
        </div>

        {/* Detected Issues Quick View */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Detected Integrity & Citation Inconsistencies</span>
              </h3>
              <p className="text-xs text-slate-400">
                {issues.length} issues identified during multi-source verification and body text scan
              </p>
            </div>
            <Link
              to={`/papers/${paper.id}/issues`}
              className="text-xs font-medium text-brand-400 hover:text-brand-300 flex items-center gap-1"
            >
              <span>View all issues</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {issues.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-400 rounded-xl bg-slate-900/40 border border-slate-800">
              No integrity issues or metadata mismatches detected.
            </div>
          ) : (
            <div className="space-y-2.5">
              {issues.slice(0, 4).map((iss) => (
                <div
                  key={iss.id}
                  className="flex items-start justify-between gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs"
                >
                  <div className="flex items-start gap-2.5">
                    <SeverityBadge severity={iss.severity} size="sm" />
                    <div>
                      <div className="font-bold text-slate-200">{iss.title}</div>
                      <div className="text-slate-400 text-[11px] leading-relaxed mt-0.5">
                        {iss.description}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
