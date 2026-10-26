import React, { useState } from 'react';
import { Upload, X, Layers, RefreshCw, CheckCircle2 } from 'lucide-react';
import {
  useBatchImportMutation,
  useReloadCatalogMutation,
} from './queries.js';

export const BatchImportModal = ({
  isOpen,
  onClose,
  onImportCompleted,
}) => {
  const [jsonText, setJsonText] = useState('');
  const [resultMsg, setResultMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const batchImportMutation = useBatchImportMutation();
  const reloadCatalogMutation = useReloadCatalogMutation();

  if (!isOpen) return null;

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          setJsonText(reader.result);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleExecuteImport = async () => {
    if (!jsonText.trim()) return;
    setResultMsg('');
    setErrorMsg('');

    try {
      const parsed = JSON.parse(jsonText);
      const res = await batchImportMutation.mutateAsync(parsed);
      setResultMsg(`🎉 Successfully processed ${res.count || 'catalog'} products!`);
      if (onImportCompleted) onImportCompleted();
      setTimeout(() => {
        onClose();
        setJsonText('');
        setResultMsg('');
      }, 1400);
    } catch (err) {
      console.error('Batch import error:', err);
      setErrorMsg(err.message || 'Invalid JSON or batch import rejected');
    }
  };

  const handleReloadCatalog = async () => {
    try {
      await reloadCatalogMutation.mutateAsync();
      setResultMsg('🔄 Catalog database reloaded from disk successfully!');
      if (onImportCompleted) onImportCompleted();
    } catch (err) {
      setErrorMsg('Failed to reload catalog: ' + err.message);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-3xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center border border-amber-200">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-900">Batch Import Catalog</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Bulk upsert products, variants, and finishes from JSON
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4 text-xs">
          {resultMsg && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{resultMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 font-semibold">
              {errorMsg}
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700">Paste JSON Content</span>
            <label className="text-xs text-amber-700 hover:text-amber-800 font-bold flex items-center gap-1.5 cursor-pointer">
              <Upload className="w-4 h-4" />
              <span>Load JSON File</span>
              <input type="file" accept=".json,application/json" onChange={handleFileSelect} className="hidden" />
            </label>
          </div>

          <textarea
            rows="10"
            value={jsonText}
            onChange={(e) => setJsonText(e.target.value)}
            placeholder='[&#10;  {&#10;    "fanCode": "AIREX_8_BLADES",&#10;    "fanName": "AIREX 8 BLADES",&#10;    "productId": "FAN-0001",&#10;    "variants": [...],&#10;    "colors": [...]&#10;  }&#10;]'
            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono text-[11px] text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />

          <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
            <button
              type="button"
              onClick={handleReloadCatalog}
              disabled={reloadCatalogMutation.isPending}
              className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1.5 font-semibold cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reloadCatalogMutation.isPending ? 'animate-spin' : ''}`} />
              <span>Reload from data/catalog.json</span>
            </button>

            <button
              type="button"
              onClick={handleExecuteImport}
              disabled={batchImportMutation.isPending || !jsonText.trim()}
              className="w-full sm:w-auto px-6 py-2.5 rounded-2xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              {batchImportMutation.isPending ? 'Processing...' : 'Execute Batch Import'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
