/**
 * StatusDot — Indicateur de statut de source
 * Utilisé pour les connecteurs, sources CVE, sources custom.
 *
 * Statuts : ok | warning | error | unknown
 */

import { cn } from "@/lib/utils";

export type SourceStatus = "ok" | "warning" | "error" | "unknown";

interface StatusDotProps {
  status: SourceStatus;
  className?: string;
  /** Afficher le label textuel à côté du point */
  label?: boolean;
}

const STATUS_CONFIG: Record<
  SourceStatus,
  { color: string; pingColor: string; text: string; label: string }
> = {
  ok: {
    color: "bg-green-500",
    pingColor: "bg-green-400",
    text: "text-green-400",
    label: "Opérationnel",
  },
  warning: {
    color: "bg-yellow-500",
    pingColor: "bg-yellow-400",
    text: "text-yellow-400",
    label: "Dégradé",
  },
  error: {
    color: "bg-red-500",
    pingColor: "bg-red-400",
    text: "text-red-400",
    label: "Erreur",
  },
  unknown: {
    color: "bg-slate-500",
    pingColor: "bg-slate-400",
    text: "text-slate-400",
    label: "Inconnu",
  },
};

export function StatusDot({ status, className, label = false }: StatusDotProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;

  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      {/* Point avec animation ping pour ok/warning */}
      <span className="relative flex h-2 w-2">
        {(status === "ok" || status === "warning") && (
          <span
            className={cn(
              "animate-ping absolute inline-flex h-full w-full rounded-full opacity-50",
              config.pingColor
            )}
          />
        )}
        <span
          className={cn("relative inline-flex rounded-full h-2 w-2", config.color)}
          aria-label={`Status: ${config.label}`}
        />
      </span>

      {label && (
        <span className={cn("text-xs font-medium", config.text)}>{config.label}</span>
      )}
    </span>
  );
}
