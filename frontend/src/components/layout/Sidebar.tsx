"use client";

/**
 * Sidebar — BreachRadar WebUI
 * Barre latérale gauche, icônes uniquement, tooltip au survol.
 * Logo : SVG inline — pas de fond blanc, compatible dark/light mode.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ScanSearch,
  KeyRound,
  Users,
  ScrollText,
} from "lucide-react";

// ─── Navigation items ─────────────────────────────────────────────────────────
const NAV_ITEMS = [
  { href: "/",          icon: LayoutDashboard, label: "Dashboard", id: "nav-dashboard" },
  { href: "/scans",     icon: ScanSearch,      label: "Scans",     id: "nav-scans" },
  { href: "/api-keys",  icon: KeyRound,        label: "API Keys",  id: "nav-api-keys",  adminOnly: true },
  { href: "/users",     icon: Users,           label: "Users",     id: "nav-users",     adminOnly: true },
  { href: "/changelog", icon: ScrollText,      label: "Changelog", id: "nav-changelog" },
];

// ─── Logo SVG inline ────────────────────────────────────────────────────────────────
// Représentation vectorielle fidèle au logo BreachRadar :
// • Bouclier bleu marine (outline) à gauche
// • Lettre B ancrée au centre du bouclier
// • Arcs de radar cyan (à droite) partant de l'intérieur du bouclier
// Fond transparent — s'adapte au dark mode sans aucun traitement image.
function BreachRadarLogo({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="BreachRadar"
      role="img"
    >
      {/* — Bouclier (outline bleu marine) — */}
      <path
        d="M50 8 L82 22 L82 52 C82 68 66 82 50 90 C34 82 18 68 18 52 L18 22 Z"
        stroke="#1e3a5f"
        strokeWidth="5"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Ligne de division verticale au centre du bouclier */}
      <line x1="50" y1="8" x2="50" y2="90" stroke="#1e3a5f" strokeWidth="3.5" />

      {/* — Lettre B (bleu marine, moitié gauche du bouclier) — */}
      <path
        d="M32 30 L32 70 L44 70 C52 70 57 65 57 58 C57 53 54 49 50 48
           C53 46 56 43 56 38 C56 33 52 30 44 30 Z
           M38 36 L43 36 C47 36 50 38 50 42 C50 46 47 48 43 48 L38 48 Z
           M38 54 L44 54 C49 54 51 56 51 59 C51 63 48 64 44 64 L38 64 Z"
        fill="#1e3a5f"
      />

      {/* — Arcs de radar (cyan, moitié droite) — */}
      {/* Arc 1 — le plus proche */}
      <path
        d="M54 50 A8 8 0 0 1 62 42"
        stroke="#38bdf8"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      {/* Arc 2 */}
      <path
        d="M54 50 A18 18 0 0 1 72 32"
        stroke="#38bdf8"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
        opacity="0.85"
      />
      {/* Arc 3 — le plus lointain */}
      <path
        d="M54 50 A28 28 0 0 1 82 22"
        stroke="#38bdf8"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
        opacity="0.65"
      />
    </svg>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────────
export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="w-14 flex-shrink-0 flex flex-col bg-card border-r border-border/50 py-4 z-20"
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative group" title="BreachRadar">
          <BreachRadarLogo className="w-8 h-8" />
          <span
            className="absolute left-12 top-1/2 -translate-y-1/2
                       bg-popover text-popover-foreground text-xs
                       px-2 py-1 rounded border border-border
                       whitespace-nowrap opacity-0 group-hover:opacity-100
                       pointer-events-none transition-opacity duration-150 z-50"
          >
            BreachRadar
          </span>
        </div>
      </div>

      {/* Séparateur */}
      <div className="w-8 mx-auto border-t border-border/50 mb-4" />

      {/* Navigation */}
      <nav className="flex-1 flex flex-col items-center gap-1 px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

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
              <span
                className="absolute left-12 top-1/2 -translate-y-1/2
                           bg-popover text-popover-foreground text-xs
                           px-2 py-1 rounded border border-border
                           whitespace-nowrap opacity-0 group-hover:opacity-100
                           pointer-events-none transition-opacity duration-150 z-50"
              >
                {item.label}
                {item.adminOnly && (
                  <span className="ml-1 text-radar opacity-70">(Admin)</span>
                )}
              </span>
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-radar rounded-r" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Version */}
      <div className="flex items-center justify-center mt-auto">
        <span className="text-[10px] font-data text-muted-foreground/40" title="BreachRadar v1.0">
          v1.0
        </span>
      </div>
    </aside>
  );
}
