import React from 'react';
import { Search, ArrowUpDown } from 'lucide-react';


interface ReferenceFilterBarProps {
  search: string;
  onSearchChange: (val: string) => void;
  statusFilter: string;
  onStatusFilterChange: (val: string) => void;
  sortBy: string;
  onSortByChange: (val: string) => void;
  counts?: Record<string, number>;
}

export const ReferenceFilterBar: React.FC<ReferenceFilterBarProps> = ({
  search,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  sortBy,
  onSortByChange,
  counts = {},
}) => {
  const filters: { key: string; label: string }[] = [
    { key: 'ALL', label: 'All References' },
    { key: 'VERIFIED', label: 'Verified' },
    { key: 'METADATA_ISSUES', label: 'Metadata Issues' },
    { key: 'POSSIBLE_MATCH', label: 'Possible Match' },
    { key: 'NOT_FOUND', label: 'Not Found' },
    { key: 'INVALID_DOI', label: 'Invalid DOI' },
    { key: 'DUPLICATE', label: 'Duplicate' },
  ];

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title, author, or keyword..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-850/80 border border-slate-700/60 rounded-xl text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition"
          />
        </div>

        {/* Sort selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <ArrowUpDown className="w-3.5 h-3.5" /> Sort:
          </span>
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            className="bg-slate-850 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500 cursor-pointer"
          >
            <option value="number">Reference # (Order in paper)</option>
            <option value="confidence">Confidence (High to Low)</option>
            <option value="status">Verification Status</option>
            <option value="title">Title (A to Z)</option>
          </select>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {filters.map((f) => {
          const isActive = statusFilter === f.key;
          const count = counts[f.key];

          return (
            <button
              key={f.key}
              onClick={() => onStatusFilterChange(f.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 ${
                isActive
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-600/20 font-semibold'
                  : 'bg-slate-850/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              <span>{f.label}</span>
              {typeof count === 'number' && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    isActive ? 'bg-brand-700 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
