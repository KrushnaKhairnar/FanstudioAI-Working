import React from 'react';
import { PackageOpen } from 'lucide-react';

export const NoData = ({
  icon: Icon = PackageOpen,
  title = 'No Data Found',
  description = 'There are no items to display matching your criteria.',
  actionLabel,
  onAction,
  className = '',
}) => {
  return (
    <div className={`p-12 text-center flex flex-col items-center justify-center ${className}`}>
      <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-4 border border-amber-200 shadow-2xs">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-base font-extrabold text-slate-800">{title}</h3>
      <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-sm leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-5 px-4 py-2 rounded-xl bg-slate-900 hover:bg-amber-700 text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
