/**
 * Dashboard Principal — BreachRadar WebUI
 * Server Component async : toutes les données proviennent du backend FastAPI.
 * Aucune donnée fictive — empty state si le backend ne répond pas ou retourne vide.
 */

import { APIStatusCards } from "@/components/dashboard/APIStatusCards";
import type { ConnectorStatus } from "@/lib/api";
import { RiskHeatmap } from "@/components/dashboard/RiskHeatmap";
import { FindingsTable } from "@/components/dashboard/FindingsTable";
import { RadarLoader } from "@/components/dashboard/RadarLoader";
import { RansomwareAlertBlock } from "@/components/dashboard/RansomwareAlertBlock";
import { CVEAlertsBlock } from "@/components/dashboard/CVEAlertsBlock";
import { ScansTableBlock } from "@/components/dashboard/ScansTableBlock";
import { QuickAccessBlock } from "@/components/dashboard/QuickAccessBlock";
import { AlertTriangle, Clock, ShieldAlert, TrendingUp } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard — BreachRadar",
  description: "SOC Governance Dashboard — Data breach and ransomware monitoring",
};

// Pas de cache — données temps réel à chaque requête
export const revalidate = 0;

// ─── Types ────────────────────────────────────────────────────────────────────────────────
interface DashboardStats {
  scans_7d: number;
  critical_count: number;
  total_findings: number;
  last_scan_at: string | null;
}

// ─── Helpers fetch ─────────────────────────────────────────────────────────────────────
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://breachradar-api:8000";

async function fetchJSON<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

// ─── Formatage "X ago" ────────────────────────────────────────────────────────────────────
function timeAgo(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1)  return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24)   return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

// ─── Page ────────────────────────────────────────────────────────────────────────────────
export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ period?: string }>;
}) {
  const { period = "7d" } = await searchParams;

  // Appels parallèles vers le backend
  const [stats, connectors, findings, chartData, ransomwareAlerts, cveAlerts, scansRes] = await Promise.all([
    fetchJSON<DashboardStats>("/api/v1/dashboard/stats"),
    fetchJSON<ConnectorStatus[]>("/api/v1/connectors/status"),
    fetchJSON<any[]>("/api/v1/findings?limit=10&sort=discovered_at:desc"),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?period=${period}`),
    fetchJSON<any[]>("/api/v1/ransomlook/alerts?status=LISTED&limit=1"),
    fetchJSON<any[]>("/api/v1/cve/alerts?limit=5"),
    fetchJSON<any>("/api/v1/scans?limit=10"),
  ]);

  const recentScans = scansRes?.items || [];

  // Au moins un connecteur actif ? → afficher le CTA "Premier scan"
  const hasActiveConnector =
    Array.isArray(connectors) &&
    connectors.some((c) => c.is_active && c.configured);

  // ─── Cards de statistiques rapides ───────────────────────────────────────────────
  const quickStats = [
    {
      id: "stat-total-scans",
      label: "Scans (7d)",
      value: stats ? String(stats.scans_7d) : "—",
      icon: Clock,
      color: "text-radar",
      bg: "bg-radar/10",
    },
    {
      id: "stat-critical",
      label: "Critical",
      value: stats ? String(stats.critical_count) : "—",
      icon: ShieldAlert,
      color: "text-red-400",
      bg: "bg-red-500/10",
    },
    {
      id: "stat-total-findings",
      label: "Total Findings",
      value: stats ? String(stats.total_findings) : "—",
      icon: TrendingUp,
      color: "text-orange-400",
      bg: "bg-orange-500/10",
    },
    {
      id: "stat-last-scan",
      label: "Last Scan",
      value: stats ? timeAgo(stats.last_scan_at) : "—",
      icon: AlertTriangle,
      color: "text-yellow-400",
      bg: "bg-yellow-500/10",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ─── Rangée 1 : Stats rapides ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {quickStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.id} id={stat.id} className="card-soc p-4 flex items-center gap-3">
              <div className={`w-9 h-9 rounded-md ${stat.bg} flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-5 h-5 ${stat.color}`} strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-xl font-bold text-foreground font-data">
                  {stat.value}
                </p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* ─── Rangée 2 : Graphique + Statut connecteurs ──────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          <RiskHeatmap data={chartData ?? []} initialPeriod={period as any} />
        </div>
        <div className="card-soc p-4">
          <APIStatusCards statuses={connectors ?? []} />
        </div>
      </div>

      {/* ─── Rangée 3 : Alertes Ransomware (conditionnel) ───────────────────────── */}
      {Array.isArray(ransomwareAlerts) && ransomwareAlerts.length > 0 && (
        <RansomwareAlertBlock alerts={ransomwareAlerts} />
      )}

      {/* ─── Rangée 4 : Dernières CVE (si configuré) ─────────────────────────────── */}
      {Array.isArray(cveAlerts) && cveAlerts.length > 0 && (
        <CVEAlertsBlock alerts={cveAlerts} />
      )}

      {/* ─── Rangée 5 : Tableau des dernières trouvailles ─────────────────────────── */}
      <FindingsTable
        findings={findings ?? []}
        hasActiveConnector={hasActiveConnector}
      />

      {/* ─── Rangée 6 : Scans & Accès Rapide ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          <ScansTableBlock scans={recentScans} />
        </div>
        <div>
          <QuickAccessBlock />
        </div>
      </div>

      {/* ─── Indicateur radar discret ──────────────────────────────────────────────── */}
      <div className="fixed bottom-6 right-6 opacity-20 hover:opacity-60 transition-opacity duration-300">
        <RadarLoader size={48} label="" />
      </div>
    </div>
  );
}
