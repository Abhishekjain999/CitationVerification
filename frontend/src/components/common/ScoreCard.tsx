import React from 'react';
import { LucideIcon } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple' | 'slate';
  badge?: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'slate',
  badge,
}) => {
  const variantStyles = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20 group-hover:border-blue-500/40',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 group-hover:border-emerald-500/40',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20 group-hover:border-amber-500/40',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20 group-hover:border-rose-500/40',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20 group-hover:border-purple-500/40',
    slate: 'bg-slate-800/40 text-slate-300 border-slate-700/50 group-hover:border-slate-600',
  }[variant];

  return (
    <div className="glass-card glass-card-hover rounded-xl p-4 flex flex-col justify-between group">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg border transition-colors ${variantStyles}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-2 flex items-baseline justify-between gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-100">{value}</span>
        {badge && (
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
            {badge}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
