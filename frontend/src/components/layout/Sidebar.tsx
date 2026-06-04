"use client";

/**
 * Sidebar — BreachRadar WebUI
 * Adaptive: Fixed on Desktop, Overlay (drawer) on Mobile.
 */

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
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
  X,
} from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useSidebarStore } from "@/lib/store";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface NavItem {
  href: string;
  icon: React.ElementType;
  label: string;
  id: string;
  adminOnly?: boolean;
}

// ─── Navigation items ──────────────────────────────────────────────────────────
const NAV_ITEMS: NavItem[] = [
  { href: "/", icon: LayoutDashboard, label: "dashboard", id: "nav-dashboard" },
  { href: "/intelligence", icon: ScrollText, label: "intelligence", id: "nav-intelligence" },
  { href: "/scans", icon: ScanSearch, label: "scans", id: "nav-scans" },
  { href: "/reports", icon: FileText, label: "reports", id: "nav-reports" },
  { href: "/alerts/ransomware", icon: ShieldAlert, label: "ransomware", id: "nav-alerts-ransomware" },
  { href: "/alerts/cve", icon: Bug, label: "cve", id: "nav-alerts-cve" },
  { href: "/tools/hibp", icon: Mail, label: "hibp", id: "nav-tool-hibp" },
  { href: "/tools/github", icon: Github, label: "github", id: "nav-tool-github" },
  { href: "/tools/ransomlook", icon: Activity, label: "ransomlook", id: "nav-tool-ransomlook" },
  { href: "/tools/leakcheck", icon: Database, label: "leakcheck", id: "nav-tool-leakcheck" },
  { href: "/tools/urlscan", icon: Globe, label: "urlscan", id: "nav-tool-urlscan" },
];

const BOTTOM_ITEMS: NavItem[] = [
  { href: "/changelog", icon: ScrollText, label: "changelog", id: "nav-changelog" },
  { href: "/profile", icon: User, label: "profile", id: "nav-profile" },
];

const ADMIN_ITEMS: NavItem[] = [
  { href: "/admin/users", icon: Users, label: "users", id: "nav-admin-users", adminOnly: true },
  { href: "/admin/api-keys", icon: Key, label: "api_keys", id: "nav-admin-api-keys", adminOnly: true },
  { href: "/admin/smtp", icon: Mail, label: "smtp", id: "nav-admin-smtp", adminOnly: true },
  { href: "/admin/scheduling", icon: Clock, label: "scheduling", id: "nav-admin-scheduling", adminOnly: true },
  { href: "/admin/audit", icon: ClipboardList, label: "audit", id: "nav-admin-audit", adminOnly: true },
  { href: "/admin/settings", icon: Settings, label: "settings", id: "nav-admin-settings", adminOnly: true },
];

