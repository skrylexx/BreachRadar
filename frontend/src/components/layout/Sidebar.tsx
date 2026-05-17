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

// ─── NavIcon — icône avec label (affiché à l'expansion) ──────────────────────
function NavIcon({ item, isActive, isExpanded }: { item: NavItem; isActive: boolean, isExpanded: boolean }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      id={item.id}
      className={cn(
        "sidebar-icon group relative flex items-center gap-3 w-full px-3 py-2 rounded-md transition-all duration-200",
        isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/50 text-muted-foreground hover:text-foreground"
      )}
      aria-current={isActive ? "page" : undefined}
    >
      <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
      
      {/* Label (visible seulement quand élargi) */}
      <span className={cn(
        "text-sm font-medium whitespace-nowrap transition-all duration-300 overflow-hidden",
        isExpanded ? "opacity-100 w-auto" : "opacity-0 w-0"
      )}>
        {item.label}
      </span>

      {/* Tooltip (seulement quand réduit) */}
      {!isExpanded && (
        <span
          className="absolute left-14 top-1/2 -translate-y-1/2
                     bg-popover text-popover-foreground text-xs
                     px-2 py-1 rounded border border-border
                     whitespace-nowrap opacity-0 group-hover:opacity-100
                     pointer-events-none transition-opacity duration-150 z-50 shadow-md"
        >
          {item.label}
          {item.adminOnly && <span className="ml-1 text-radar opacity-70">(Admin)</span>}
        </span>
      )}

      {/* Indicateur actif */}
      {isActive && (
        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-radar rounded-r" />
      )}
    </Link>
  );
}

// ─── Composant principal ───────────────────────────────────────────────────────
export function Sidebar() {
  const pathname = usePathname();
  const [isHovered, setIsHovered] = useState(false);
  const [adminExpanded, setAdminExpanded] = useState(
    pathname.startsWith("/admin")
  );

  const isActive = (item: NavItem) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

  return (
    <aside
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        "flex-shrink-0 flex flex-col bg-card border-r border-border/50 py-3 z-20 transition-all duration-300 ease-in-out overflow-x-hidden",
        isHovered ? "w-64" : "w-16"
      )}
      aria-label="Navigation principale"
    >
      {/* Logo Section */}
      <div className={cn(
        "flex items-center mb-6 px-4 transition-all duration-300",
        isHovered ? "justify-start gap-3" : "justify-center"
      )}>
        <Image
          src="/images/logo_only-nobg.png"
          alt="BreachRadar"
          width={32}
          height={32}
          className="w-8 h-8 object-contain flex-shrink-0"
          priority
        />
        <span className={cn(
          "font-bold text-lg tracking-tight text-foreground transition-all duration-300 overflow-hidden whitespace-nowrap",
          isHovered ? "opacity-100 w-auto" : "opacity-0 w-0"
        )}>
          BreachRadar
        </span>
      </div>

      {/* Navigation principale */}
      <nav className="flex-1 flex flex-col items-center gap-1 px-2 scrollbar-hide overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered} />
        ))}

        {/* Section Admin (collapsible) */}
        <div className="w-full mt-4">
          <button
            id="nav-admin-toggle"
            onClick={() => setAdminExpanded((v) => !v)}
            className={cn(
              "sidebar-icon group relative flex items-center gap-3 w-full px-3 py-2 rounded-md transition-all duration-200",
              pathname.startsWith("/admin") ? "text-foreground" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Lock className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
            <span className={cn(
              "text-sm font-medium whitespace-nowrap flex-1 text-left transition-all duration-300 overflow-hidden",
              isHovered ? "opacity-100 w-auto" : "opacity-0 w-0"
            )}>
              Administration
            </span>
            {isHovered && (
              <ChevronDown
                className={cn(
                  "w-4 h-4 transition-transform duration-200",
                  adminExpanded && "rotate-180"
                )}
              />
            )}
            {!isHovered && (
              <span className="absolute left-14 top-1/2 -translate-y-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded border border-border whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50">
                Administration
              </span>
            )}
          </button>

          {adminExpanded && (
            <div className={cn(
              "flex flex-col gap-1 mt-1 transition-all",
              !isHovered && "items-center"
            )}>
              {ADMIN_ITEMS.map((item) => (
                <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered} />
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Items bas de sidebar */}
      <div className="flex flex-col gap-1 px-2 mt-auto pt-4 border-t border-border/50">
        {BOTTOM_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered} />
        ))}
        
        {/* Version (seulement quand réduit ou en petit texte) */}
        <div className="flex items-center justify-center py-2">
          <span className="text-[10px] font-data text-muted-foreground/30">
            {isHovered ? "BreachRadar Version 1.0" : "v1.0"}
          </span>
        </div>
      </div>
    </aside>
  );
}
