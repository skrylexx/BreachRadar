/**
 * APIStatusCards — Grille de statut des connecteurs
 * Affiche TOUS les connecteurs (configurés ou non).
 * Vert = actif/opérationnel  |  Rouge = non configuré / erreur
 */

import { CheckCircle, XCircle, HelpCircle, Plug } from "lucide-react";

export interface ConnectorStatus {
  service_name: string;
  service_label: string;
  configured: boolean;
  is_active: boolean;
  last_test_success: boolean | null;
}

// ─── Indicateur de statut ───────────────────────────────────────────────────────────
function StatusDot({ status }: { status: "ok" | "error" | "unknown" }) {
  const map = {
    ok:      { Icon: CheckCircle, cls: "text-emerald-400" },
    error:   { Icon: XCircle,     cls: "text-red-400" },
    unknown: { Icon: HelpCircle,  cls: "text-yellow-400" },
  };
  const { Icon, cls } = map[status];
  return <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${cls}`} strokeWidth={1.5} />;
}

function resolveStatus(c: ConnectorStatus): "ok" | "error" | "unknown" {
  if (!c.configured || !c.is_active) return "error";
  if (c.last_test_success === true)  return "ok";
  if (c.last_test_success === false) return "error";
  return "unknown"; // null = test pas encore effectué
}

function resolveLabel(c: ConnectorStatus): string {
  if (!c.configured)                 return "Not configured";
  if (!c.is_active)                  return "Inactive";
  if (c.last_test_success === true)  return "Operational";
  if (c.last_test_success === false) return "Error";
  return "Not tested";
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
            const status = resolveStatus(c);
            const label  = resolveLabel(c);
            return (
              <div
                key={c.service_name}
                className={
                  "flex items-start gap-1.5 p-2 rounded-md border " +
                  (status === "ok"
                    ? "bg-emerald-500/5 border-emerald-500/20"
                    : status === "error"
                    ? "bg-red-500/5 border-red-500/20"
                    : "bg-yellow-500/5 border-yellow-500/20")
                }
              >
                <StatusDot status={status} />
                <div className="min-w-0">
                  <p className="text-xs font-medium text-foreground truncate">
                    {c.service_label}
                  </p>
                  <p className={"text-xs " + (
                    status === "ok"
                      ? "text-emerald-400"
                      : status === "error"
                      ? "text-red-400/80"
                      : "text-yellow-400/80"
                  )}>
                    {label}
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
