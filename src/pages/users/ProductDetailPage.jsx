import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useProductDetail } from '../../features/product/useProductDetail.js';
import { ProductGallery } from '../../features/product/ProductGallery.jsx';
import { FinishMixer } from '../../features/product/FinishMixer.jsx';
import { ProductSpecs } from '../../features/product/ProductSpecs.jsx';
import { NoData } from '../../components/NoData.jsx';

export const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    product,
    motorFinishes,
    bladeFinishes,
    isLoading,
    error,
    selectedThumb,
    setSelectedThumb,
    bladeSizes,
    fanTypes,
    selectedBladeSize,
    setSelectedBladeSize,
    selectedFanType,
    setSelectedFanType,
    selectedMotorId,
    setSelectedMotorId,
    selectedBladeId,
    setSelectedBladeId,
    selectedColorIdx,
    setSelectedColorIdx,
    calculatedPrice,
  } = useProductDetail(id);

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-amber-600 mb-2" />
        <p className="text-xs font-semibold">Loading product specifications...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <NoData
          title="Product Not Found"
          description={error || "The ceiling fan product you requested could not be found."}
          actionLabel="Back to Fan Catalog"
          onAction={() => navigate('/users')}
        />
      </div>
    );
  }

  const selectedMotorFinish = motorFinishes.find((f) => f.finish_id === selectedMotorId);
  const selectedBladeFinish = bladeFinishes.find((f) => f.finish_id === selectedBladeId);

  const handleOpenVisualizer = () => {
    navigate(
      `/users/visualizer?product=${encodeURIComponent(product.product_id)}&motor=${encodeURIComponent(
        selectedMotorId || ''
      )}&blade=${encodeURIComponent(selectedBladeId || '')}`
    );
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Top Back Navigation Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/users')}
          className="flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-slate-900 transition-colors cursor-pointer group"
        >
          <div className="w-7 h-7 rounded-lg bg-white border border-slate-200 group-hover:border-slate-300 shadow-2xs flex items-center justify-center">
            <ArrowLeft className="w-3.5 h-3.5 text-slate-700" />
          </div>
          <span>Back to Catalog</span>
        </button>

        <div className="text-xs text-slate-400 font-mono">
          Model: {product.product_code || product.fanCode}
        </div>
      </div>

      {/* Main 2-Column Split: Gallery & Finish Mixer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-start">
        <ProductGallery
          product={product}
          selectedThumb={selectedThumb}
          onSelectThumb={setSelectedThumb}
          selectedMotorFinish={selectedMotorFinish}
          selectedBladeFinish={selectedBladeFinish}
        />

        <FinishMixer
          bladeSizes={bladeSizes}
          selectedBladeSize={selectedBladeSize}
          onSelectBladeSize={setSelectedBladeSize}
          fanTypes={fanTypes}
          selectedFanType={selectedFanType}
          onSelectFanType={setSelectedFanType}
          motorFinishes={motorFinishes}
          selectedMotorId={selectedMotorId}
          onSelectMotorId={setSelectedMotorId}
          bladeFinishes={bladeFinishes}
          selectedBladeId={selectedBladeId}
          onSelectBladeId={setSelectedBladeId}
          colorsList={product.colors || []}
          selectedColorIdx={selectedColorIdx}
          onSelectColorIdx={setSelectedColorIdx}
          calculatedPrice={calculatedPrice}
          onOpenVisualizer={handleOpenVisualizer}
        />
      </div>

      {/* Specifications & Overview */}
      <ProductSpecs product={product} />
    </div>
  );
};
