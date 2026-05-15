/**
 * SeverityBadge — Composant réutilisable de badge de sévérité
 * Utilisé partout où une sévérité doit être affichée (findings, CVE, alertes).
 *
 * Niveaux : CRITICAL | HIGH | MEDIUM | LOW | NONE | INFO
 */

import { cn } from "@/lib/utils";

export type SeverityLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE" | "INFO";

interface SeverityBadgeProps {
  level: SeverityLevel;
  className?: string;
  /** Afficher uniquement un point coloré (compact mode) */
  dot?: boolean;
}

const SEVERITY_CONFIG: Record<
  SeverityLevel,
  { label: string; className: string; dotColor: string }
> = {
  CRITICAL: {
    label: "CRITICAL",
    className: "badge-critical",
    dotColor: "bg-red-500",
  },
  HIGH: {
    label: "HIGH",
    className: "badge-high",
    dotColor: "bg-orange-500",
  },
  MEDIUM: {
    label: "MEDIUM",
    className: "badge-medium",
    dotColor: "bg-yellow-500",
  },
  LOW: {
    label: "LOW",
    className: "badge-low",
    dotColor: "bg-slate-400",
  },
  NONE: {
    label: "NONE",
    className: "badge-none",
    dotColor: "bg-green-500",
  },
  INFO: {
    label: "INFO",
    className: "badge-info",
    dotColor: "bg-blue-400",
  },
};

export function SeverityBadge({ level, className, dot = false }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[level] ?? SEVERITY_CONFIG.LOW;

  if (dot) {
    return (
      <span
        className={cn("inline-block w-2 h-2 rounded-full", config.dotColor, className)}
        title={config.label}
        aria-label={`Severity: ${config.label}`}
      />
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold tracking-wider uppercase",
        config.className,
        className
      )}
      aria-label={`Severity: ${config.label}`}
    >
      {config.label}
    </span>
  );
}
