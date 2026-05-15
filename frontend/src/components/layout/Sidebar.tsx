"use client";

/**
 * Sidebar — BreachRadar WebUI
 * Barre latérale gauche, icônes uniquement, tooltip au survol.
 * Logo : image PNG réelle (/images/logo_only-nobg.png) — fond transparent natif.
 *
 * Navigation couvre toutes les routes du TODO.md :
 *   - Dashboard, Scans, Reports
 *   - Tools (HIBP, GitHub, RansomLook, LeakCheck, URLScan)
 *   - Alerts (Ransomware, CVE)
 *   - Admin (Users, API Keys, SMTP, Scheduling, Audit, Settings)
 *   - Profile, Changelog
 */

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ScanSearch,
  FileText,
  ShieldAlert,
  Bug,
  Settings,
  Users,
  Key,
  ScrollText,
  User,
  ChevronDown,
  Mail,
  Clock,
  ClipboardList,
  Database,
  Github,
  Lock,
  Globe,
  Activity,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface NavItem {
  href: string;
  icon: React.ElementType;
  label: string;
  id: string;
  adminOnly?: boolean;
  children?: NavItem[];
}

// ─── Navigation items ──────────────────────────────────────────────────────────
const NAV_ITEMS: NavItem[] = [
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
    href: "/reports",
    icon: FileText,
    label: "Rapports",
    id: "nav-reports",
  },
  // Alertes
  {
    href: "/alerts/ransomware",
    icon: ShieldAlert,
    label: "Ransomware",
    id: "nav-alerts-ransomware",
  },
  {
    href: "/alerts/cve",
    icon: Bug,
    label: "CVE & Exploits",
    id: "nav-alerts-cve",
  },
  // Outils OSINT
  {
    href: "/tools/hibp",
    icon: Mail,
    label: "HIBP",
    id: "nav-tool-hibp",
  },
  {
    href: "/tools/github",
    icon: Github,
    label: "GitHub",
    id: "nav-tool-github",
  },
  {
    href: "/tools/ransomlook",
    icon: Activity,
    label: "RansomLook",
    id: "nav-tool-ransomlook",
  },
  {
    href: "/tools/leakcheck",
    icon: Database,
    label: "LeakCheck",
    id: "nav-tool-leakcheck",
  },
  {
    href: "/tools/urlscan",
    icon: Globe,
    label: "URLScan",
    id: "nav-tool-urlscan",
  },
];

const BOTTOM_ITEMS: NavItem[] = [
  {
    href: "/changelog",
    icon: ScrollText,
    label: "Changelog",
    id: "nav-changelog",
  },
  {
    href: "/profile",
    icon: User,
    label: "Mon profil",
    id: "nav-profile",
  },
];

const ADMIN_ITEMS: NavItem[] = [
  {
    href: "/admin/users",
    icon: Users,
    label: "Utilisateurs",
    id: "nav-admin-users",
    adminOnly: true,
  },
  {
    href: "/admin/api-keys",
    icon: Key,
    label: "Clés API",
    id: "nav-admin-api-keys",
    adminOnly: true,
  },
  {
    href: "/admin/smtp",
    icon: Mail,
    label: "SMTP",
    id: "nav-admin-smtp",
    adminOnly: true,
  },
  {
    href: "/admin/scheduling",
    icon: Clock,
    label: "Scheduling",
    id: "nav-admin-scheduling",
    adminOnly: true,
  },
  {
    href: "/admin/audit",
    icon: ClipboardList,
    label: "Audit trail",
    id: "nav-admin-audit",
    adminOnly: true,
  },
  {
    href: "/admin/settings",
    icon: Settings,
    label: "Paramètres",
    id: "nav-admin-settings",
    adminOnly: true,
  },
];

// ─── NavIcon — icône avec tooltip ─────────────────────────────────────────────
function NavIcon({ item, isActive }: { item: NavItem; isActive: boolean }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      id={item.id}
      title={item.label}
      className={cn("sidebar-icon group relative", isActive && "active")}
      aria-current={isActive ? "page" : undefined}
    >
      <Icon className="w-4.5 h-4.5" strokeWidth={1.5} />
      {/* Tooltip */}
      <span
        className="absolute left-12 top-1/2 -translate-y-1/2
                   bg-popover text-popover-foreground text-xs
                   px-2 py-1 rounded border border-border
                   whitespace-nowrap opacity-0 group-hover:opacity-100
                   pointer-events-none transition-opacity duration-150 z-50"
      >
        {item.label}
        {item.adminOnly && <span className="ml-1 text-radar opacity-70">(Admin)</span>}
      </span>
      {/* Indicateur actif */}
      {isActive && (
        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-radar rounded-r" />
      )}
    </Link>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────
export function Sidebar() {
  const pathname = usePathname();
  const [adminExpanded, setAdminExpanded] = useState(
    pathname.startsWith("/admin")
  );

  const isActive = (item: NavItem) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

  return (
    <aside
      className="w-14 flex-shrink-0 flex flex-col bg-card border-r border-border/50 py-3 z-20 overflow-y-auto custom-scrollbar"
      aria-label="Navigation principale"
    >
      {/* Logo */}
      <div className="flex items-center justify-center mb-4">
        <div className="relative group" title="BreachRadar">
          <Image
            src="/images/logo_only-nobg.png"
            alt="BreachRadar"
            width={32}
            height={32}
            className="w-8 h-8 object-contain"
            priority
          />
          <span
            className="absolute left-12 top-1/2 -translate-y-1/2
                       bg-popover text-popover-foreground text-xs font-semibold
                       px-2 py-1 rounded border border-border
                       whitespace-nowrap opacity-0 group-hover:opacity-100
                       pointer-events-none transition-opacity duration-150 z-50"
          >
            BreachRadar
          </span>
        </div>
      </div>

      <div className="w-8 mx-auto border-t border-border/50 mb-3" />

      {/* Navigation principale */}
      <nav className="flex-1 flex flex-col items-center gap-0.5 px-2">
        {NAV_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} />
        ))}

        {/* Séparateur Admin */}
        <div className="w-8 border-t border-border/50 my-2" />

        {/* Section Admin (collapsible) */}
        <button
          id="nav-admin-toggle"
          onClick={() => setAdminExpanded((v) => !v)}
          title="Administration"
          className={cn(
            "sidebar-icon group relative",
            pathname.startsWith("/admin") && "active"
          )}
        >
          <Lock className="w-4.5 h-4.5" strokeWidth={1.5} />
          <span
            className="absolute left-12 top-1/2 -translate-y-1/2
                       bg-popover text-popover-foreground text-xs
                       px-2 py-1 rounded border border-border
                       whitespace-nowrap opacity-0 group-hover:opacity-100
                       pointer-events-none transition-opacity duration-150 z-50 flex items-center gap-1"
          >
            Administration
            <ChevronDown
              className={cn(
                "w-3 h-3 transition-transform",
                adminExpanded && "rotate-180"
              )}
            />
          </span>
        </button>

        {adminExpanded &&
          ADMIN_ITEMS.map((item) => (
            <NavIcon key={item.href} item={item} isActive={isActive(item)} />
          ))}
      </nav>

      {/* Items bas de sidebar */}
      <div className="flex flex-col items-center gap-0.5 px-2 mt-2">
        <div className="w-8 border-t border-border/50 mb-2" />
        {BOTTOM_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} />
        ))}
      </div>

      {/* Version */}
      <div className="flex items-center justify-center mt-2">
        <span className="text-[10px] font-data text-muted-foreground/40" title="BreachRadar v1.0">
          v1.0
        </span>
      </div>
    </aside>
  );
}
