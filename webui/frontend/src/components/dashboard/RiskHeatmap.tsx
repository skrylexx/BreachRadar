"use client";

/**
 * RiskHeatmap — Graphique à bâtonnets des détections dans le temps
 * Basé sur Recharts (BarChart).
 * Sélecteur de période : 7j | 1 mois | 6 mois | 12 mois.
 */

import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

type Period = "7d" | "1m" | "6m" | "12m";

interface DataPoint {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

interface RiskHeatmapProps {
  data?: DataPoint[];
  isLoading?: boolean;
}

const PERIOD_LABELS: Record<Period, string> = {
  "7d": "7 days",
  "1m": "1 month",
  "6m": "6 months",
  "12m": "12 months",
};

// Données de démonstration si pas de data réelle
const DEMO_DATA: DataPoint[] = [
  { date: "Apr 28", critical: 0, high: 2, medium: 5, low: 8, total: 15 },
  { date: "Apr 29", critical: 1, high: 3, medium: 4, low: 6, total: 14 },
  { date: "Apr 30", critical: 2, high: 4, medium: 7, low: 3, total: 16 },
  { date: "May 01", critical: 0, high: 1, medium: 3, low: 9, total: 13 },
  { date: "May 02", critical: 3, high: 5, medium: 2, low: 4, total: 14 },
  { date: "May 03", critical: 0, high: 2, medium: 6, low: 7, total: 15 },
  { date: "May 04", critical: 1, high: 3, medium: 4, low: 5, total: 13 },
];

// ─── Tooltip personnalisé ─────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-foreground mb-2 font-data">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center justify-between gap-4 text-xs">
          <span className="text-muted-foreground capitalize">{entry.name}</span>
          <span className="font-semibold" style={{ color: entry.fill }}>
            {entry.value}
          </span>
        </div>
      ))}
      <div className="border-t border-border mt-2 pt-2 flex justify-between text-xs">
        <span className="text-muted-foreground">Total</span>
        <span className="font-bold text-foreground">
          {payload.reduce((acc: number, e: any) => acc + e.value, 0)}
        </span>
      </div>
    </div>
  );
}

// ─── Composant ────────────────────────────────────────────────────────────────
export function RiskHeatmap({ data = DEMO_DATA, isLoading = false }: RiskHeatmapProps) {
  const [period, setPeriod] = useState<Period>("7d");

  return (
    <div className="card-soc p-4 space-y-4">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Detection Volume</h3>
          <p className="text-xs text-muted-foreground">
            Findings over time — all sources combined
          </p>
        </div>

        {/* Sélecteur de période */}
        <div
          className="flex items-center bg-secondary rounded-md border border-border overflow-hidden"
          role="group"
          aria-label="Time period selector"
        >
          {(Object.keys(PERIOD_LABELS) as Period[]).map((p) => (
            <button
              key={p}
              id={`period-${p}`}
              onClick={() => setPeriod(p)}
              className={`px-2.5 py-1.5 text-xs font-medium transition-colors duration-150
                ${period === p
                  ? "bg-radar text-background"
                  : "text-muted-foreground hover:text-foreground"
                }`}
              aria-pressed={period === p}
            >
              {PERIOD_LABELS[p]}
            </button>
          ))}
        </div>
      </div>

      {/* Graphique */}
      <div className="h-48">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-xs text-muted-foreground font-data animate-pulse">
              Loading data...
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 4, right: 4, left: -20, bottom: 0 }}
              barSize={data.length > 30 ? 4 : data.length > 15 ? 8 : 16}
              barGap={2}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="hsl(var(--border))"
                strokeOpacity={0.5}
              />
              <XAxis
                dataKey="date"
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(56,189,248,0.05)" }} />

              {/* Bâtonnets empilés par sévérité */}
              <Bar dataKey="critical" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
              <Bar dataKey="high"     stackId="a" fill="#f97316" radius={[0, 0, 0, 0]} />
              <Bar dataKey="medium"   stackId="a" fill="#eab308" radius={[0, 0, 0, 0]} />
              <Bar dataKey="low"      stackId="a" fill="#64748b" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Légende manuelle (plus lisible que celle de Recharts) */}
      <div className="flex items-center gap-4 justify-end">
        {[
          { label: "Critical", color: "#ef4444" },
          { label: "High",     color: "#f97316" },
          { label: "Medium",   color: "#eab308" },
          { label: "Low",      color: "#64748b" },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: color }} />
            <span className="text-xs text-muted-foreground">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
