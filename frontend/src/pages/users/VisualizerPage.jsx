import React, { useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { useVisualizer } from '../../features/visualizer/useVisualizer.js';
import { useVisualizerStore } from '../../features/visualizer/store.js';
import { RoomCanvas } from '../../features/visualizer/RoomCanvas.jsx';
import { PlacementTools } from '../../features/visualizer/PlacementTools.jsx';
import { VisualizerFanSelector } from '../../features/visualizer/VisualizerFanSelector.jsx';
import { BeforeAfterView } from '../../features/visualizer/BeforeAfterView.jsx';

export const VisualizerPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const queryProductId = searchParams.get('product');
  const queryMotorId = searchParams.get('motor');
  const queryBladeId = searchParams.get('blade');

  const resetVisualizer = useVisualizerStore((s) => s.resetVisualizer);

  const {
    products,
    finishes,
    selectedProduct,
    selectedMotorId,
    selectedBladeId,
    roomList,
    isUploadingRoom,
    handleUploadRoom,
    handleRenderAI,
  } = useVisualizer({
    initialProductCode: queryProductId,
    initialMotorFinishId: queryMotorId,
    initialBladeFinishId: queryBladeId,
  });

  // Reset visualizer store state when navigating away from visualizer page
  useEffect(() => {
    return () => {
      resetVisualizer();
    };
  }, [resetVisualizer]);

  // Keep shareable URL query parameters in sync with visualizer selection
  useEffect(() => {
    const code = selectedProduct?.product_id || selectedProduct?.productId;
    if (code) {
      const currentCode = searchParams.get('product');
      const currentMotor = searchParams.get('motor');
      const currentBlade = searchParams.get('blade');

      if (
        currentCode !== code ||
        currentMotor !== (selectedMotorId || null) ||
        currentBlade !== (selectedBladeId || null)
      ) {
        const nextParams = new URLSearchParams();
        nextParams.set('product', code);
        if (selectedMotorId) nextParams.set('motor', selectedMotorId);
        if (selectedBladeId) nextParams.set('blade', selectedBladeId);
        setSearchParams(nextParams, { replace: true });
      }
    }
  }, [selectedProduct, selectedMotorId, selectedBladeId, searchParams, setSearchParams]);

  const selectedMotorFinish = useMemo(
    () => finishes.find((f) => f.finish_id === selectedMotorId),
    [finishes, selectedMotorId]
  );

  const selectedBladeFinish = useMemo(
    () => finishes.find((f) => f.finish_id === selectedBladeId),
    [finishes, selectedBladeId]
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6">
      {/* Top Banner Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-600" />
            <span>AI Room Ceiling Fan Visualizer</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Photorealistic in-room placement with automatic ceiling anchor detection & lighting harmonization
          </p>
        </div>

        <button
          onClick={() => navigate('/users')}
          className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors cursor-pointer self-start sm:self-auto"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Catalog</span>
        </button>
      </div>

      {/* Main Canvas + Control Rail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left 2 Cols: Interactive Canvas & Comparison */}
        <div className="lg:col-span-2 space-y-4">
          <RoomCanvas
            selectedProduct={selectedProduct}
            selectedMotorFinish={selectedMotorFinish}
            selectedBladeFinish={selectedBladeFinish}
          />

          <BeforeAfterView />
        </div>

        {/* Right Col: Placement Tools & Model / Room Switchers */}
        <div className="space-y-6">
          <PlacementTools onRenderAI={handleRenderAI} />

          <VisualizerFanSelector
            roomList={roomList}
            onUploadRoom={handleUploadRoom}
            isUploadingRoom={isUploadingRoom}
            products={products}
            selectedProduct={selectedProduct}
            finishes={finishes}
          />
        </div>
      </div>
    </div>
  );
};
