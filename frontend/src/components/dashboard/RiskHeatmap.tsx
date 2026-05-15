"use client";

/**
 * RiskHeatmap — Graphique à bâtonnets des détections dans le temps
 * Reçoit les données du Server Component parent.
 * Affiche un empty state si data est vide.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { BarChart2 } from "lucide-react";
import { TimeFilter, type TimePeriod } from "@/components/ui/time-filter";

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
  initialPeriod?: TimePeriod;
}

// ─── Tooltip personnalisé ─────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-foreground mb-2 font-data">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center justify-between gap-4 text-xs">
          <span className="text-muted-foreground capitalize">{entry.name}</span>
          <span className="font-semibold" style={{ color: entry.fill }}>{entry.value}</span>
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

// ─── Empty state ──────────────────────────────────────────────────────────────
function EmptyChart() {
  return (
    <div className="h-48 flex flex-col items-center justify-center gap-2">
      <BarChart2 className="w-8 h-8 text-muted-foreground/30" strokeWidth={1} />
      <p className="text-xs text-muted-foreground">No detection data yet</p>
    </div>
  );
}

export function RiskHeatmap({ data = [], isLoading = false, initialPeriod = "7d" }: RiskHeatmapProps) {
  const router = useRouter();

  const handlePeriodChange = (p: TimePeriod) => {
    router.push(`/?period=${p}`);
  };

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
        <TimeFilter value={initialPeriod} onChange={handlePeriodChange} />
      </div>

      {/* Graphique ou empty state */}
      {isLoading ? (
        <div className="h-48 flex items-center justify-center">
          <p className="text-xs text-muted-foreground font-data animate-pulse">Loading data...</p>
        </div>
      ) : data.length === 0 ? (
        <EmptyChart />
      ) : (
        <div className="h-48">
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
              <Bar dataKey="critical" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
              <Bar dataKey="high"     stackId="a" fill="#f97316" radius={[0, 0, 0, 0]} />
              <Bar dataKey="medium"   stackId="a" fill="#eab308" radius={[0, 0, 0, 0]} />
              <Bar dataKey="low"      stackId="a" fill="#64748b" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Légende */}
      {data.length > 0 && (
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
      )}
    </div>
  );
}
