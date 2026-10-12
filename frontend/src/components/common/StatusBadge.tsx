import React from 'react';
import { VerificationStatus, IssueSeverity } from '../../types';
import { CheckCircle2, AlertTriangle, HelpCircle, XCircle, Copy, AlertOctagon } from 'lucide-react';

interface StatusBadgeProps {
  status: VerificationStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = HelpCircle;
  let label = status;

  if (norm === 'VERIFIED') {
    colorClasses = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    Icon = CheckCircle2;
    label = 'Verified';
  } else if (norm.includes('METADATA')) {
    colorClasses = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = AlertTriangle;
    label = 'Metadata Issues';
  } else if (norm === 'POSSIBLE MATCH') {
    colorClasses = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    Icon = HelpCircle;
    label = 'Possible Match';
  } else if (norm === 'NOT FOUND') {
    colorClasses = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    Icon = XCircle;
    label = 'Not Found';
  } else if (norm === 'INVALID DOI') {
    colorClasses = 'bg-red-500/20 text-red-300 border-red-500/50 font-semibold';
    Icon = AlertOctagon;
    label = 'Invalid DOI';
  } else if (norm === 'DUPLICATE') {
    colorClasses = 'bg-purple-500/10 text-purple-400 border-purple-500/30';
    Icon = Copy;
    label = 'Duplicate';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border transition-all duration-200 ${colorClasses} ${sizeClasses}`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      <span>{label}</span>
    </span>
  );
};

export const SeverityBadge: React.FC<{ severity: IssueSeverity; size?: 'sm' | 'md' }> = ({
  severity,
  size = 'md',
}) => {
  const norm = (severity || 'WARNING').toUpperCase();

  let colorClasses = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  let Icon = AlertTriangle;

  if (norm === 'CRITICAL') {
    colorClasses = 'bg-red-500/20 text-red-400 border-red-500/40 font-semibold';
    Icon = AlertOctagon;
  } else if (norm === 'INFO') {
    colorClasses = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    Icon = HelpCircle;
  }

  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5';

  return (
    <span className={`inline-flex items-center font-medium rounded-md border ${colorClasses} ${sizeClasses}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{norm}</span>
    </span>
  );
};
