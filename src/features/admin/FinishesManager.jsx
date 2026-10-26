import React, { useState } from 'react';
import { Palette, Plus } from 'lucide-react';
import { Badge } from '../../components/Badge.jsx';
import { useCreateFinishMutation, useToggleFinishStatusMutation } from './queries.js';

export const FinishesManager = ({ finishesList = [] }) => {
  const [filterType, setFilterType] = useState('all');
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [name, setName] = useState('');
  const [type, setType] = useState('motor');
  const [colorCode, setColorCode] = useState('#1A1A1A');
  const [sortOrder, setSortOrder] = useState(1);
  const [errorMsg, setErrorMsg] = useState('');

  const createFinishMutation = useCreateFinishMutation();
  const toggleFinishMutation = useToggleFinishStatusMutation();

  const filteredFinishes = finishesList.filter((f) => {
    if (filterType === 'all') return true;
    return f.type === filterType;
  });

  const handleCreateFinish = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setErrorMsg('');

    try {
      const finishId = `${type === 'motor' ? 'mf' : 'bf'}-${name
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')}`;

      const payload = {
        finish_id: finishId,
        name: name.trim(),
        type,
        color_code: colorCode,
        sort_order: Number(sortOrder),
        is_active: true,
      };

      await createFinishMutation.mutateAsync(payload);
      setIsAddOpen(false);
      setName('');
      setColorCode('#1A1A1A');
    } catch (err) {
      console.error('Failed to create finish:', err);
      setErrorMsg(err.message || 'Failed to create finish');
    }
  };

  const handleToggleActive = async (finish) => {
    try {
      await toggleFinishMutation.mutateAsync({
        finishId: finish.finish_id,
        isActive: !finish.is_active,
      });
    } catch (err) {
      console.error('Error toggling finish:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Palette className="w-5 h-5 text-amber-600" />
            <span>Finishes & Materials Registry</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Standard reusable finishes across all motors and aerodynamic blade surfaces
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
            {['all', 'motor', 'blade'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all cursor-pointer ${
                  filterType === t
                    ? 'bg-white text-slate-900 shadow-2xs font-bold'
                    : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsAddOpen(true)}
            className="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Add Finish</span>
          </button>
        </div>
      </div>

      {/* Add Finish Modal */}
      {isAddOpen && (
        <div className="p-5 rounded-2xl bg-amber-50/50 border border-amber-200">
          <h3 className="text-xs font-bold text-amber-950 uppercase tracking-wider mb-3">
            Register New Finish
          </h3>
          <form onSubmit={handleCreateFinish} className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1">Finish Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Weathered Driftwood"
                className="w-full p-2 bg-white border border-slate-200 rounded-xl"
              />
            </div>
            <div>
              <label className="font-bold text-slate-700 block mb-1">Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full p-2 bg-white border border-slate-200 rounded-xl"
              >
                <option value="motor">Motor Finish</option>
                <option value="blade">Blade Finish</option>
              </select>
            </div>
            <div>
              <label className="font-bold text-slate-700 block mb-1">Hex Color</label>
              <div className="flex gap-2">
                <input
                  type="color"
                  value={colorCode}
                  onChange={(e) => setColorCode(e.target.value)}
                  className="w-9 h-8 p-0 border-0 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={colorCode}
                  onChange={(e) => setColorCode(e.target.value)}
                  className="w-full p-2 bg-white border border-slate-200 rounded-xl font-mono text-xs"
                />
              </div>
            </div>
            <div className="flex items-end gap-2">
              <button
                type="submit"
                disabled={createFinishMutation.isPending}
                className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold cursor-pointer disabled:opacity-50"
              >
                {createFinishMutation.isPending ? 'Saving...' : 'Save Finish'}
              </button>
              <button
                type="button"
                onClick={() => setIsAddOpen(false)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 font-bold hover:bg-slate-100 cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </form>
          {errorMsg && <p className="text-xs text-rose-600 mt-2 font-medium">{errorMsg}</p>}
        </div>
      )}

      {/* Finishes Grid Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 border-b border-slate-100 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Swatch</th>
                <th className="py-3 px-4">Finish Name</th>
                <th className="py-3 px-4">Identifier / ID</th>
                <th className="py-3 px-4">Component Type</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredFinishes.map((f) => (
                <tr key={f.finish_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4">
                    <div
                      className="w-8 h-8 rounded-lg border border-slate-200 shadow-2xs"
                      style={{ backgroundColor: f.color_code || '#ccc' }}
                    />
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">{f.name}</td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{f.finish_id}</td>
                  <td className="py-3 px-4">
                    <Badge variant={f.type === 'motor' ? 'default' : 'neutral'} size="xs">
                      {f.type}
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={f.is_active ? 'success' : 'neutral'} size="xs">
                      {f.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleToggleActive(f)}
                      disabled={toggleFinishMutation.isPending}
                      className="text-xs font-semibold text-amber-700 hover:text-amber-800 cursor-pointer disabled:opacity-50"
                    >
                      {f.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
