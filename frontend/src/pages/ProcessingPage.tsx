import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, Loader2, Circle, AlertCircle, Shield } from 'lucide-react';
import { api } from '../services/api';

const PIPELINE_STEPS = [
  { id: 1, label: 'PDF Uploaded & Validated', desc: 'Securely parsed raw PDF file buffer' },
  { id: 2, label: 'Extracting Paper Text & Layout', desc: 'Analyzing layout blocks, fonts, and page sequences via PyMuPDF' },
  { id: 3, label: 'Detecting Metadata & Structure', desc: 'Identifying paper title, authors, DOI, abstract, and sections' },
  { id: 4, label: 'Detecting Bibliography References', desc: 'Segmenting individual citation entries and formatting patterns' },
  { id: 5, label: 'Parsing Citations into Structured Metadata', desc: 'Extracting title, authors list, year, venue, and volume' },
  { id: 6, label: 'Searching Scholarly Databases', desc: 'Querying OpenAlex, Crossref, and Semantic Scholar concurrently' },
  { id: 7, label: 'Verifying References & Similarity Scoring', desc: 'Multi-dimensional fuzzy, title, author, year & venue matching' },
  { id: 8, label: 'In-Text Citation & Preliminary Relevance', desc: 'Comparing citation context with retrieved paper abstracts' },
  { id: 9, label: 'Detecting Integrity Issues & Inconsistencies', desc: 'Checking for invalid DOIs, orphan citations, and duplicates' },
  { id: 10, label: 'Generating Health Report & Dashboard', desc: 'Calculating ResearchGuard Reference Health Score' },
];

export const ProcessingPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState('Initializing verification pipeline...');

  useEffect(() => {
    if (!id) return;

    let isMounted = true;

    let pollTimer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const paper = await api.getPaper(id);
        if (!isMounted) return;
        setStatusMessage(paper.progress_stage || 'Queued');
        const stage = (paper.progress_stage || '').toLowerCase();
        setCurrentStep(stage.includes('completed') ? 10 : stage.includes('calculating') ? 10 : stage.includes('issues') ? 9 : stage.includes('in-text') ? 8 : stage.includes('searching') ? 6 : stage.includes('parsing') ? 5 : stage.includes('bibliography') ? 4 : stage.includes('metadata') ? 3 : 2);
        if (paper.processing_status === 'completed') {
          navigate(`/papers/${id}`);
        } else if (paper.processing_status === 'failed') {
          setError(paper.error_message || 'Analysis failed.');
        } else {
          pollTimer = setTimeout(poll, 1500);
        }
      } catch (err: any) {
        if (isMounted) setError(err.response?.data?.detail || err.message || 'Could not retrieve analysis status.');
      }
    };

    const runAnalysis = async () => {
      try {
        setStatusMessage('Executing scholarly search and NLP analysis...');
        await api.analyzePaper(id);

        if (isMounted) await poll();
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || err.message || 'Analysis encountered an error.');
        }
      }
    };

    runAnalysis();

    return () => {
      isMounted = false;
      clearTimeout(pollTimer);
    };
  }, [id, navigate]);

  return (
    <div className="max-w-2xl mx-auto py-12 px-4 space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="relative inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-600/20 border border-brand-500/30 text-brand-400 mb-2">
          <Shield className="w-7 h-7" />
          <Loader2 className="w-14 h-14 text-brand-500/40 animate-spin absolute -inset-0" />
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Analyzing Research Paper
        </h1>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          {statusMessage}
        </p>
      </div>

      {error ? (
        <div className="glass-card rounded-2xl p-6 border border-red-500/40 bg-red-950/20 space-y-4 text-center">
          <div className="w-12 h-12 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">Pipeline Execution Error</h3>
            <p className="text-xs text-red-300 max-w-sm mx-auto">{error}</p>
          </div>
          <div className="pt-2 flex justify-center gap-3">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-semibold"
            >
              Retry Analysis
            </button>
            <button
              onClick={() => navigate('/upload')}
              className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-700"
            >
              Back to Upload
            </button>
          </div>
        </div>
      ) : (
        /* Progress Stepper */
        <div className="glass-card rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-4">
          <div className="space-y-3">
            {PIPELINE_STEPS.map((step) => {
              const isCompleted = step.id < currentStep;
              const isCurrent = step.id === currentStep;

              return (
                <div
                  key={step.id}
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition-all duration-300 ${
                    isCurrent
                      ? 'bg-brand-600/10 border border-brand-500/30'
                      : isCompleted
                      ? 'bg-slate-900/30 text-slate-300'
                      : 'opacity-40 text-slate-500'
                  }`}
                >
                  <div className="mt-0.5">
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-600" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className={`text-xs font-bold ${isCurrent ? 'text-brand-300' : isCompleted ? 'text-white' : 'text-slate-400'}`}>
                      {step.label}
                    </div>
                    <div className="text-[11px] text-slate-400 line-clamp-1">
                      {step.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
