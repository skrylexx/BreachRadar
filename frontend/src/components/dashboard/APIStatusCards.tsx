/**
 * APIStatusCards — Grille de statut des connecteurs
 * Reçoit les données du Server Component parent.
 * Affiche un empty state si aucun connecteur n'est retourné.
 */

import { CheckCircle, XCircle, HelpCircle, Plug } from "lucide-react";

interface ConnectorStatus {
  service_name: string;
  service_label: string;
  configured: boolean;
  is_active: boolean;
  last_test_success: boolean | null;
}

// ─── Indicateur de statut ─────────────────────────────────────────────────────
function StatusDot({ status }: { status: "ok" | "error" | "unknown" | "inactive" }) {
  const map = {
    ok:       { Icon: CheckCircle, cls: "text-emerald-400" },
    error:    { Icon: XCircle,     cls: "text-red-400" },
    unknown:  { Icon: HelpCircle,  cls: "text-yellow-400" },
    inactive: { Icon: HelpCircle,  cls: "text-muted-foreground/40" },
  };
  const { Icon, cls } = map[status];
  return <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${cls}`} strokeWidth={1.5} />;
}

function resolveStatus(c: ConnectorStatus): "ok" | "error" | "unknown" | "inactive" {
  if (!c.configured) return "inactive";
  if (!c.is_active)  return "inactive";
  if (c.last_test_success === true)  return "ok";
  if (c.last_test_success === false) return "error";
  return "unknown";
}

function resolveLabel(c: ConnectorStatus): string {
  if (!c.configured) return "Not configured";
  if (!c.is_active)  return "Inactive";
  if (c.last_test_success === true)  return "Operational";
  if (c.last_test_success === false) return "Error";
  return "Not tested";
}

// ─── Empty state ──────────────────────────────────────────────────────────────
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

// ─── Composant ────────────────────────────────────────────────────────────────
export function APIStatusCards({ statuses = [] }: { statuses?: ConnectorStatus[] }) {
  const active  = statuses.filter((s) => s.is_active && s.configured).length;
  const total   = statuses.length;

  // Séparer configurés / non configurés
  const configured   = statuses.filter((s) => s.configured);
  const unconfigured = statuses.filter((s) => !s.configured);

  return (
    <div className="flex flex-col h-full">
      {/* En-tête */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-foreground">Connectors</h3>
        {total > 0 && (
          <span className="text-xs text-muted-foreground">
            {active}/{total} active
          </span>
        )}
      </div>

      {/* Contenu */}
      {statuses.length === 0 ? (
        <EmptyConnectors />
      ) : (
        <div className="space-y-2">
          {/* Connecteurs configurés */}
          <div className="grid grid-cols-2 gap-2">
            {configured.map((c) => {
              const status = resolveStatus(c);
              const label  = resolveLabel(c);
              return (
                <div
                  key={c.service_name}
                  className="flex items-start gap-1.5 p-2 rounded-md bg-secondary/50 border border-border/40"
                >
                  <StatusDot status={status} />
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-foreground truncate">
                      {c.service_label}
                    </p>
                    <p className="text-xs text-muted-foreground">{label}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Connecteurs non configurés regroupés */}
          {unconfigured.length > 0 && (
            <p className="text-xs text-muted-foreground pt-1">
              +{unconfigured.length} not configured
            </p>
          )}
        </div>
      )}
    </div>
  );
}
