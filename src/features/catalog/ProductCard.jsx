import React, { useState } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { FanGraphic } from '../../components/FanGraphic.jsx';
import { Badge } from '../../components/Badge.jsx';

export const ProductCard = ({ fan, onSelectProduct, onOpenVisualizer }) => {
  const [imgError, setImgError] = useState(false);
  const rawImg = fan.primary_image_url || fan.imagePath || (fan.images && fan.images[0]);
  const displayImg = rawImg ? (rawImg.startsWith('http') ? rawImg : `/${rawImg.replace(/^\//, '')}`) : null;

  const nameLower = (fan.name || '').toLowerCase();
  const isCane = nameLower.includes('cane') || (fan.fanCode || '').toLowerCase().includes('cane');
  const isWood = nameLower.includes('wood') || (fan.category || '') === 'Wooden';
  const isBronze = nameLower.includes('bronze') || nameLower.includes('antique');
  const isBrass = nameLower.includes('brass') || (fan.blade_type || '').toLowerCase().includes('brass');
  const isWhite = nameLower.includes('white');

  const bladeColor = isCane ? '#C27E38' : isWood ? '#5F311C' : isBrass ? '#D4AF37' : isWhite ? '#DCDDDC' : '#222222';
  const motorColor = isBronze ? '#8B7355' : isBrass ? '#B8860B' : isWhite ? '#EDEDED' : '#141414';

  const priceVal = fan.price || fan.base_price || 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs hover:shadow-xl transition-all duration-300 flex flex-col justify-between overflow-hidden group">
      {/* Top Meta: Category / Tag & Code */}
      <div className="p-4 pb-0 flex items-center justify-between">
        {fan.tag ? (
          <Badge
            variant={fan.tag === 'Best Seller' ? 'warning' : 'info'}
            size="sm"
          >
            {fan.tag}
          </Badge>
        ) : (
          <Badge variant="default" size="sm">
            {fan.category || 'Ceiling'}
          </Badge>
        )}

        <span className="text-[11px] text-slate-400 font-mono">
          {fan.product_code || fan.fanCode}
        </span>
      </div>

      {/* Fan Image or Canvas Graphic */}
      <div
        onClick={() => onSelectProduct(fan)}
        className="p-6 cursor-pointer flex items-center justify-center h-56 group-hover:scale-105 transition-transform duration-300 relative"
      >
        {displayImg && !imgError ? (
          <div className="w-48 h-48 flex items-center justify-center overflow-hidden rounded-xl bg-slate-50 border border-slate-100 p-2 shadow-2xs">
            <img
              src={displayImg}
              alt={fan.name}
              className="w-full h-full object-contain"
              onError={() => setImgError(true)}
            />
          </div>
        ) : (
          <div className="w-48 h-48 flex items-center justify-center bg-slate-50/70 rounded-xl p-2 border border-slate-100 shadow-2xs">
            <FanGraphic
              bladeCount={fan.blade_count || 3}
              isCaneWeave={isCane}
              bladeColor={bladeColor}
              motorColor={motorColor}
            />
          </div>
        )}
      </div>

      {/* Card Content & Details */}
      <div className="p-4 pt-2 border-t border-slate-100 bg-slate-50/40">
        <div className="mb-2">
          <h3
            onClick={() => onSelectProduct(fan)}
            className="font-extrabold text-sm text-slate-900 group-hover:text-amber-800 transition-colors cursor-pointer"
          >
            {fan.name || fan.fanName}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">
            {fan.blade_type || 'Aerodynamic Wooden Blade'} • {fan.blade_count || 3} Blades
          </p>

          {/* Motor Housing & Blade Color Badges */}
          {(fan.motor_colors?.length || fan.blade_colors?.length) ? (
            <div className="flex flex-wrap gap-1 mt-2">
              {fan.motor_colors && fan.motor_colors.length > 0 && (
                <Badge variant="motor" size="xs">
                  {fan.motor_colors.length} Motors
                </Badge>
              )}
              {fan.blade_colors && fan.blade_colors.length > 0 && (
                <Badge variant="blade" size="xs">
                  {fan.blade_colors.length} Blade Finishes
                </Badge>
              )}
              {fan.default_motor_color && fan.default_blade_color && (
                <span className="text-[9px] text-slate-400 truncate w-full mt-0.5">
                  Default: {fan.default_motor_color} / {fan.default_blade_color}
                </span>
              )}
            </div>
          ) : null}
        </div>

        {/* Price & Action Row */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 mt-3">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">
              Starting at
            </span>
            <span className="text-sm font-extrabold text-slate-900">
              ₹{Number(priceVal).toLocaleString()}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onOpenVisualizer(fan)}
              title="Visualize in room with AI"
              className="p-2 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 transition-colors cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onSelectProduct(fan)}
              className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-amber-700 text-white text-xs font-bold transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>Details</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
