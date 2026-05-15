"use client";

/**
 * FindingsTable — Tableau des dernières trouvailles
 * - Empty state standard si aucune donnée et aucun connecteur actif
 * - Empty state avec CTA "Premier scan" si au moins un connecteur est actif
 */

import { Shield, Radar } from "lucide-react";
import { useState } from "react";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";

interface Finding {
  id: string;
  source: string;
  domain: string;
  severity: SeverityLevel;
  type: string;
  count: number;
  discovered_at: string;
}

// ─── Badge source ──────────────────────────────────────────────────────────────────
function SourceBadge({ source }: { source: string }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-md text-xs
                 bg-secondary border border-border/50 text-muted-foreground font-data"
    >
      {source}
    </span>
  );
}

// ─── CTA "Premier scan" ─────────────────────────────────────────────────────────────
function FirstScanCTA() {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");

  async function triggerScan() {
    setState("loading");
    try {
      const res = await fetch("/scans/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_domain: null }),
        credentials: "include",
      });
      setState(res.ok ? "done" : "error");
      // Recharger la page après 2s pour afficher les résultats
      if (res.ok) setTimeout(() => window.location.reload(), 2000);
    } catch {
      setState("error");
    }
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-8">
      <div className="relative mb-5">
        <Shield className="w-10 h-10 text-muted-foreground/30" strokeWidth={1} />
        <span className="absolute -bottom-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-radar opacity-60" />
          <span className="relative inline-flex rounded-full h-4 w-4 bg-radar/80" />
        </span>
      </div>

      <p className="text-sm font-medium text-foreground mb-1">No findings yet</p>
      <p className="text-xs text-muted-foreground max-w-xs mb-5">
        Your connectors are ready. Launch a first scan to populate the dashboard.
      </p>

      {state === "idle" && (
        <button
          onClick={triggerScan}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md
                     bg-radar/10 hover:bg-radar/20 border border-radar/30
                     text-radar text-xs font-semibold transition-colors duration-150"
        >
          <Radar className="w-3.5 h-3.5" />
          Launch first scan
        </button>
      )}

      {state === "loading" && (
        <span className="text-xs text-radar animate-pulse">Scan in progress…</span>
      )}

      {state === "done" && (
        <span className="text-xs text-emerald-400">
          Scan launched — refreshing…
        </span>
      )}

      {state === "error" && (
        <span className="text-xs text-red-400">
          Failed to start scan. Check your permissions.
        </span>
      )}
    </div>
  );
}

// ─── Empty state standard ───────────────────────────────────────────────────────────
function EmptyFindings() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-8">
      <Shield className="w-10 h-10 text-muted-foreground/30 mb-4" strokeWidth={1} />
      <p className="text-sm font-medium text-foreground mb-1">No findings yet</p>
      <p className="text-xs text-muted-foreground max-w-xs">
        Findings will appear here once the backend has completed its first scan
        and data sources are configured.
      </p>
    </div>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────────
export function FindingsTable({
  findings = [],
  hasActiveConnector = false,
}: {
  findings?: Finding[];
  hasActiveConnector?: boolean;
}) {
  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const columns: DataTableColumn<Finding>[] = [
    {
      key: "severity",
      header: "Severity",
      render: (row) => <SeverityBadge level={row.severity} />,
      sortable: true,
      accessor: (row) => row.severity,
    },
    {
      key: "source",
      header: "Source",
      render: (row) => <SourceBadge source={row.source} />,
      sortable: true,
      accessor: (row) => row.source,
    },
    {
      key: "domain",
      header: "Domain",
      className: "font-data text-foreground",
      sortable: true,
      accessor: (row) => row.domain,
    },
    {
      key: "type",
      header: "Type",
      className: "capitalize",
      sortable: true,
      accessor: (row) => row.type,
    },
    {
      key: "count",
      header: "Count",
      className: "font-data font-semibold text-foreground",
      sortable: true,
      accessor: (row) => row.count,
    },
    {
      key: "discovered_at",
      header: "Discovered",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.discovered_at),
      sortable: true,
      accessor: (row) => row.discovered_at,
    },
  ];

  return (
    <div className="card-soc">
      {/* En-tête */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-radar" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold text-foreground">Latest Findings</h3>
        </div>
        <span className="text-xs text-muted-foreground">
          {findings.length} result{findings.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Contenu */}
      {findings.length === 0 && hasActiveConnector ? (
        <FirstScanCTA />
      ) : (
        <DataTable<Finding>
          columns={columns}
          data={findings}
          rowKey={(row) => row.id}
          emptyMessage="Findings will appear here once the backend has completed its first scan and data sources are configured."
          className="border-0 rounded-none"
        />
      )}
    </div>
  );
}
