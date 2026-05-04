"use client";

/**
 * APIStatusCards — Cards de statut des connecteurs OSINT
 * Design : bordure latérale colorée (vert=ok, rouge=ko), badge statut.
 * Affiche tous les connecteurs configurés ET non-configurés.
 */

import { CheckCircle2, XCircle, Clock, Minus } from "lucide-react";

interface APIKeyStatus {
  service_name: string;
  service_label: string;
  configured: boolean;
  is_active: boolean;
  last_test_success: boolean | null;
}

interface APIStatusCardsProps {
  statuses: APIKeyStatus[];
}

// ─── Composant carte individuelle ─────────────────────────────────────────────
function StatusCard({ status }: { status: APIKeyStatus }) {
  const isOk = status.configured && status.is_active && status.last_test_success !== false;
  const isError = !status.configured || !status.is_active || status.last_test_success === false;
  const isPending = status.configured && status.last_test_success === null;

  const borderClass = isOk ? "card-status-ok"
    : isError ? "card-status-error"
    : "card-status-warning";

  return (
    <div className={`card-soc px-3 py-2.5 ${borderClass} flex items-center gap-2.5 min-w-[140px]`}>
      {/* Icône de statut */}
      <div className="flex-shrink-0">
        {isOk ? (
          <CheckCircle2 className="w-4 h-4 text-green-400" strokeWidth={1.5} />
        ) : isPending ? (
          <Clock className="w-4 h-4 text-yellow-400" strokeWidth={1.5} />
        ) : isError ? (
          <XCircle className="w-4 h-4 text-red-400" strokeWidth={1.5} />
        ) : (
          <Minus className="w-4 h-4 text-muted-foreground" strokeWidth={1.5} />
        )}
      </div>

      {/* Nom du service */}
      <div className="flex flex-col min-w-0">
        <span className="text-xs font-semibold text-foreground truncate">
          {status.service_label}
        </span>
        <span className="text-[10px] font-data text-muted-foreground">
          {!status.configured ? "Not configured"
           : isPending ? "Not tested"
           : isOk ? "Operational"
           : "Error"}
        </span>
      </div>
    </div>
  );
}

// ─── Composant liste ──────────────────────────────────────────────────────────
export function APIStatusCards({ statuses }: APIStatusCardsProps) {
  const configured = statuses.filter((s) => s.configured);
  const unconfigured = statuses.filter((s) => !s.configured);
  const activeCount = configured.filter((s) => s.is_active && s.last_test_success !== false).length;

  return (
    <div className="space-y-3">
      {/* Résumé */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Connectors</h3>
        <span className="text-xs text-muted-foreground">
          <span className="text-green-400 font-medium">{activeCount}</span>
          /{statuses.length} active
        </span>
      </div>

      {/* Cards configurées */}
      <div className="flex flex-wrap gap-2">
        {configured.map((status) => (
          <StatusCard key={status.service_name} status={status} />
        ))}

        {/* Bouton "voir les non-configurés" (collapsible via details) */}
        {unconfigured.length > 0 && (
          <details className="group">
            <summary className="cursor-pointer text-xs text-muted-foreground
                                hover:text-foreground transition-colors
                                flex items-center gap-1 px-2 py-2">
              +{unconfigured.length} not configured
            </summary>
            <div className="flex flex-wrap gap-2 mt-2">
              {unconfigured.map((status) => (
                <StatusCard key={status.service_name} status={status} />
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
