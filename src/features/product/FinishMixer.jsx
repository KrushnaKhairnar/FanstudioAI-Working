import React from 'react';
import { Sparkles, Check, ArrowRight } from 'lucide-react';

export const FinishMixer = ({
  bladeSizes,
  selectedBladeSize,
  onSelectBladeSize,
  fanTypes,
  selectedFanType,
  onSelectFanType,
  motorFinishes,
  selectedMotorId,
  onSelectMotorId,
  bladeFinishes,
  selectedBladeId,
  onSelectBladeId,
  colorsList,
  selectedColorIdx,
  onSelectColorIdx,
  calculatedPrice,
  onOpenVisualizer,
}) => {
  return (
    <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-xs space-y-6">
      {/* 1. Blade Size Options */}
      {bladeSizes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
            Sweep Blade Size
          </label>
          <div className="flex flex-wrap gap-2">
            {bladeSizes.map((size) => (
              <button
                key={size}
                onClick={() => onSelectBladeSize(size)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                  selectedBladeSize === size
                    ? 'border-amber-600 bg-amber-50 text-amber-900 shadow-2xs font-bold ring-1 ring-amber-600'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 bg-white'
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 2. Fan Type Options */}
      {fanTypes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
            Fan Blade Construction
          </label>
          <div className="flex flex-wrap gap-2">
            {fanTypes.map((type) => (
              <button
                key={type}
                onClick={() => onSelectFanType(type)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                  selectedFanType === type
                    ? 'border-amber-600 bg-amber-50 text-amber-900 shadow-2xs font-bold ring-1 ring-amber-600'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 bg-white'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 3. Preset Color Combinations */}
      {colorsList.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
            Designer Combinations
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {colorsList.map((col, idx) => (
              <button
                key={idx}
                onClick={() => onSelectColorIdx(idx)}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                  selectedColorIdx === idx
                    ? 'border-amber-600 bg-amber-50/40 shadow-2xs'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div>
                  <div className="text-xs font-bold text-slate-900">
                    {col.body_color} / {col.blade_color}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    Motor & Blade Harmonized
                  </div>
                </div>
                {selectedColorIdx === idx && (
                  <Check className="w-4 h-4 text-amber-700 shrink-0" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 4. Motor Housing Finishes */}
      {motorFinishes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
            Motor Housing Finish
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {motorFinishes.map((finish) => {
              const isSelected = selectedMotorId === finish.finish_id;
              return (
                <button
                  key={finish.finish_id}
                  onClick={() => onSelectMotorId(finish.finish_id)}
                  className={`p-2.5 rounded-xl border flex items-center gap-2.5 transition-all cursor-pointer text-left ${
                    isSelected
                      ? 'border-amber-600 bg-amber-50/50 shadow-2xs ring-1 ring-amber-600 font-bold'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <span
                    className="w-4 h-4 rounded-full border border-slate-300 shrink-0 shadow-2xs"
                    style={{ backgroundColor: finish.color_code || '#1A1A1A' }}
                  />
                  <span className="text-xs text-slate-800 truncate">{finish.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. Blade Surface Finishes */}
      {bladeFinishes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
            Blade Surface Finish
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {bladeFinishes.map((finish) => {
              const isSelected = selectedBladeId === finish.finish_id;
              return (
                <button
                  key={finish.finish_id}
                  onClick={() => onSelectBladeId(finish.finish_id)}
                  className={`p-2.5 rounded-xl border flex items-center gap-2.5 transition-all cursor-pointer text-left ${
                    isSelected
                      ? 'border-amber-600 bg-amber-50/50 shadow-2xs ring-1 ring-amber-600 font-bold'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <span
                    className="w-4 h-4 rounded-full border border-slate-300 shrink-0 shadow-2xs"
                    style={{ backgroundColor: finish.color_code || '#5F311C' }}
                  />
                  <span className="text-xs text-slate-800 truncate">{finish.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Pricing and Action CTA */}
      <div className="pt-4 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400 block">
            Custom Configured Price
          </span>
          <span className="text-2xl font-black text-slate-900">
            ₹{Number(calculatedPrice).toLocaleString()}
          </span>
        </div>

        <button
          onClick={onOpenVisualizer}
          className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Visualize in My Room</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
