import React from 'react';
import { ChevronDown } from 'lucide-react';

export const CatalogSearch = ({
  totalResults,
  selectedCategory,
  sortBy,
  onSortChange,
}) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80">
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span>{selectedCategory}</span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-200">
            {totalResults} models
          </span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Precision engineered ceiling fans with custom motor and blade finishes
        </p>
      </div>

      {/* Sorting Dropdown */}
      <div className="flex items-center gap-2 self-start sm:self-auto">
        <span className="text-xs text-slate-500 font-medium">Sort by:</span>
        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="appearance-none bg-white border border-slate-200 rounded-xl px-3 py-1.5 pr-8 text-xs font-semibold text-slate-800 shadow-2xs hover:border-slate-300 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
          >
            <option value="Popular">Popular & Catalog</option>
            <option value="Price: Low to High">Price: Low to High</option>
            <option value="Price: High to Low">Price: High to Low</option>
            <option value="Name: A-Z">Name: A-Z</option>
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>
    </div>
  );
};
