/**
 * RadarSpinner — Spinner animé type radar
 * Utilisé pendant les scans en cours et le chargement des données.
 *
 * SVG natif — pas de dépendance externe.
 * Identique visuellement au RadarLoader mais plus léger (aucun état interne).
 */

import { cn } from "@/lib/utils";

interface RadarSpinnerProps {
  size?: number;
  className?: string;
  label?: string;
}

export function RadarSpinner({ size = 40, className, label }: RadarSpinnerProps) {
  const r = size / 2;

  return (
    <div
      className={cn("flex flex-col items-center gap-2", className)}
      role="status"
      aria-label={label ?? "Chargement en cours…"}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* Cercles concentriques */}
        {[0.85, 0.6, 0.35].map((ratio, idx) => (
          <circle
            key={idx}
            cx={r}
            cy={r}
            r={r * ratio}
            fill="none"
            stroke="rgba(56, 189, 248, 0.15)"
            strokeWidth="1"
          />
        ))}

        {/* Ligne de sweep radar — rotation continue */}
        <g
          style={{
            transformOrigin: `${r}px ${r}px`,
            animation: "radar-sweep 3s linear infinite",
          }}
        >
          <line
            x1={r}
            y1={r}
            x2={r}
            y2={r * 0.1}
            stroke="#38bdf8"
            strokeWidth="1.5"
            strokeLinecap="round"
            opacity="0.9"
          />
          {/* Dégradé de traîne */}
          <path
            d={`M ${r} ${r} L ${r} ${r * 0.1} A ${r * 0.9} ${r * 0.9} 0 0 0 ${r + r * 0.9 * Math.sin(-Math.PI / 4)} ${r - r * 0.9 * Math.cos(-Math.PI / 4)} Z`}
            fill="url(#radarGradient)"
            opacity="0.2"
          />
        </g>

        {/* Point central */}
        <circle cx={r} cy={r} r="2" fill="#38bdf8" opacity="0.8" />

        <defs>
          <linearGradient id="radarGradient" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>

      {label && (
        <span className="text-xs text-muted-foreground font-data animate-pulse">
          {label}
        </span>
      )}
    </div>
  );
}
