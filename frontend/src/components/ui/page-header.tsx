/**
 * PageHeader — En-tête de page standard BreachRadar
 * Présent sur toutes les pages de la WebUI.
 *
 * Props :
 *   - title       : titre principal (h1)
 *   - description : sous-titre optionnel
 *   - breadcrumb  : tableau de segments [{ label, href? }]
 *   - children    : actions CTA (boutons, etc.) placées à droite
 */

import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbSegment {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumb?: BreadcrumbSegment[];
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  breadcrumb,
  children,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("mb-6", className)}>
      {/* Breadcrumb */}
      {breadcrumb && breadcrumb.length > 0 && (
        <nav
          aria-label="Breadcrumb"
          className="flex items-center gap-1 mb-2 text-xs text-muted-foreground font-data"
        >
          {breadcrumb.map((segment, idx) => (
            <span key={idx} className="flex items-center gap-1">
              {idx > 0 && <ChevronRight className="w-3 h-3 opacity-40" />}
              {segment.href ? (
                <Link
                  href={segment.href}
                  className="hover:text-foreground transition-colors"
                >
                  {segment.label}
                </Link>
              ) : (
                <span className="text-foreground/60">{segment.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}

      {/* Titre + actions */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-foreground tracking-tight">
            {title}
          </h1>
          {description && (
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          )}
        </div>

        {/* Slot actions CTA */}
        {children && (
          <div className="flex items-center gap-2 flex-shrink-0">{children}</div>
        )}
      </div>
    </div>
  );
}
