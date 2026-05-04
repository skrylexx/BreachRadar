"use client";

/**
 * RadarLoader — Animation de chargement radar SVG
 * Utilisée : pendant les scans en cours + dans la landing page (discret).
 * Props : size (px), label (texte sous le radar).
 */

interface RadarLoaderProps {
  size?: number;
  label?: string;
  className?: string;
}

export function RadarLoader({
  size = 120,
  label = "Scanning...",
  className = "",
}: RadarLoaderProps) {
  const center = size / 2;
  const maxRadius = size / 2 - 4;
  const rings = 4;

  return (
    <div
      className={`flex flex-col items-center gap-3 ${className}`}
      role="status"
      aria-label={label}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="radar-glow"
        >
          {/* Cercles concentriques */}
          {Array.from({ length: rings }).map((_, i) => (
            <circle
              key={i}
              cx={center}
              cy={center}
              r={(maxRadius / rings) * (i + 1)}
              stroke="#38bdf8"
              strokeWidth="0.75"
              strokeDasharray="3 6"
              opacity={0.3 + i * 0.1}
            />
          ))}

          {/* Lignes de quadrant */}
          <line x1={center} y1="4" x2={center} y2={size - 4} stroke="#38bdf8" strokeWidth="0.5" opacity="0.3" />
          <line x1="4" y1={center} x2={size - 4} y2={center} stroke="#38bdf8" strokeWidth="0.5" opacity="0.3" />

          {/* Sweep animé */}
          <g
            style={{
              transformOrigin: `${center}px ${center}px`,
              animation: "radar-sweep 2.5s linear infinite",
            }}
          >
            <defs>
              <radialGradient id={`sweep-g-${size}`} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
                gradientTransform={`translate(${center} ${center}) scale(${maxRadius})`}>
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0" />
                <stop offset="60%" stopColor="#38bdf8" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.1" />
              </radialGradient>
            </defs>
            <path
              d={`M${center} ${center} L${size - 4} ${center} A${maxRadius} ${maxRadius} 0 0 0 ${center} ${4} Z`}
              fill={`url(#sweep-g-${size})`}
            />
          </g>

          {/* Point clignotant au centre */}
          <circle cx={center} cy={center} r="3" fill="#38bdf8" />
          <circle
            cx={center} cy={center} r="3"
            fill="#38bdf8"
            opacity="0.6"
            style={{ animation: "radar-ping 2s ease-in-out infinite" }}
          />
        </svg>
      </div>

      {/* Label */}
      {label && (
        <p className="text-xs font-data text-radar/70 tracking-wider uppercase">
          {label}
        </p>
      )}
    </div>
  );
}
