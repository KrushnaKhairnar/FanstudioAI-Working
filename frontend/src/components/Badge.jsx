import React from 'react';

const VARIANTS = {
  default: 'bg-slate-100 text-slate-700 border-slate-200',
  primary: 'bg-amber-50 text-amber-900 border-amber-200',
  success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  warning: 'bg-amber-100 text-amber-800 border-amber-300',
  danger: 'bg-rose-50 text-rose-800 border-rose-200',
  info: 'bg-blue-50 text-blue-800 border-blue-200',
  dark: 'bg-slate-900 text-white border-slate-800',
  motor: 'bg-slate-100 text-slate-800 border-slate-300',
  blade: 'bg-amber-50 text-amber-900 border-amber-300',
};

const SIZES = {
  xs: 'text-[9px] px-1.5 py-0.5',
  sm: 'text-[10px] px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3 py-1.5',
};

export const Badge = ({
  children,
  variant = 'default',
  size = 'sm',
  className = '',
  dot = false,
  dotColor = null,
}) => {
  const variantClass = VARIANTS[variant] || VARIANTS.default;
  const sizeClass = SIZES[size] || SIZES.sm;

  return (
    <span
      className={`inline-flex items-center gap-1 font-semibold rounded-full border transition-colors ${variantClass} ${sizeClass} ${className}`}
    >
      {dot && (
        <span
          className="w-1.5 h-1.5 rounded-full shrink-0"
          style={{ backgroundColor: dotColor || 'currentColor' }}
        />
      )}
      {children}
    </span>
  );
};
