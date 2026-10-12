import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FileText, Shield, Sparkles, Upload, Info } from 'lucide-react';
import { DisclaimerModal } from '../common/DisclaimerModal';
import { api } from '../../services/api';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDisclaimerOpen, setIsDisclaimerOpen] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleLoadDemo = async () => {
    try {
      setLoadingDemo(true);
      const demoPaper = await api.loadDemoPaper();
      navigate(`/papers/${demoPaper.id}`);
    } catch (err) {
      console.error('Failed to load demo:', err);
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#0b0f19]/85 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo and Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-indigo-500 shadow-lg shadow-brand-700/25 p-0.5 group-hover:scale-105 transition-transform duration-200">
              <div className="w-full h-full bg-[#0b0f19] rounded-[10px] flex items-center justify-center">
                <div className="relative flex items-center justify-center">
                  <Shield className="w-5 h-5 text-brand-400" />
                  <FileText className="w-3 h-3 text-indigo-300 absolute" />
                </div>
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-white group-hover:text-brand-300 transition-colors">
                  ResearchGuard
                </span>
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                  AI v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 tracking-wide">
                Scholarly Paper & Citation Verification
              </p>
            </div>
          </Link>

          {/* Navigation Items */}
          <nav className="hidden md:flex items-center gap-1.5">
            <Link
              to="/upload"
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                location.pathname === '/upload'
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              Upload Paper
            </Link>
            <Link
              to="/papers"
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                location.pathname === '/papers'
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              All Papers
            </Link>
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsDisclaimerOpen(true)}
              className="p-2 rounded-lg text-slate-400 hover:text-amber-400 hover:bg-slate-800/60 transition border border-transparent hover:border-slate-700"
              title="Academic Disclaimer & Verification Guide"
            >
              <Info className="w-4 h-4" />
            </button>

            <button
              onClick={handleLoadDemo}
              disabled={loadingDemo}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 transition shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>{loadingDemo ? 'Loading Demo...' : 'Try Demo'}</span>
            </button>

            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 shadow-md shadow-brand-600/30 transition duration-150"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Analyze PDF</span>
            </Link>
          </div>
        </div>
      </header>

      <DisclaimerModal isOpen={isDisclaimerOpen} onClose={() => setIsDisclaimerOpen(false)} />
    </>
  );
};
