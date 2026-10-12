import React from 'react';
import { HealthRating, ScoreBreakdown } from '../../types';
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

interface HealthGaugeProps {
  score: number;
  rating: HealthRating;
  breakdown?: ScoreBreakdown;
  size?: 'sm' | 'md' | 'lg';
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({
  score,
  rating,
  breakdown,
  size = 'md',
}) => {
  const cleanScore = Math.min(100, Math.max(0, Math.round(score)));
  const incomplete = rating === 'Inconclusive' || rating === 'Pending';

  let strokeColor = '#10b981'; // green
  let textColor = 'text-emerald-400';
  let badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let Icon = ShieldCheck;

  if (cleanScore < 50) {
    strokeColor = '#ef4444'; // red
    textColor = 'text-red-400';
    badgeColor = 'bg-red-500/10 text-red-400 border-red-500/30';
    Icon = ShieldAlert;
  } else if (cleanScore < 70) {
    strokeColor = '#f59e0b'; // amber
    textColor = 'text-amber-400';
    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = ShieldAlert;
  } else if (cleanScore < 85) {
    strokeColor = '#3b82f6'; // blue
    textColor = 'text-blue-400';
    badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    Icon = Shield;
  }
  if (incomplete) {
    strokeColor = '#94a3b8';
    textColor = 'text-slate-300';
    badgeColor = 'bg-slate-800 text-slate-300 border-slate-600';
    Icon = Shield;
  }

  // SVG parameters
  const radius = size === 'lg' ? 64 : size === 'md' ? 48 : 36;
  const strokeWidth = size === 'lg' ? 9 : size === 'md' ? 7 : 5;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (cleanScore / 100) * circumference;
  const viewBoxSize = (radius + strokeWidth) * 2;

  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center justify-center">
        <svg
          width={radius * 2 + strokeWidth * 2}
          height={radius * 2 + strokeWidth * 2}
          viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
          className="transform -rotate-90 drop-shadow-md"
        >
          {/* Background circle */}
          <circle
            cx={viewBoxSize / 2}
            cy={viewBoxSize / 2}
            r={radius}
            fill="transparent"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={viewBoxSize / 2}
            cy={viewBoxSize / 2}
            r={radius}
            fill="transparent"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className={`font-extrabold tracking-tight ${size === 'lg' ? 'text-3xl' : size === 'md' ? 'text-2xl' : 'text-lg'} ${textColor}`}>
            {incomplete ? '—' : cleanScore}
          </span>
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
            / 100
          </span>
        </div>
      </div>

      <div className="mt-3 flex flex-col items-center gap-1.5">
        <div className={`inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full border text-xs font-semibold ${badgeColor}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{rating === 'Pending' ? 'Analyzing' : incomplete ? 'Verification incomplete' : rating === 'Poor' ? 'Needs review' : rating}</span>
        </div>
        <p className="text-[11px] text-slate-400 text-center max-w-[200px]">
          {incomplete ? 'Insufficient evidence to rate this paper' : 'Reference health score — review aid'}
        </p>
      </div>

      {breakdown && (
        <div className="mt-4 w-full grid grid-cols-2 gap-2 text-[11px] text-slate-300">
          <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50">
            <div className="text-slate-400">Verification</div>
            <div className="font-semibold text-slate-200">{breakdown.verification_score}/40 pts</div>
          </div>
          <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50">
            <div className="text-slate-400">Metadata</div>
            <div className="font-semibold text-slate-200">{breakdown.metadata_score}/20 pts</div>
          </div>
          <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50">
            <div className="text-slate-400">Coverage</div>
            <div className="font-semibold text-slate-200">{breakdown.coverage_score}/15 pts</div>
          </div>
          <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50">
            <div className="text-slate-400">Consistency</div>
            <div className="font-semibold text-slate-200">{breakdown.consistency_score}/15 pts</div>
          </div>
        </div>
      )}
    </div>
  );
};
