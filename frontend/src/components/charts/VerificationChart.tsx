import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { PaperStatistics } from '../../types';

interface VerificationChartProps {
  stats: PaperStatistics;
}

const COLORS = {
  Verified: '#10b981',        // Emerald
  'Metadata Issues': '#f59e0b',// Amber
  'Possible Match': '#0ea5e9', // Sky
  'Not Found': '#f43f5e',      // Rose
  'Invalid DOI': '#dc2626',    // Red
  Duplicate: '#a855f7',        // Purple
};

export const VerificationChart: React.FC<VerificationChartProps> = ({ stats }) => {
  const data = [
    { name: 'Verified', value: stats.verified_count, color: COLORS.Verified },
    { name: 'Metadata Issues', value: stats.metadata_issues_count, color: COLORS['Metadata Issues'] },
    { name: 'Possible Match', value: stats.possible_matches_count, color: COLORS['Possible Match'] },
    { name: 'Not Found', value: stats.not_found_count, color: COLORS['Not Found'] },
    { name: 'Invalid DOI', value: stats.invalid_doi_count, color: COLORS['Invalid DOI'] },
    { name: 'Duplicate', value: stats.duplicates_count, color: COLORS.Duplicate },
  ].filter((item) => item.value > 0);

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
        No verification data available
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              borderColor: '#334155',
              borderRadius: '0.75rem',
              color: '#f8fafc',
              fontSize: '12px',
            }}
            itemStyle={{ color: '#f8fafc' }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => <span className="text-xs text-slate-300">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
