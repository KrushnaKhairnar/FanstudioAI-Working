import React, { useState } from 'react';
import { Layers, Upload, RefreshCw, CheckCircle2 } from 'lucide-react';
import {
  useBatchImportMutation,
  useReloadCatalogMutation,
} from '../../features/admin/queries.js';

export const AdminImportPage = () => {
  const [jsonText, setJsonText] = useState('');
  const [resultMsg, setResultMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const batchImportMutation = useBatchImportMutation();
  const reloadCatalogMutation = useReloadCatalogMutation();

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
      setResultMsg(`🎉 Successfully processed ${res.count || 'catalog'} products into the database!`);
    } catch (err) {
      console.error('Batch import error:', err);
      setErrorMsg(err.message || 'Invalid JSON format or batch import rejected');
    }
  };

  const handleReloadCatalog = async () => {
    try {
      await reloadCatalogMutation.mutateAsync();
      setResultMsg('🔄 Catalog database reloaded from disk data/catalog.json successfully!');
    } catch (err) {
      setErrorMsg('Failed to reload catalog: ' + err.message);
    }
  };

  return (
    <div className="p-6 sm:p-8 space-y-6 max-w-4xl">
      <div>
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Layers className="w-5 h-5 text-amber-600" />
          <span>Batch Import & Database Synchronization</span>
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Bulk import catalog JSON documents or trigger hot-reloading from data/catalog.json
        </p>
      </div>

      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs space-y-5">
        {resultMsg && (
          <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{resultMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
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
          rows="14"
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          placeholder='[&#10;  {&#10;    "fanCode": "AIREX_8_BLADES",&#10;    "fanName": "AIREX 8 BLADES",&#10;    "productId": "FAN-0001",&#10;    "variants": [...],&#10;    "colors": [...]&#10;  }&#10;]'
          className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl font-mono text-[11px] text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
        />

        <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            type="button"
            onClick={handleReloadCatalog}
            disabled={reloadCatalogMutation.isPending}
            className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1.5 font-semibold cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reloadCatalogMutation.isPending ? 'animate-spin' : ''}`} />
            <span>Reload live database from data/catalog.json</span>
          </button>

          <button
            type="button"
            onClick={handleExecuteImport}
            disabled={batchImportMutation.isPending || !jsonText.trim()}
            className="w-full sm:w-auto px-6 py-2.5 rounded-2xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            {batchImportMutation.isPending ? 'Processing Batch Import...' : 'Execute Batch Import'}
          </button>
        </div>
      </div>
    </div>
  );
};
