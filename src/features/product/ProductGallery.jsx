import React, { useState } from 'react';
import { FanGraphic } from '../../components/FanGraphic.jsx';
import { Badge } from '../../components/Badge.jsx';

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

export const ProductGallery = ({
  product,
  selectedThumb,
  onSelectThumb,
  selectedMotorFinish,
  selectedBladeFinish,
}) => {
  const [imgError, setImgError] = useState(false);

  // Collect all images
  const allImages = React.useMemo(() => {
    const list = [];
    if (product.primary_image_url) list.push(product.primary_image_url);
    if (product.imagePath && !list.includes(product.imagePath)) list.push(product.imagePath);
    if (Array.isArray(product.images)) {
      product.images.forEach((im) => {
        if (im && !list.includes(im)) list.push(im);
      });
    }
    return list.map((im) => (im.startsWith('http') ? im : `/${im.replace(/^\//, '')}`));
  }, [product]);

  const activeImageUrl = allImages.length > 0 ? allImages[selectedThumb] || allImages[0] : null;

  // Colors for FanGraphic fallback
  const nameLower = (product.name || '').toLowerCase();
  const isCane = nameLower.includes('cane') || (product.fanCode || '').toLowerCase().includes('cane');
  const isWood = nameLower.includes('wood') || (product.category || '') === 'Wooden';
  const isBronze = nameLower.includes('bronze') || nameLower.includes('antique');
  const isBrass = nameLower.includes('brass') || (product.blade_type || '').toLowerCase().includes('brass');
  const isWhite = nameLower.includes('white');

  const defaultBladeColor = isCane ? '#C27E38' : isWood ? '#5F311C' : isBrass ? '#D4AF37' : isWhite ? '#DCDDDC' : '#222222';
  const defaultMotorColor = isBronze ? '#8B7355' : isBrass ? '#B8860B' : isWhite ? '#EDEDED' : '#141414';

  const bladeColor = selectedBladeFinish?.color_code || BLADE_COLOR_MAP[selectedBladeFinish?.name] || defaultBladeColor;
  const motorColor = selectedMotorFinish?.color_code || MOTOR_COLOR_MAP[selectedMotorFinish?.name] || defaultMotorColor;

  return (
    <div className="space-y-4">
      {/* Main Large Showcase Area */}
      <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-xs flex items-center justify-center relative min-h-[380px] sm:min-h-[460px] overflow-hidden group">
        <div className="absolute top-4 left-4 z-10 flex gap-1.5">
          <Badge variant="warning" size="sm">
            {product.category || 'Ceiling'}
          </Badge>
          <span className="text-[11px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
            {product.product_code || product.fanCode}
          </span>
        </div>

        {activeImageUrl && !imgError ? (
          <div className="w-full h-80 sm:h-96 flex items-center justify-center">
            <img
              src={activeImageUrl}
              alt={product.name}
              className="max-h-full max-w-full object-contain transition-transform duration-500 group-hover:scale-105 drop-shadow-md"
              onError={() => setImgError(true)}
            />
          </div>
        ) : (
          <div className="w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
            <FanGraphic
              bladeCount={product.blade_count || product.specifications?.blade_count || 3}
              isCaneWeave={isCane}
              bladeColor={bladeColor}
              motorColor={motorColor}
            />
          </div>
        )}
      </div>

      {/* Thumbnails row */}
      {allImages.length > 1 && (
        <div className="flex gap-2.5 overflow-x-auto pb-1">
          {allImages.map((img, idx) => (
            <button
              key={idx}
              onClick={() => onSelectThumb(idx)}
              className={`w-16 h-16 rounded-xl border-2 p-1 bg-white shrink-0 transition-all cursor-pointer overflow-hidden ${
                selectedThumb === idx
                  ? 'border-amber-600 shadow-xs ring-2 ring-amber-500/20'
                  : 'border-slate-200 hover:border-slate-300 opacity-70 hover:opacity-100'
              }`}
            >
              <img src={img} alt={`Thumb ${idx}`} className="w-full h-full object-contain" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
