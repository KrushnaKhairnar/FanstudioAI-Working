import React from 'react';
import { ShieldCheck, Award, Feather, Wrench } from 'lucide-react';

export const ProductSpecs = ({ product }) => {
  const specs = product.specifications || {};

  const specItems = [
    { label: 'Category', value: specs.category || product.category || 'Ceiling Fan' },
    { label: 'Blade Sweep Size', value: specs.sweep_size || '1200mm (48")' },
    { label: 'Blade Count', value: `${specs.blade_count || product.blade_count || 3} Blades` },
    { label: 'Blade Material', value: specs.blade_type || product.blade_type || 'Solid Natural Hardwood' },
    { label: 'Motor Technology', value: specs.motor_type || 'Precision DC / BLDC Inverter' },
    { label: 'Air Delivery', value: specs.air_delivery || '260 CMM' },
    { label: 'Motor Warranty', value: '10 Years Replacement' },
    { label: 'Remote Control', value: '6-Speed Smart RF Remote Included' },
  ];

  return (
    <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
      <div>
        <h3 className="text-base font-extrabold text-slate-900 mb-2">
          Product Overview & Architecture
        </h3>
        <p className="text-sm text-slate-600 leading-relaxed">
          {product.description ||
            `Engineered ${product.name} with aerodynamic airflow, whisper-quiet performance, and premium finishes.`}
        </p>
      </div>

      {/* Feature Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
        <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center gap-2.5">
          <Feather className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <div className="text-xs font-bold text-slate-900">Whisper Quiet</div>
            <div className="text-[10px] text-slate-500">&lt; 32 dB acoustic noise</div>
          </div>
        </div>

        <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center gap-2.5">
          <Award className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <div className="text-xs font-bold text-slate-900">5-Star Energy</div>
            <div className="text-[10px] text-slate-500">65% power saving</div>
          </div>
        </div>

        <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center gap-2.5">
          <ShieldCheck className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <div className="text-xs font-bold text-slate-900">10-Yr Warranty</div>
            <div className="text-[10px] text-slate-500">Full motor warranty</div>
          </div>
        </div>

        <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center gap-2.5">
          <Wrench className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <div className="text-xs font-bold text-slate-900">Easy Mount</div>
            <div className="text-[10px] text-slate-500">Standard & angled ceilings</div>
          </div>
        </div>
      </div>

      {/* Technical Specifications Table */}
      <div className="pt-2">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
          Technical Specifications
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 border-t border-slate-100 pt-3">
          {specItems.map((item, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between py-1.5 border-b border-slate-100/60 text-xs"
            >
              <span className="text-slate-500">{item.label}</span>
              <span className="font-semibold text-slate-800 text-right">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
