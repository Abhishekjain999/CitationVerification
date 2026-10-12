import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, Sparkles, Upload, CheckCircle2, AlertTriangle, Database, ArrowRight, Quote, FileCheck, TrendingUp, Award } from 'lucide-react';
import { api } from '../services/api';
import { PaperSummary } from '../types';


export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [recentPapers, setRecentPapers] = useState<PaperSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingDemo, setLoadingDemo] = useState(false);

  useEffect(() => {
    const fetchPapers = async () => {
      try {
        const papers = await api.listPapers();
        setRecentPapers(papers);
      } catch {
        setError('Failed to load papers. Please check the backend connection and retry.');
      } finally {
        setLoading(false);
      }
    };
    fetchPapers();
  }, []);

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

  if (error) return <div role="alert" className="p-8 text-red-300">{error} <button className="underline" onClick={() => window.location.reload()}>Retry</button></div>;

  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto px-4 space-y-6 pt-6">
        <div className="absolute inset-0 -top-24 bg-gradient-to-b from-brand-600/10 via-transparent to-transparent blur-3xl pointer-events-none -z-10" />

        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Next-Generation Academic Verification Engine</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Verify the sources <br />
          <span className="gradient-text">behind your research.</span>
        </h1>

        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          AI-powered research paper and reference verification. Extract paper metadata, cross-examine citations across OpenAlex, Crossref & Semantic Scholar, detect DOI mismatches, and validate semantic claim support.
        </p>

        {/* Hero CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link
            to="/upload"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-xl shadow-brand-600/30 transition-all hover:scale-[1.02]"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Research Paper PDF</span>
          </Link>

          <button
            onClick={handleLoadDemo}
            disabled={loadingDemo}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 font-semibold text-sm flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>{loadingDemo ? 'Preparing Demo...' : 'Try Demo Paper'}</span>
          </button>
        </div>

        {/* Trust Badges */}
        <div className="pt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400 border-t border-slate-800/80 max-w-xl mx-auto">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Multi-Database Triangulation</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Critical DOI Validation</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Semantic Claim Entailment</span>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-xs uppercase font-bold text-brand-400 tracking-wider">
            Comprehensive Verification Architecture
          </h2>
          <p className="text-2xl font-bold text-white">
            Beyond Simple Citation Parsing
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Tri-Source Scholarly Search</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Concurrent querying across OpenAlex, Crossref, and Semantic Scholar with fuzzy title normalization, author set similarity, and venue acronym expansion.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Critical DOI Mismatch Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Resolves in-text DOIs directly via Crossref to prevent citation spoofing and flag instances where a DOI points to an unrelated publication.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Quote className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Semantic Claim Support</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Evaluates whether the cited paper’s abstract actually substantiates the claim made in the paper’s text using embedding-based cosine similarity and token overlap.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <FileCheck className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Orphan & Duplicate Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Identifies orphan citations cited in the body with missing bibliography entries, unused references, and duplicate entries pointing to the same work.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Reference Health Score</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Computes a weighted 0–100 ResearchGuard Health Score evaluating reference verification rate, metadata fidelity, coverage, and bibliography hygiene.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3 glass-card-hover">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Publication-Grade PDF Reports</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generate and download complete, styled PDF integrity audit reports suitable for journal submissions, peer review, and academic presentations.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Analyzed Papers Roster */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Analyzed Papers</h2>
            <p className="text-xs text-slate-400">Recently uploaded and processed research papers</p>
          </div>
          <Link
            to="/upload"
            className="text-xs font-medium text-brand-400 hover:text-brand-300 flex items-center gap-1"
          >
            <span>Analyze new PDF</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading papers...</div>
        ) : recentPapers.length === 0 ? (
          <div className="glass-card rounded-2xl p-8 text-center border border-slate-800 space-y-3">
            <FileText className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-slate-300 text-sm font-semibold">No papers analyzed yet</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Upload a research paper PDF or launch the pre-packaged demo dataset to inspect full verification features.
            </p>
            <div className="pt-2 flex justify-center gap-3">
              <Link
                to="/upload"
                className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold"
              >
                Upload Paper
              </Link>
              <button
                onClick={handleLoadDemo}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
              >
                Load Demo Dataset
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentPapers.map((paper) => (
              <Link
                key={paper.id}
                to={`/papers/${paper.id}`}
                className="glass-card rounded-2xl p-5 border border-slate-800 glass-card-hover flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {paper.publication_year || 'Paper'}
                    </span>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        paper.health_score >= 85
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : paper.health_score >= 70
                          ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {paper.health_rating === 'Inconclusive' ? 'Incomplete' : `${Math.round(paper.health_score)}/100`}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug">
                    {paper.title || paper.filename}
                  </h3>

                  <p className="text-xs text-slate-400 line-clamp-1">
                    {paper.authors && paper.authors.length > 0 ? paper.authors.join(', ') : 'Author(s) unspecified'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                  <span>{paper.total_references} References</span>
                  <span className="text-brand-400 font-medium flex items-center gap-1">
                    View Analysis <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
