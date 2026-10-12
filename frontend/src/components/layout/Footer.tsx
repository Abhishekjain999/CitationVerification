import React, { useState } from 'react';
import { Shield, Info, ExternalLink } from 'lucide-react';
import { DisclaimerModal } from '../common/DisclaimerModal';

export const Footer: React.FC = () => {
  const [isDisclaimerOpen, setIsDisclaimerOpen] = useState(false);

  return (
    <>
      <footer className="border-t border-slate-800 bg-[#080c14] py-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-lg bg-brand-600 flex items-center justify-center text-white">
                <Shield className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-slate-200">ResearchGuard</span>
              <span className="text-slate-500">|</span>
              <span>AI-Powered Academic Paper & Reference Verification</span>
            </div>

            <div className="flex items-center gap-4 text-slate-400">
              <button
                onClick={() => setIsDisclaimerOpen(true)}
                className="hover:text-white transition flex items-center gap-1"
              >
                <Info className="w-3.5 h-3.5 text-amber-400" />
                <span>Academic Disclaimer</span>
              </button>
              <a
                href="https://openalex.org"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition flex items-center gap-1"
              >
                <span>OpenAlex</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <a
                href="https://crossref.org"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition flex items-center gap-1"
              >
                <span>Crossref</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <a
                href="https://www.semanticscholar.org"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition flex items-center gap-1"
              >
                <span>Semantic Scholar</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
            <p>
              Automated verification engine is designed for decision-support and integrity screening. Always cross-examine findings.
            </p>
            <p>ResearchGuard Academic Systems.</p>
          </div>
        </div>
      </footer>

      <DisclaimerModal isOpen={isDisclaimerOpen} onClose={() => setIsDisclaimerOpen(false)} />
    </>
  );
};
