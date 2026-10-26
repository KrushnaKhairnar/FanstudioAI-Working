import React from 'react';
import { useShallow } from 'zustand/react/shallow';
import { Eye, EyeOff, Download } from 'lucide-react';
import { useVisualizerStore } from './store.js';

export const BeforeAfterView = () => {
  const {
    renderedImageUrl,
    showComparison,
    setShowComparison,
    compareSplit,
    setCompareSplit,
  } = useVisualizerStore(
    useShallow((s) => ({
      renderedImageUrl: s.renderedImageUrl,
      showComparison: s.showComparison,
      setShowComparison: s.setShowComparison,
      compareSplit: s.compareSplit,
      setCompareSplit: s.setCompareSplit,
    }))
  );

  if (!renderedImageUrl) return null;

  return (
    <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-3 w-full sm:w-auto">
        <button
          onClick={() => setShowComparison(!showComparison)}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-colors flex items-center gap-1.5 cursor-pointer ${
            showComparison
              ? 'bg-amber-600 text-white border-amber-600'
              : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
          }`}
        >
          {showComparison ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
          <span>{showComparison ? 'Exit Split Compare' : 'Before / After Compare'}</span>
        </button>

        {showComparison && (
          <div className="flex items-center gap-2 flex-1 sm:w-48">
            <span className="text-[10px] text-slate-400 font-bold uppercase">Before</span>
            <input
              type="range"
              min="0"
              max="100"
              value={compareSplit}
              onChange={(e) => setCompareSplit(parseInt(e.target.value, 10))}
              className="w-full accent-amber-600 cursor-pointer"
            />
            <span className="text-[10px] text-slate-400 font-bold uppercase">After</span>
          </div>
        )}
      </div>

      <a
        href={renderedImageUrl}
        download="fanstudio-ai-room.jpg"
        target="_blank"
        rel="noreferrer"
        className="px-4 py-1.5 rounded-xl bg-slate-900 hover:bg-amber-700 text-white text-xs font-bold transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs self-end sm:self-auto"
      >
        <Download className="w-3.5 h-3.5" />
        <span>Download Composite</span>
      </a>
    </div>
  );
};
