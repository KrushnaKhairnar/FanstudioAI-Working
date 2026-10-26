import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateProductMutation } from './queries.js';

export const ProductForm = ({
  isOpen,
  onClose,
  finishesList = [],
}) => {
  const [name, setName] = useState('');
  const [productCode, setProductCode] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Ceiling');
  const [bladeCount, setBladeCount] = useState(3);
  const [bladeType, setBladeType] = useState('Aerodynamic Timber Blade');
  const [motorType, setMotorType] = useState('BLDC Inverter');
  const [basePrice, setBasePrice] = useState(14999);

  const [selectedMotorIds, setSelectedMotorIds] = useState([]);
  const [selectedBladeIds, setSelectedBladeIds] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  const createProductMutation = useCreateProductMutation();

  if (!isOpen) return null;

  const motorFinishes = finishesList.filter((f) => f.type === 'motor');
  const bladeFinishes = finishesList.filter((f) => f.type === 'blade');

  const toggleMotorFinish = (id) => {
    setSelectedMotorIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const toggleBladeFinish = (id) => {
    setSelectedBladeIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !productCode.trim()) {
      setErrorMsg('Please enter Product Name and Product Code');
      return;
    }

    setErrorMsg('');

    try {
      const payload = {
        name: name.trim(),
        product_code: productCode.trim().toUpperCase(),
        fanName: name.trim(),
        fanCode: productCode.trim().toUpperCase(),
        description: description.trim(),
        status: 'active',
        base_price: Number(basePrice),
        price: Number(basePrice),
        motor_finish_ids: selectedMotorIds.length > 0 ? selectedMotorIds : ['mf-matt-black'],
        blade_finish_ids: selectedBladeIds.length > 0 ? selectedBladeIds : ['bf-rosewood'],
        specifications: {
          category,
          blade_count: Number(bladeCount),
          blade_type: bladeType,
          motor_type: motorType,
          sweep_size: '1200mm',
          air_delivery: '260 CMM',
        },
      };

      await createProductMutation.mutateAsync(payload);
      onClose();
    } catch (err) {
      console.error('Create product error:', err);
      setErrorMsg(err.message || 'Failed to create product');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-extrabold text-slate-900">Add New Fan Product</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Register a manufactured ceiling fan in the database
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
              {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Fan Model Name *</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Aerolux Horizon Prime"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Product Code / SKU *</label>
              <input
                type="text"
                required
                value={productCode}
                onChange={(e) => setProductCode(e.target.value)}
                placeholder="e.g. FAN-HORIZON-01"
                className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500 uppercase"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
            <textarea
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="High-efficiency BLDC motor with hand-balanced sculpted timber blades."
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">Category</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">Blade Count</label>
              <input
                type="number"
                min="2"
                max="8"
                value={bladeCount}
                onChange={(e) => setBladeCount(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">Motor Type</label>
              <input
                type="text"
                value={motorType}
                onChange={(e) => setMotorType(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">Base Price (₹)</label>
              <input
                type="number"
                value={basePrice}
                onChange={(e) => setBasePrice(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Offered Motor Finishes</label>
            <div className="flex flex-wrap gap-2">
              {motorFinishes.map((f) => (
                <button
                  type="button"
                  key={f.finish_id}
                  onClick={() => toggleMotorFinish(f.finish_id)}
                  className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 cursor-pointer transition-colors ${
                    selectedMotorIds.includes(f.finish_id)
                      ? 'border-amber-600 bg-amber-50 text-amber-900'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span
                    className="w-3 h-3 rounded-full border border-slate-300"
                    style={{ backgroundColor: f.color_code || '#ccc' }}
                  />
                  <span>{f.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">Offered Blade Finishes</label>
            <div className="flex flex-wrap gap-2">
              {bladeFinishes.map((f) => (
                <button
                  type="button"
                  key={f.finish_id}
                  onClick={() => toggleBladeFinish(f.finish_id)}
                  className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 cursor-pointer transition-colors ${
                    selectedBladeIds.includes(f.finish_id)
                      ? 'border-amber-600 bg-amber-50 text-amber-900'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span
                    className="w-3 h-3 rounded-full border border-slate-300"
                    style={{ backgroundColor: f.color_code || '#ccc' }}
                  />
                  <span>{f.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createProductMutation.isPending}
              className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              {createProductMutation.isPending ? 'Saving...' : 'Create Fan Model'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
