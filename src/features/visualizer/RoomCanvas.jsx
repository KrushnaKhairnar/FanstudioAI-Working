import React, { useRef, useState } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { FanGraphic } from '../../components/FanGraphic.jsx';
import { useVisualizerStore } from './store.js';

const MOTOR_COLOR_MAP = {
  'Matt Grey': '#808080',
  'Metallic Grey': '#808080',
  'Matt Black': '#1A1A1A',
  'Matt White': '#F3F4F6',
  'Antique Bronze': '#8B7355',
  'Champagne Gold': '#D4AF37',
  'Brass': '#C5A059',
  'Walnut': '#5C4033',
  'Teak': '#B3672B',
  'Oriental Ash': '#D7B88C',
};

const BLADE_COLOR_MAP = {
  'Teak Wooden': '#C27E38',
  'Rosewood Wooden': '#5F311C',
  'Walnut Wooden': '#996933',
  'Natural Wood': '#BA9962',
  'Cane Weave': '#D2A66C',
  'Matt Black': '#1A1A1A',
  'Matt White': '#F3F4F6',
  'Oriental Ash': '#D7B88C',
};

export const RoomCanvas = ({
  selectedProduct,
  selectedMotorFinish,
  selectedBladeFinish,
  onAnchorChange,
}) => {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [imgCutoutFailed, setImgCutoutFailed] = useState(false);

  // Select only canvas and placement fields with useShallow from useVisualizerStore
  const {
    roomImage,
    renderedImageUrl,
    anchorX,
    anchorY,
    scale,
    rotation,
    brightness,
    colorTemp,
    applyShadow,
    showComparison,
    compareSplit,
    setAnchor,
  } = useVisualizerStore(
    useShallow((s) => ({
      roomImage: s.roomImage,
      renderedImageUrl: s.renderedImageUrl,
      anchorX: s.anchorX,
      anchorY: s.anchorY,
      scale: s.scale,
      rotation: s.rotation,
      brightness: s.brightness,
      colorTemp: s.colorTemp,
      applyShadow: s.applyShadow,
      showComparison: s.showComparison,
      compareSplit: s.compareSplit,
      setAnchor: s.setAnchor,
    }))
  );

  // Fallback colors for FanGraphic
  const nameLower = (selectedProduct?.name || '').toLowerCase();
  const isCane = nameLower.includes('cane') || (selectedProduct?.fanCode || '').toLowerCase().includes('cane');
  const isWood = nameLower.includes('wood') || (selectedProduct?.category || '') === 'Wooden';
  const isBronze = nameLower.includes('bronze') || nameLower.includes('antique');
  const isBrass = nameLower.includes('brass') || (selectedProduct?.blade_type || '').toLowerCase().includes('brass');
  const isWhite = nameLower.includes('white');

  const defaultBladeColor = isCane ? '#C27E38' : isWood ? '#5F311C' : isBrass ? '#D4AF37' : isWhite ? '#DCDDDC' : '#222222';
  const defaultMotorColor = isBronze ? '#8B7355' : isBrass ? '#B8860B' : isWhite ? '#EDEDED' : '#141414';

  const bladeColor = selectedBladeFinish?.color_code || BLADE_COLOR_MAP[selectedBladeFinish?.name] || defaultBladeColor;
  const motorColor = selectedMotorFinish?.color_code || MOTOR_COLOR_MAP[selectedMotorFinish?.name] || defaultMotorColor;

  const rawImg = selectedProduct?.primary_image_url || selectedProduct?.imagePath || (selectedProduct?.images && selectedProduct?.images[0]);
  const fanPhotoUrl = rawImg ? (rawImg.startsWith('http') ? rawImg : `/${rawImg.replace(/^\//, '')}`) : null;

  // Handle Dragging
  const handlePointerDown = (e) => {
    setIsDragging(true);
    updateAnchorFromEvent(e);
  };

  const handlePointerMove = (e) => {
    if (isDragging) {
      updateAnchorFromEvent(e);
    }
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  const updateAnchorFromEvent = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0.1, Math.min(0.9, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0.05, Math.min(0.8, (e.clientY - rect.top) / rect.height));
    setAnchor(x, y);
    if (onAnchorChange) onAnchorChange(x, y);
  };

  // Color temperature CSS filter approximation
  const kelvinDiff = colorTemp - 5000;
  const sepia = kelvinDiff < 0 ? Math.min(0.35, Math.abs(kelvinDiff) / 10000) : 0;
  const hueRotate = kelvinDiff > 0 ? `${Math.min(25, kelvinDiff / 200)}deg` : '0deg';

  return (
    <div
      ref={containerRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      className="relative w-full h-[450px] sm:h-[580px] bg-slate-900 rounded-3xl overflow-hidden shadow-xl select-none cursor-crosshair border border-slate-800"
    >
      {/* 1. Base Room Background */}
      <img
        src={roomImage}
        alt="Room Interior"
        className="w-full h-full object-cover pointer-events-none"
      />

      {/* 2. AI Rendered Image (when completed) */}
      {renderedImageUrl && !showComparison && (
        <img
          src={renderedImageUrl}
          alt="AI Composited Room"
          className="absolute inset-0 w-full h-full object-cover pointer-events-none z-10 animate-in fade-in duration-300"
        />
      )}

      {/* 3. Before / After Comparison Split View */}
      {renderedImageUrl && showComparison && (
        <div
          className="absolute inset-0 overflow-hidden pointer-events-none z-10"
          style={{ width: `${compareSplit}%` }}
        >
          <img
            src={renderedImageUrl}
            alt="AI Composited Room Before/After"
            className="absolute inset-0 w-full h-full object-cover"
            style={{ width: containerRef.current ? `${containerRef.current.offsetWidth}px` : '100%' }}
          />
        </div>
      )}

      {/* 4. Real-time Interactive Fan Preview Overlay (when not showing AI result) */}
      {!renderedImageUrl && selectedProduct && (
        <div
          className="absolute pointer-events-none transition-transform duration-75"
          style={{
            left: `${anchorX * 100}%`,
            top: `${anchorY * 100}%`,
            transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
            filter: `brightness(${brightness}) sepia(${sepia}) hue-rotate(${hueRotate}) ${
              applyShadow ? 'drop-shadow(0px 24px 28px rgba(0,0,0,0.45))' : ''
            }`,
          }}
        >
          {fanPhotoUrl && !imgCutoutFailed ? (
            <div className="w-56 h-56 sm:w-64 sm:h-64 flex items-center justify-center">
              <img
                src={fanPhotoUrl}
                alt={selectedProduct.name}
                className="w-full h-full object-contain"
                onError={() => setImgCutoutFailed(true)}
              />
            </div>
          ) : (
            <div className="w-56 h-56 sm:w-64 sm:h-64 flex items-center justify-center">
              <FanGraphic
                bladeCount={selectedProduct.blade_count || selectedProduct.specifications?.blade_count || 3}
                bladeColor={bladeColor}
                motorColor={motorColor}
                isDownrod={true}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
