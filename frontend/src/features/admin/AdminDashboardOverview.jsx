import React from 'react';
import { Package, Palette, Layers, Database } from 'lucide-react';
import { useMongoStatusQuery } from './queries.js';

export const AdminDashboardOverview = ({ productsCount = 0, finishesCount = 0 }) => {
  const { data: mongoStatus } = useMongoStatusQuery();

  const engineName = mongoStatus?.engine === 'mongodb_native' ? 'MongoDB Native' : 'MongoDB';
  const engineDesc = mongoStatus?.status === 'connected' ? 'Connected & Synced' : 'File-backed JSON Store & PyMongo';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-2xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Total Products
          </span>
          <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
            <Package className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 text-2xl font-black text-slate-900">{productsCount}</div>
        <div className="text-[10px] text-slate-400 mt-1">Catalog Fan Models</div>
      </div>

      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-2xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Custom Finishes
          </span>
          <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
            <Palette className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 text-2xl font-black text-slate-900">{finishesCount}</div>
        <div className="text-[10px] text-slate-400 mt-1">Motors & Blade Materials</div>
      </div>

      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-2xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Database Engine
          </span>
          <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Database className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 text-lg font-black text-emerald-700">{engineName}</div>
        <div className="text-[10px] text-slate-400 mt-1">{engineDesc}</div>
      </div>

      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-2xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            AI Computer Vision
          </span>
          <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center">
            <Layers className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 text-lg font-black text-purple-700">OpenCV Ready</div>
        <div className="text-[10px] text-slate-400 mt-1">Ceiling Anchor & Harmonization</div>
      </div>
    </div>
  );
};
