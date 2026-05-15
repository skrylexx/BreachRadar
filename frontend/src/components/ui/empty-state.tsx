/**
 * EmptyState — État vide standard BreachRadar
 * Affiché quand une liste/tableau ne contient aucune donnée.
 *
 * Props :
 *   - icon    : composant Lucide icon
 *   - title   : titre principal
 *   - message : description de l'état vide
 *   - action  : CTA button (optionnel)
 */

import { type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateAction {
  label: string;
  onClick?: () => void;
  href?: string;
}

interface EmptyStateProps {
  icon?: LucideIcon;
  title?: string;
  message: string;
  action?: EmptyStateAction;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  message,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 px-6 text-center",
        className
      )}
      aria-live="polite"
    >
      {/* Icône avec halo radar */}
      {Icon && (
        <div className="relative mb-4">
          <div className="w-14 h-14 rounded-full bg-radar/10 border border-radar/20 flex items-center justify-center">
            <Icon className="w-6 h-6 text-radar/60" strokeWidth={1.5} />
          </div>
          {/* Anneau externe */}
          <div className="absolute inset-0 rounded-full border border-radar/10 animate-ping opacity-30" />
        </div>
      )}

      {title && (
        <h3 className="text-sm font-semibold text-foreground mb-1">{title}</h3>
      )}
      <p className="text-sm text-muted-foreground max-w-xs">{message}</p>

      {action && (
        <div className="mt-4">
          {action.href ? (
            <a
              href={action.href}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md
                         bg-radar/10 text-radar text-xs font-medium border border-radar/20
                         hover:bg-radar/20 transition-colors"
            >
              {action.label}
            </a>
          ) : (
            <button
              onClick={action.onClick}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md
                         bg-radar/10 text-radar text-xs font-medium border border-radar/20
                         hover:bg-radar/20 transition-colors"
            >
              {action.label}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
