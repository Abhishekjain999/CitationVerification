import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from 'recharts';
import { PaperStatistics } from '../../types';

interface ConfidenceChartProps {
  stats: PaperStatistics;
}

export const ConfidenceChart: React.FC<ConfidenceChartProps> = ({ stats }) => {
  const buckets = stats.confidence_distribution || {};

  const data = [
    { range: '90-100%', count: buckets['90-100%'] || 0, color: '#10b981' },
    { range: '70-89%', count: buckets['70-89%'] || 0, color: '#3b82f6' },
    { range: '50-69%', count: buckets['50-69%'] || 0, color: '#f59e0b' },
    { range: '0-49%', count: buckets['0-49%'] || 0, color: '#f43f5e' },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
          <XAxis dataKey="range" stroke="#94a3b8" fontSize={11} />
          <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
          <Tooltip
            cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
            contentStyle={{
              backgroundColor: '#1e293b',
              borderColor: '#334155',
              borderRadius: '0.75rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const SourceDistributionChart: React.FC<{ stats: PaperStatistics }> = ({ stats }) => {
  const sources = stats.sources_distribution || {};

  const data = [
    { name: 'OpenAlex', count: sources['OpenAlex'] || 0, color: '#3b82f6' },
    { name: 'Crossref', count: sources['Crossref'] || 0, color: '#10b981' },
    { name: 'Semantic Scholar', count: sources['Semantic Scholar'] || 0, color: '#8b5cf6' },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
          <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
          <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
          <Tooltip
            cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
            contentStyle={{
              backgroundColor: '#1e293b',
              borderColor: '#334155',
              borderRadius: '0.75rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
