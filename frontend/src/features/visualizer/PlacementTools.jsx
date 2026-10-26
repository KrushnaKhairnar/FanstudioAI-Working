import React from 'react';
import { useShallow } from 'zustand/react/shallow';
import { Sparkles, Sliders, RotateCcw, Loader2, CheckCircle2 } from 'lucide-react';
import { useVisualizerStore } from './store.js';

export const PlacementTools = ({ onRenderAI }) => {
  const {
    scale,
    setScale,
    rotation,
    setRotation,
    brightness,
    setBrightness,
    colorTemp,
    setColorTemp,
    applyShadow,
    setApplyShadow,
    resetPlacement,
    jobStatus,
    renderTimeMs,
    errorMessage,
  } = useVisualizerStore(
    useShallow((s) => ({
      scale: s.scale,
      setScale: s.setScale,
      rotation: s.rotation,
      setRotation: s.setRotation,
      brightness: s.brightness,
      setBrightness: s.setBrightness,
      colorTemp: s.colorTemp,
      setColorTemp: s.setColorTemp,
      applyShadow: s.applyShadow,
      setApplyShadow: s.setApplyShadow,
      resetPlacement: s.resetPlacement,
      jobStatus: s.jobStatus,
      renderTimeMs: s.renderTimeMs,
      errorMessage: s.errorMessage,
    }))
  );

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-amber-600" />
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Perspective & Lighting Tools
          </h3>
        </div>
        <button
          onClick={resetPlacement}
          className="text-xs text-slate-400 hover:text-amber-800 flex items-center gap-1 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* Scale Slider */}
      <div>
        <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
          <span>Fan Size / Distance</span>
          <span className="text-amber-700 font-bold">{Math.round(scale * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.05"
          value={scale}
          onChange={(e) => setScale(parseFloat(e.target.value))}
          className="w-full accent-amber-600 cursor-pointer"
        />
      </div>

      {/* Rotation Slider */}
      <div>
        <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
          <span>Blade Angle / Orientation</span>
          <span className="text-amber-700 font-bold">{rotation}°</span>
        </div>
        <input
          type="range"
          min="-180"
          max="180"
          step="5"
          value={rotation}
          onChange={(e) => setRotation(parseInt(e.target.value, 10))}
          className="w-full accent-amber-600 cursor-pointer"
        />
      </div>

      {/* Brightness Adjustment */}
      <div>
        <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
          <span>Room Ambient Brightness</span>
          <span className="text-amber-700 font-bold">{Math.round(brightness * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.4"
          max="1.3"
          step="0.05"
          value={brightness}
          onChange={(e) => setBrightness(parseFloat(e.target.value))}
          className="w-full accent-amber-600 cursor-pointer"
        />
      </div>

      {/* Color Temperature (Warm to Daylight) */}
      <div>
        <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
          <span>Lighting Temperature</span>
          <span className="text-amber-700 font-bold">{colorTemp}K</span>
        </div>
        <input
          type="range"
          min="2700"
          max="6500"
          step="100"
          value={colorTemp}
          onChange={(e) => setColorTemp(parseInt(e.target.value, 10))}
          className="w-full accent-amber-600 cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
          <span>Warm (2700K)</span>
          <span>Daylight (6500K)</span>
        </div>
      </div>

      {/* Shadow Toggle */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-700">Ceiling Drop Shadow</span>
        <button
          type="button"
          onClick={() => setApplyShadow(!applyShadow)}
          className={`w-10 h-6 rounded-full p-1 transition-colors cursor-pointer flex items-center ${
            applyShadow ? 'bg-amber-600 justify-end' : 'bg-slate-200 justify-start'
          }`}
        >
          <span className="w-4 h-4 rounded-full bg-white shadow-xs" />
        </button>
      </div>

      {/* Error Notice */}
      {errorMessage && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
          {errorMessage}
        </div>
      )}

      {/* Render AI Action Button */}
      <div className="pt-2 border-t border-slate-100">
        <button
          onClick={onRenderAI}
          disabled={jobStatus === 'PROCESSING'}
          className={`w-full py-3.5 px-4 rounded-2xl font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer ${
            jobStatus === 'PROCESSING'
              ? 'bg-amber-400 text-amber-950 cursor-not-allowed'
              : 'bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white shadow-amber-600/20 hover:shadow-lg'
          }`}
        >
          {jobStatus === 'PROCESSING' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Rendering Computer Vision Composite...</span>
            </>
          ) : jobStatus === 'SUCCESS' ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              <span>Re-render AI Composite {renderTimeMs ? `(${renderTimeMs}ms)` : ''}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Render AI Photorealistic Composite</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
