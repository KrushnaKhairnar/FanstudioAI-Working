import React from 'react';
import { SlidersHorizontal, RotateCcw, Check } from 'lucide-react';

const MOTOR_COLOR_MAP = {
  'Matt Grey': '#808080',
  'Metallic Grey': '#808080',
  'Matt Black': '#1A1A1A',
  'Matt White': '#F3F4F6',
  'Antique Bronze': '#8B7355',
  'Champagne Gold': '#D4AF37',
  'Brass': '#C5A059',
  'Walnut': '#5C4033',
  'Teak': '#B3672B',
  'Oriental Ash': '#D7B88C',
};

const BLADE_COLOR_MAP = {
  'Teak Wooden': '#C27E38',
  'Rosewood Wooden': '#5F311C',
  'Walnut Wooden': '#996933',
  'Natural Wood': '#BA9962',
  'Cane Weave': '#D2A66C',
  'Matt Black': '#1A1A1A',
  'Matt White': '#F3F4F6',
  'Oriental Ash': '#D7B88C',
};

export const CatalogFilters = ({
  selectedCategory,
  onSelectCategory,
  dynamicCategories,
  selectedBladeCounts,
  onToggleBladeCount,
  dynamicBladeCounts,
  selectedMotorColor,
  onSelectMotorColor,
  dynamicMotorColors,
  selectedBladeColor,
  onSelectBladeColor,
  dynamicBladeColors,
  priceMax,
  onChangePriceMax,
  onResetFilters,
}) => {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-amber-600" />
          <h2 className="font-bold text-sm text-slate-900 uppercase tracking-wide">
            Filter Catalog
          </h2>
        </div>
        <button
          onClick={onResetFilters}
          className="text-xs text-slate-400 hover:text-amber-800 flex items-center gap-1 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* 1. Category Filter */}
      <div>
        <label className="text-xs font-bold text-slate-800 block mb-2.5">Category</label>
        <div className="space-y-1">
          {dynamicCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => onSelectCategory(cat)}
              className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer flex items-center justify-between ${
                selectedCategory === cat
                  ? 'bg-amber-50 text-amber-900 font-bold border border-amber-200/60'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <span>{cat}</span>
              {selectedCategory === cat && <Check className="w-3.5 h-3.5 text-amber-700" />}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Blade Count */}
      <div>
        <label className="text-xs font-bold text-slate-800 block mb-2.5">Blade Count</label>
        <div className="grid grid-cols-2 gap-1.5">
          {dynamicBladeCounts.map(({ count, total }) => {
            const isChecked = selectedBladeCounts.includes(count);
            return (
              <button
                key={count}
                onClick={() => onToggleBladeCount(count)}
                className={`px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center justify-between cursor-pointer ${
                  isChecked
                    ? 'bg-amber-600 text-white border-amber-600 shadow-2xs font-bold'
                    : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
                }`}
              >
                <span>{count} Blades</span>
                <span className={`text-[10px] ${isChecked ? 'text-amber-100' : 'text-slate-400'}`}>
                  {total}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Motor Finish Swatches */}
      <div>
        <label className="text-xs font-bold text-slate-800 block mb-2.5">
          Motor Housing Finish
        </label>
        <div className="flex flex-wrap gap-1.5">
          {dynamicMotorColors.map((colorName) => {
            const isSelected = selectedMotorColor === colorName;
            const hex = MOTOR_COLOR_MAP[colorName] || '#1A1A1A';
            return (
              <button
                key={colorName}
                onClick={() => onSelectMotorColor(isSelected ? null : colorName)}
                title={colorName}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] border transition-all cursor-pointer ${
                  isSelected
                    ? 'border-amber-700 bg-amber-50 text-amber-900 font-bold ring-1 ring-amber-700'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 bg-white'
                }`}
              >
                <span
                  className="w-3 h-3 rounded-full border border-slate-300 shadow-2xs"
                  style={{ backgroundColor: hex }}
                />
                <span className="truncate max-w-[90px]">{colorName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. Blade Finish Swatches */}
      <div>
        <label className="text-xs font-bold text-slate-800 block mb-2.5">
          Blade Surface Finish
        </label>
        <div className="flex flex-wrap gap-1.5">
          {dynamicBladeColors.map((colorName) => {
            const isSelected = selectedBladeColor === colorName;
            const hex = BLADE_COLOR_MAP[colorName] || '#5F311C';
            return (
              <button
                key={colorName}
                onClick={() => onSelectBladeColor(isSelected ? null : colorName)}
                title={colorName}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] border transition-all cursor-pointer ${
                  isSelected
                    ? 'border-amber-700 bg-amber-50 text-amber-900 font-bold ring-1 ring-amber-700'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300 bg-white'
                }`}
              >
                <span
                  className="w-3 h-3 rounded-full border border-slate-300 shadow-2xs"
                  style={{ backgroundColor: hex }}
                />
                <span className="truncate max-w-[90px]">{colorName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 5. Price Max Slider */}
      <div className="pt-2 border-t border-slate-100">
        <div className="flex items-center justify-between text-xs font-bold text-slate-800 mb-2">
          <span>Max Price</span>
          <span className="text-amber-700 font-extrabold">₹{priceMax.toLocaleString()}</span>
        </div>
        <input
          type="range"
          min="8000"
          max="35000"
          step="1000"
          value={priceMax}
          onChange={(e) => onChangePriceMax(Number(e.target.value))}
          className="w-full accent-amber-600 cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-slate-400 mt-1">
          <span>₹8,000</span>
          <span>₹35,000</span>
        </div>
      </div>
    </div>
  );
};
