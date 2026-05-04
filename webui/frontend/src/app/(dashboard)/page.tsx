/**
 * Dashboard Principal — BreachRadar WebUI
 * Vue d'ensemble : statut API, graphique de détections, dernières trouvailles.
 */

import { APIStatusCards } from "@/components/dashboard/APIStatusCards";
import { RiskHeatmap } from "@/components/dashboard/RiskHeatmap";
import { FindingsTable } from "@/components/dashboard/FindingsTable";
import { RadarLoader } from "@/components/dashboard/RadarLoader";
import {
  AlertTriangle,
  Clock,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard — BreachRadar",
  description: "SOC Governance Dashboard — Data breach and ransomware monitoring",
};

// ─── Données statiques de démonstration (remplacées par fetch() en prod) ──────
const DEMO_API_STATUSES = [
  { service_name: "hibp",     service_label: "HIBP",         configured: true,  is_active: true,  last_test_success: true  },
  { service_name: "leakcheck",service_label: "LeakCheck",    configured: true,  is_active: true,  last_test_success: true  },
  { service_name: "ransomlook",service_label: "RansomLook",  configured: true,  is_active: true,  last_test_success: true  },
  { service_name: "github",   service_label: "GitHub",       configured: true,  is_active: false, last_test_success: false },
  { service_name: "dehashed", service_label: "Dehashed",     configured: false, is_active: false, last_test_success: null  },
  { service_name: "intelx",   service_label: "IntelX",       configured: false, is_active: false, last_test_success: null  },
  { service_name: "hunter",   service_label: "Hunter.io",    configured: false, is_active: false, last_test_success: null  },
  { service_name: "urlscan",  service_label: "URLScan.io",   configured: true,  is_active: true,  last_test_success: null  },
];

// ─── Cards de statistiques rapides ───────────────────────────────────────────
const QUICK_STATS = [
  {
    id: "stat-total-scans",
    label: "Scans (7d)",
    value: "7",
    icon: Clock,
    color: "text-radar",
    bg: "bg-radar/10",
  },
  {
    id: "stat-critical",
    label: "Critical",
    value: "3",
    icon: ShieldAlert,
    color: "text-red-400",
    bg: "bg-red-500/10",
  },
  {
    id: "stat-total-findings",
    label: "Total Findings",
    value: "87",
    icon: TrendingUp,
    color: "text-orange-400",
    bg: "bg-orange-500/10",
  },
  {
    id: "stat-last-scan",
    label: "Last Scan",
    value: "2h ago",
    icon: AlertTriangle,
    color: "text-yellow-400",
    bg: "bg-yellow-500/10",
  },
];

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">

      {/* ─── Rangée 1 : Stats rapides ─────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {QUICK_STATS.map((stat) => {
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

      {/* ─── Rangée 2 : Graphique + Statut API ───────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Graphique bâtonnets — 2/3 de la largeur */}
        <div className="xl:col-span-2">
          <RiskHeatmap />
        </div>

        {/* Statut des connecteurs — 1/3 */}
        <div className="card-soc p-4">
          <APIStatusCards statuses={DEMO_API_STATUSES} />
        </div>
      </div>

      {/* ─── Rangée 3 : Tableau des dernières trouvailles ─────────────────── */}
      <FindingsTable />

      {/* ─── Indicateur discret radar en bas à droite ─────────────────────── */}
      <div className="fixed bottom-6 right-6 opacity-20 hover:opacity-60 transition-opacity duration-300">
        <RadarLoader size={48} label="" />
      </div>
    </div>
  );
}
