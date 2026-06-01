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
import { IntelligenceWidget } from "@/components/dashboard/IntelligenceWidget";
import { AlertTriangle, Clock, ShieldAlert, TrendingUp } from "lucide-react";
import type { Metadata } from "next";
import { fetchJSON } from "@/lib/fetch";
import { getTranslations } from "next-intl/server";

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

// ─── Formatage "X ago" ────────────────────────────────────────────────────────────────────
function formatTimeAgo(iso: string | null, t: any): string {
  if (!iso) return t("Common.never");
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1)  return t("Common.just_now");
  if (minutes < 60) return t("Common.time_ago", { time: minutes, unit: t("Common.unit_m") });
  const hours = Math.floor(minutes / 60);
  if (hours < 24)   return t("Common.time_ago", { time: hours, unit: t("Common.unit_h") });
  return t("Common.time_ago", { time: Math.floor(hours / 24), unit: t("Common.unit_d") });
}

// ─── Page ────────────────────────────────────────────────────────────────────────────────
export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ period?: string }>;
}) {
  const { period = "7d" } = await searchParams;
  const t = await getTranslations();

  // Appels parallèles vers le backend
  const [stats, connectors, findingsRes, chartData, ransomwareRes, cveRes, scansRes] = await Promise.all([
    fetchJSON<DashboardStats>("/api/v1/dashboard/stats"),
    fetchJSON<ConnectorStatus[]>("/api/v1/connectors/status"),
    fetchJSON<any>("/api/v1/findings?limit=10&sort=discovered_at:desc"),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?period=${period}`),
    fetchJSON<any>("/api/v1/ransomlook/alerts?status=LISTED&limit=1"),
    fetchJSON<any>("/api/v1/cve/alerts?limit=5"),
    fetchJSON<any>("/api/v1/scans?limit=10"),
  ]);

  const findings = findingsRes?.items || [];
  const ransomwareAlerts = ransomwareRes?.items || [];
  const cveAlerts = cveRes?.items || [];
  const recentScans = scansRes?.items || [];

  // Au moins un connecteur actif ? → afficher le CTA "Premier scan"
  const hasActiveConnector =
    Array.isArray(connectors) &&
    connectors.some((c) => c.is_active && c.configured);

  // ─── Cards de statistiques rapides ───────────────────────────────────────────────
  const quickStats = [
    {
      id: "stat-critical",
      label: t("Dashboard.stat_critical"),
      value: stats?.critical_count ?? 0,
      icon: ShieldAlert,
      bg: "bg-red-500/10",
      color: "text-red-500",
    },
    {
      id: "stat-total",
      label: t("Dashboard.stat_findings"),
      value: stats?.total_findings ?? 0,
      icon: TrendingUp,
      bg: "bg-radar/10",
      color: "text-radar",
    },
    {
      id: "stat-scans",
      label: t("Dashboard.stat_scans"),
      value: stats?.scans_7d ?? 0,
      icon: Clock,
      bg: "bg-blue-500/10",
      color: "text-blue-500",
    },
    {
      id: "stat-last-scan",
      label: t("Dashboard.stat_last_scan"),
      value: formatTimeAgo(stats?.last_scan_at ?? null, t),
      icon: Clock,
      bg: "bg-secondary",
      color: "text-muted-foreground",
    },
  ];

  const hasMockData = Array.isArray(connectors) && connectors.some(c => c.is_mock);

  return (
    <div className="space-y-6 animate-fade-in">
      {hasMockData && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 flex items-center gap-3 text-orange-400">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div className="text-sm">
            <span className="font-bold uppercase mr-2">{t("Dashboard.alert_demo_title")} :</span>
            {t("Dashboard.alert_demo_text")}
          </div>
        </div>
      )}

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
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="h-[400px]">
          <RiskHeatmap data={chartData ?? []} initialPeriod={period as any} />
        </div>
        <div className="card-soc p-4 h-[400px]">
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
        <div className="flex flex-col gap-4">
          <IntelligenceWidget />
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
