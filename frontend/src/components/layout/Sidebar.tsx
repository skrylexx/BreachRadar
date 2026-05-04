"use client";

/**
 * Sidebar — BreachRadar WebUI
 * Design : fine barre latérale gauche, icônes uniquement, tooltip au survol.
 * Largeur : 56px (w-14) — maximise l'espace de données.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ScanSearch,
  KeyRound,
  Users,
  ScrollText,
  Shield,
} from "lucide-react";

// ─── Navigation items ─────────────────────────────────────────────────────────
const NAV_ITEMS = [
  {
    href: "/",
    icon: LayoutDashboard,
    label: "Dashboard",
    id: "nav-dashboard",
  },
  {
    href: "/scans",
    icon: ScanSearch,
    label: "Scans",
    id: "nav-scans",
  },
  {
    href: "/api-keys",
    icon: KeyRound,
    label: "API Keys",
    id: "nav-api-keys",
    adminOnly: true,
  },
  {
    href: "/users",
    icon: Users,
    label: "Users",
    id: "nav-users",
    adminOnly: true,
  },
  {
    href: "/changelog",
    icon: ScrollText,
    label: "Changelog",
    id: "nav-changelog",
  },
];

// ─── Composant ────────────────────────────────────────────────────────────────
export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="w-14 flex-shrink-0 flex flex-col
                 bg-card border-r border-border/50
                 py-4 z-20"
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative group" title="BreachRadar">
          <Shield
            className="w-7 h-7 text-radar animate-glow-pulse"
            strokeWidth={1.5}
          />
          {/* Tooltip */}
          <span className="absolute left-12 top-1/2 -translate-y-1/2
                           bg-popover text-popover-foreground text-xs
                           px-2 py-1 rounded border border-border
                           whitespace-nowrap opacity-0 group-hover:opacity-100
                           pointer-events-none transition-opacity duration-150 z-50">
            BreachRadar
          </span>
        </div>
      </div>

      {/* Séparateur */}
      <div className="w-8 mx-auto border-t border-border/50 mb-4" />

      {/* Navigation principale */}
      <nav className="flex-1 flex flex-col items-center gap-1 px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              id={item.id}
              title={item.label}
              className={`sidebar-icon group relative ${isActive ? "active" : ""}`}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="w-5 h-5" strokeWidth={1.5} />

              {/* Tooltip */}
              <span className="absolute left-12 top-1/2 -translate-y-1/2
                               bg-popover text-popover-foreground text-xs
                               px-2 py-1 rounded border border-border
                               whitespace-nowrap opacity-0 group-hover:opacity-100
                               pointer-events-none transition-opacity duration-150 z-50">
                {item.label}
                {item.adminOnly && (
                  <span className="ml-1 text-radar opacity-70">(Admin)</span>
                )}
              </span>

              {/* Indicateur actif */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2
                                 w-0.5 h-5 bg-radar rounded-r" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Version en bas */}
      <div className="flex items-center justify-center mt-auto">
        <span
          className="text-[10px] font-data text-muted-foreground/40 rotate-0"
          title="BreachRadar v1.0"
        >
          v1.0
        </span>
      </div>
    </aside>
  );
}
