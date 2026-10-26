import React from 'react';
import { useShallow } from 'zustand/react/shallow';
import { Upload, Check } from 'lucide-react';
import { FanGraphic } from '../../components/FanGraphic.jsx';
import { useVisualizerStore } from './store.js';

export const VisualizerFanSelector = ({
  roomList,
  onUploadRoom,
  isUploadingRoom,
  products = [],
  selectedProduct,
  finishes = [],
}) => {
  const {
    selectedRoomId,
    selectedMotorId,
    selectedBladeId,
    setSelectedRoom,
    setSelectedMotorId,
    setSelectedBladeId,
    setSelectedProductCode,
  } = useVisualizerStore(
    useShallow((s) => ({
      selectedRoomId: s.selectedRoomId,
      selectedMotorId: s.selectedMotorId,
      selectedBladeId: s.selectedBladeId,
      setSelectedRoom: s.setSelectedRoom,
      setSelectedMotorId: s.setSelectedMotorId,
      setSelectedBladeId: s.setSelectedBladeId,
      setSelectedProductCode: s.setSelectedProductCode,
    }))
  );

  const motorFinishes = finishes.filter((f) => f.type === 'motor');
  const bladeFinishes = finishes.filter((f) => f.type === 'blade');

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-6">
      {/* 1. Room Photos & Custom Upload */}
      <div>
        <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
          Select Room Photo
        </label>
        <div className="grid grid-cols-4 gap-2">
          {roomList.map((room) => (
            <button
              key={room.id}
              onClick={() => setSelectedRoom(room)}
              className={`h-16 rounded-xl overflow-hidden border-2 transition-all cursor-pointer relative group ${
                selectedRoomId === room.id
                  ? 'border-amber-600 shadow-xs ring-2 ring-amber-500/20'
                  : 'border-slate-200 hover:border-slate-300 opacity-80 hover:opacity-100'
              }`}
            >
              <img src={room.imageUrl} alt={room.name} className="w-full h-full object-cover" />
              {selectedRoomId === room.id && (
                <div className="absolute top-1 right-1 w-3.5 h-3.5 rounded-full bg-amber-600 text-white flex items-center justify-center">
                  <Check className="w-2 h-2" />
                </div>
              )}
            </button>
          ))}

          {/* Upload Button */}
          <label className="h-16 rounded-xl border-2 border-dashed border-slate-300 hover:border-amber-500 bg-slate-50 hover:bg-amber-50/30 flex flex-col items-center justify-center text-slate-500 hover:text-amber-800 transition-all cursor-pointer">
            <Upload className="w-4 h-4 mb-0.5" />
            <span className="text-[10px] font-semibold">
              {isUploadingRoom ? 'Uploading...' : 'Upload'}
            </span>
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) onUploadRoom(e.target.files[0]);
              }}
            />
          </label>
        </div>
      </div>

      {/* 2. Fan Model Selector */}
      <div>
        <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2.5">
          Select Fan Model
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-56 overflow-y-auto pr-1">
          {products.slice(0, 18).map((fan) => {
            const isSelected = selectedProduct?.product_id === fan.product_id;
            const rawImg = fan.primary_image_url || fan.imagePath || (fan.images && fan.images[0]);
            const fanImg = rawImg ? (rawImg.startsWith('http') ? rawImg : `/${rawImg.replace(/^\//, '')}`) : null;

            return (
              <button
                key={fan.product_id}
                onClick={() => setSelectedProductCode(fan.product_id || fan.productId)}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'border-amber-600 bg-amber-50/40 shadow-xs ring-1 ring-amber-600'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div className="h-14 flex items-center justify-center">
                  {fanImg ? (
                    <img src={fanImg} alt={fan.name} className="h-full object-contain" />
                  ) : (
                    <div className="w-12 h-12">
                      <FanGraphic
                        bladeCount={fan.blade_count || 3}
                        bladeColor="#5F311C"
                        motorColor="#1A1A1A"
                      />
                    </div>
                  )}
                </div>
                <div className="mt-1.5">
                  <div className="text-xs font-bold text-slate-900 truncate">{fan.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    {fan.product_code || fan.fanCode}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Motor Finish Selector */}
      {motorFinishes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
            Motor Finish
          </label>
          <div className="flex flex-wrap gap-1.5">
            {motorFinishes.map((f) => (
              <button
                key={f.finish_id}
                onClick={() => setSelectedMotorId(f.finish_id)}
                className={`px-2.5 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  selectedMotorId === f.finish_id
                    ? 'border-amber-600 bg-amber-50 text-amber-900 font-bold shadow-2xs'
                    : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span
                  className="w-3 h-3 rounded-full border border-slate-300 shadow-2xs"
                  style={{ backgroundColor: f.color_code || '#ccc' }}
                />
                <span>{f.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 4. Blade Finish Selector */}
      {bladeFinishes.length > 0 && (
        <div>
          <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block mb-2">
            Blade Surface Material
          </label>
          <div className="flex flex-wrap gap-1.5">
            {bladeFinishes.map((f) => (
              <button
                key={f.finish_id}
                onClick={() => setSelectedBladeId(f.finish_id)}
                className={`px-2.5 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-2 cursor-pointer transition-colors ${
                  selectedBladeId === f.finish_id
                    ? 'border-amber-600 bg-amber-50 text-amber-900 font-bold shadow-2xs'
                    : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span
                  className="w-3 h-3 rounded-full border border-slate-300 shadow-2xs"
                  style={{ backgroundColor: f.color_code || '#ccc' }}
                />
                <span>{f.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
