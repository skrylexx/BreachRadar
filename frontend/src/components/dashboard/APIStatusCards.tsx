/**
 * APIStatusCards — Grille de statut des connecteurs
 * Affiche TOUS les connecteurs (configurés ou non).
 * Vert = actif/opérationnel  |  Rouge = non configuré / erreur
 */

import { Plug } from "lucide-react";
import type { ConnectorStatus } from "@/lib/api";
import { StatusDot, type SourceStatus } from "@/components/ui/status-dot";
import { useTranslations } from "next-intl";

function formatTime(iso: string | null, t: any): string {
  if (!iso) return t("Common.never");
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return t("Common.just_now");
  if (mins < 60) return t("Common.time_ago", { time: mins, unit: t("Common.unit_m") });
  const hours = Math.floor(mins / 60);
  if (hours < 24) return t("Common.time_ago", { time: hours, unit: t("Common.unit_h") });
  return t("Common.time_ago", { time: Math.floor(hours / 24), unit: t("Common.unit_d") });
}

function resolveLabel(c: ConnectorStatus, t: any): string {
  if (c.is_mock) return t("Connectors.demo_mode");
  if (!c.configured) return t("Connectors.not_configured");
  if (!c.is_active) return t("Connectors.inactive");
  return c.status === "ok" ? t("Connectors.operational") : c.status === "warning" ? t("Connectors.degraded") : c.status === "error" ? t("Connectors.error") : "Unknown";
}

function EmptyConnectors() {
  const t = useTranslations("Connectors");
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-3 opacity-40">
      <Plug className="w-8 h-8 text-muted-foreground stroke-1" />
      <p className="text-xs text-muted-foreground">
        {t("no_connectors")}
      </p>
    </div>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────────
export function APIStatusCards({ statuses = [] }: { statuses?: ConnectorStatus[] }) {
  const t = useTranslations();
  const activeCount = statuses.filter((s) => (s.is_active && s.configured) || s.is_mock).length;
  const total       = statuses.length;

  return (
    <div className="flex flex-col h-full">
      {/* En-tête */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-foreground">{t("Connectors.title")}</h3>
        {total > 0 && (
          <span className="text-xs text-muted-foreground">
            {t("Connectors.active_count", { active: activeCount, total: total })}
          </span>
        )}
      </div>

      {/* Grille — tous les connecteurs, configurés ou non */}
      {total === 0 ? (
        <EmptyConnectors />
      ) : (
        <div className="grid grid-cols-2 gap-2 overflow-y-auto">
          {statuses.map((c) => {
            let status: SourceStatus = "unknown";
            if (c.is_mock || c.status === "mock") {
              status = "warning";
            } else if (!c.configured || !c.is_active) {
              status = "error";
            } else if (c.status === "ok" || c.status === "warning" || c.status === "error") {
              status = c.status;
            }
            
            const label  = resolveLabel(c, t);
            return (
              <div
                key={c.name}
                className={
                  "flex flex-col gap-1 p-2 rounded-md border " +
                  (c.is_mock 
                    ? "bg-orange-500/5 border-orange-500/20"
                    : status === "ok"
                    ? "bg-green-500/5 border-green-500/20"
                    : status === "error"
                    ? "bg-red-500/5 border-red-500/20"
                    : status === "warning"
                    ? "bg-yellow-500/5 border-yellow-500/20"
                    : "bg-slate-500/5 border-slate-500/20")
                }
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <StatusDot status={status} />
                    <p className="text-xs font-medium text-foreground truncate uppercase tracking-wider">
                      {c.name}
                    </p>
                  </div>
                  {c.is_mock && (
                    <span className="text-[8px] font-bold px-1 rounded bg-orange-500/20 text-orange-400 border border-orange-500/30">
                      {t("Connectors.mock_badge")}
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-between mt-1">
                  <p className={"text-[10px] " + (
                    c.is_mock ? "text-orange-400" :
                    status === "ok" ? "text-green-400" :
                    status === "error" ? "text-red-400" :
                    status === "warning" ? "text-yellow-400" :
                    "text-slate-400"
                  )}>
                    {label}
                  </p>
                  <p className="text-[10px] text-muted-foreground font-data">
                    {formatTime(c.last_scan_at, t)}
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