function NavIcon({ item, isActive, isExpanded, onClick }: { item: NavItem; isActive: boolean, isExpanded: boolean, onClick?: () => void }) {
  const Icon = item.icon;
  const t = useTranslations("Navigation");
  const label = t(item.label);

  return (
    <Link
      href={item.href}
      id={item.id}
      onClick={onClick}
      className={cn(
        "group relative flex items-center gap-3 w-full px-3 py-2 rounded-md transition-all duration-200",
        isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/50 text-muted-foreground hover:text-foreground"
      )}
    >
      <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
      <span className={cn(
        "text-sm font-medium whitespace-nowrap transition-all duration-300 overflow-hidden",
        isExpanded ? "opacity-100 w-auto translate-x-0" : "opacity-0 w-0 -translate-x-4"
      )}>
        {label}
      </span>
      {!isExpanded && (
        <span className="lg:flex hidden absolute left-14 top-1/2 -translate-y-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded border border-border whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50 shadow-md">
          {label}
        </span>
      )}
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("Navigation");
  const [isHovered, setIsHovered] = useState(false);
  const [adminExpanded, setAdminExpanded] = useState(pathname.startsWith("/admin"));
  const { isOpen, close } = useSidebarStore();

  useEffect(() => {
    close();
  }, [pathname, close]);

  const isActive = (item: NavItem) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

  const sidebarContent = (
    <>
      {/* Logo Section */}
      <div className={cn(
        "flex items-center mb-6 px-2 transition-all duration-300 h-16 overflow-hidden",
        (isHovered || isOpen) ? "justify-start" : "justify-center"
      )}>
        <div className="relative h-12 w-full flex items-center">
          <Image
            src="/images/logo_only-nobg.png"
            alt="BreachRadar"
            width={48}
            height={48}
            className={cn(
              "object-contain transition-all duration-300 flex-shrink-0 absolute",
              (isHovered || isOpen) ? "opacity-0 -translate-x-10" : "opacity-100 translate-x-0"
            )}
            style={{ 
              left: (isHovered || isOpen) ? '0' : '50%', 
              transform: (isHovered || isOpen) ? 'translateX(0)' : 'translateX(-50%)',
              width: 'auto',
              height: '36px'
            }}
            priority
          />
          <Image
            src="/images/logo_full-nobg.png"
            alt="BreachRadar"
            width={240}
            height={56}
            className={cn(
              "object-contain transition-all duration-300 flex-shrink-0 absolute left-2",
              (isHovered || isOpen) ? "opacity-100 translate-x-0 scale-100" : "opacity-0 translate-x-10 scale-90"
            )}
            style={{ 
              width: 'auto', 
              height: '48px',
              maxWidth: 'calc(100% - 16px)'
            }}
            priority
          />
        </div>
        {isOpen && (
          <button onClick={close} className="lg:hidden p-1 rounded-md hover:bg-accent ml-auto">
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        )}
      </div>

      {/* Main navigation */}
      <nav className="flex-1 flex flex-col gap-1 px-2 overflow-y-auto overflow-x-hidden scrollbar-hide">
        {NAV_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered || isOpen} onClick={isOpen ? close : undefined} />
        ))}

        <div className="w-full mt-4">
          <button
            onClick={() => setAdminExpanded((v) => !v)}
            className={cn(
              "group relative flex items-center gap-3 w-full px-3 py-2 rounded-md transition-all duration-200",
              pathname.startsWith("/admin") ? "text-foreground" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Lock className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
            <span className={cn(
              "text-sm font-medium whitespace-nowrap flex-1 text-left transition-all duration-300 overflow-hidden",
              (isHovered || isOpen) ? "opacity-100 w-auto" : "opacity-0 w-0"
            )}>
              {t("administration")}
            </span>
            {(isHovered || isOpen) && (
              <ChevronDown className={cn("w-4 h-4 transition-transform duration-200", adminExpanded && "rotate-180")} />
            )}
          </button>

          {adminExpanded && (
            <div className={cn("flex flex-col gap-1 mt-1 transition-all", !(isHovered || isOpen) && "items-center")}>
              {ADMIN_ITEMS.map((item) => (
                <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered || isOpen} onClick={isOpen ? close : undefined} />
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Footer */}
      <div className="flex flex-col gap-1 px-2 mt-auto pt-4 border-t border-border/50">
        {BOTTOM_ITEMS.map((item) => (
          <NavIcon key={item.href} item={item} isActive={isActive(item)} isExpanded={isHovered || isOpen} onClick={isOpen ? close : undefined} />
        ))}
        <div className="flex items-center justify-center py-2 h-8">
          <span className="text-[10px] font-data text-muted-foreground/30 whitespace-nowrap">
            {(isHovered || isOpen) ? "BreachRadar Version 0.3.0" : "v0.3.0"}
          </span>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={close}
        />
      )}

      {/* Sidebar Container */}
      <aside
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={cn(
          "fixed lg:relative inset-y-0 left-0 z-50 flex flex-col bg-card border-r border-border/50 py-3 transition-all duration-300 ease-in-out",
          isOpen ? "translate-x-0 w-64 shadow-2xl" : "-translate-x-full lg:translate-x-0",
          !isOpen && (isHovered ? "lg:w-64 shadow-xl" : "lg:w-16")
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
