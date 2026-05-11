/**
 * APIStatusCards — Grille de statut des connecteurs
 * Affiche TOUS les connecteurs (configurés ou non).
 * Vert = actif/opérationnel  |  Rouge = non configuré / erreur
 */

import { Plug } from "lucide-react";
import type { ConnectorStatus } from "@/lib/api";
import { StatusDot, type SourceStatus } from "@/components/ui/status-dot";

function formatTime(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function resolveLabel(c: ConnectorStatus): string {
  if (!c.configured) return "Not configured";
  if (!c.is_active) return "Inactive";
  return c.status === "ok" ? "Operational" : c.status === "warning" ? "Degraded" : c.status === "error" ? "Error" : "Unknown";
}

// ─── Empty state (liste vide) ──────────────────────────────────────────────────────
function EmptyConnectors() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-8 text-center px-4">
      <Plug className="w-8 h-8 text-muted-foreground/30 mb-3" strokeWidth={1} />
      <p className="text-sm font-medium text-foreground mb-1">No connectors</p>
      <p className="text-xs text-muted-foreground">
        Configure data sources in Settings to start monitoring.
      </p>
    </div>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────────
export function APIStatusCards({ statuses = [] }: { statuses?: ConnectorStatus[] }) {
  const activeCount = statuses.filter((s) => s.is_active && s.configured).length;
  const total       = statuses.length;

  return (
    <div className="flex flex-col h-full">
      {/* En-tête */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-foreground">Connectors</h3>
        {total > 0 && (
          <span className="text-xs text-muted-foreground">
            {activeCount}/{total} active
          </span>
        )}
      </div>

      {/* Grille — tous les connecteurs, configurés ou non */}
      {total === 0 ? (
        <EmptyConnectors />
      ) : (
        <div className="grid grid-cols-2 gap-2 overflow-y-auto">
          {statuses.map((c) => {
            const status: SourceStatus = (!c.configured || !c.is_active) ? "error" : c.status;
            const label  = resolveLabel(c);
            return (
              <div
                key={c.name}
                className={
                  "flex flex-col gap-1 p-2 rounded-md border " +
                  (status === "ok"
                    ? "bg-green-500/5 border-green-500/20"
                    : status === "error"
                    ? "bg-red-500/5 border-red-500/20"
                    : status === "warning"
                    ? "bg-yellow-500/5 border-yellow-500/20"
                    : "bg-slate-500/5 border-slate-500/20")
                }
              >
                <div className="flex items-center gap-2">
                  <StatusDot status={status} />
                  <p className="text-xs font-medium text-foreground truncate uppercase tracking-wider">
                    {c.name}
                  </p>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <p className={"text-[10px] " + (
                    status === "ok" ? "text-green-400" :
                    status === "error" ? "text-red-400" :
                    status === "warning" ? "text-yellow-400" :
                    "text-slate-400"
                  )}>
                    {label}
                  </p>
                  <p className="text-[10px] text-muted-foreground font-data">
                    {formatTime(c.last_scan_at)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
