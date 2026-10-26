import React from 'react';

export const FanGraphic = ({
  motorColor = '#1F1F1F',
  bladeColor = '#5F311C',
  bladeCount = 3,
  isCaneWeave = false,
  className = 'w-full h-full',
  rotation = 0,
}) => {
  const size = 300;
  const center = size / 2;
  const motorRadius = 38;
  const canopyRadius = 14;
  const bladeLength = 112;
  const bladeWidth = 26;

  const angleStep = 360 / bladeCount;
  const blades = Array.from({ length: bladeCount }, (_, i) => i * angleStep);

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      className={className}
      style={{
        transform: `rotate(${rotation}deg)`,
        transition: 'transform 0.25s ease-out',
        filter: 'drop-shadow(0px 10px 18px rgba(0,0,0,0.22))',
      }}
    >
      <defs>
        {/* Motor gradients */}
        <radialGradient id="motorGrad" cx="45%" cy="40%" r="55%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.35" />
          <stop offset="50%" stopColor={motorColor} />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.85" />
        </radialGradient>

        {/* Blade metallic/wood sheen gradient */}
        <linearGradient id="bladeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={bladeColor} />
          <stop offset="35%" stopColor="#ffffff" stopOpacity="0.20" />
          <stop offset="70%" stopColor={bladeColor} />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.45" />
        </linearGradient>

        {/* Cane pattern if applicable */}
        <pattern id="canePattern" width="8" height="8" patternUnits="userSpaceOnUse">
          <rect width="8" height="8" fill={bladeColor} />
          <circle cx="4" cy="4" r="2.5" fill="#E6BE8A" opacity="0.65" />
          <path d="M 0 0 L 8 8 M 8 0 L 0 8" stroke="#8A5A2B" strokeWidth="0.8" opacity="0.5" />
        </pattern>
      </defs>

      {/* Blades */}
      <g>
        {blades.map((angle, index) => {
          return (
            <g
              key={index}
              transform={`rotate(${angle} ${center} ${center})`}
            >
              {/* Blade aerofoil curve */}
              <path
                d={`
                  M ${center - bladeWidth / 3} ${center - motorRadius + 6}
                  L ${center - bladeWidth / 2} ${center - motorRadius - bladeLength + 15}
                  Q ${center} ${center - motorRadius - bladeLength} ${center + bladeWidth / 2} ${center - motorRadius - bladeLength + 15}
                  L ${center + bladeWidth / 3} ${center - motorRadius + 6}
                  Z
                `}
                fill={isCaneWeave ? 'url(#canePattern)' : 'url(#bladeGrad)'}
                stroke="rgba(0,0,0,0.25)"
                strokeWidth="1.2"
              />

              {/* Cane inlay panel if applicable */}
              {isCaneWeave && (
                <rect
                  x={center - bladeWidth / 3.2}
                  y={center - motorRadius - bladeLength + 25}
                  width={bladeWidth * 0.62}
                  height={bladeLength - 35}
                  rx="4"
                  fill="url(#canePattern)"
                  stroke="#5A3D1E"
                  strokeWidth="1.2"
                />
              )}

              {/* Blade bracket joint */}
              <path
                d={`
                  M ${center - 8} ${center - motorRadius + 14}
                  L ${center + 8} ${center - motorRadius + 14}
                  L ${center + 5} ${center - motorRadius - 4}
                  L ${center - 5} ${center - motorRadius - 4}
                  Z
                `}
                fill={motorColor}
                stroke="#000"
                strokeWidth="0.8"
              />
              <circle cx={center - 3} cy={center - motorRadius + 5} r="1.5" fill="#E5E7EB" />
              <circle cx={center + 3} cy={center - motorRadius + 5} r="1.5" fill="#E5E7EB" />
            </g>
          );
        })}
      </g>

      {/* Motor Outer Ring & Housing */}
      <circle
        cx={center}
        cy={center}
        r={motorRadius}
        fill="url(#motorGrad)"
        stroke="rgba(255,255,255,0.25)"
        strokeWidth="1.5"
      />

      {/* Decorative center bevel ring */}
      <circle
        cx={center}
        cy={center}
        r={motorRadius * 0.75}
        fill="none"
        stroke="rgba(255,255,255,0.18)"
        strokeWidth="1"
      />

      {/* Center Canopy & Downrod Mount */}
      <circle
        cx={center}
        cy={center}
        r={canopyRadius}
        fill={motorColor}
        stroke="#000"
        strokeWidth="1"
      />
      <circle
        cx={center}
        cy={center}
        r={canopyRadius * 0.5}
        fill="#111111"
      />
      <circle
        cx={center - 2}
        cy={center - 2}
        r={canopyRadius * 0.25}
        fill="#FFFFFF"
        opacity="0.6"
      />
    </svg>
  );
};
