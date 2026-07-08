"use client";

/**
 * Sidebar — BreachRadar WebUI
 * Adaptive: Fixed on Desktop, Overlay (drawer) on Mobile.
 *
 * Dynamic behaviour:
 *   - Tool pages (HIBP, GitHub, etc.) whose API key is configured appear in
 *     the main navigation.
 *   - Tool pages without a configured key are collapsed under a
 *     "Disconnected Pages" (Pages non connectées) accordion at the bottom of
 *     the nav, so they remain accessible while staying out of the way.
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
  WifiOff,
} from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useSidebarStore, useApiKeyStatusStore } from "@/lib/store";
import { apiKeysPublicApi } from "@/lib/api";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface NavItem {
  href: string;
  icon: React.ElementType;
  label: string;
  id: string;
  adminOnly?: boolean;
  /**
   * If set, this item is only shown in the main nav when the given service has
   * an active API key configured.  When not configured, the item moves to the
   * "Disconnected Pages" accordion section.
   */
  requiresService?: string;
}

// ─── Navigation items ──────────────────────────────────────────────────────────

/** Always-visible pages — no API key required. */
const CORE_NAV_ITEMS: NavItem[] = [
  { href: "/", icon: LayoutDashboard, label: "dashboard", id: "nav-dashboard" },
  { href: "/intelligence", icon: ScrollText, label: "intelligence", id: "nav-intelligence" },
  { href: "/scans", icon: ScanSearch, label: "scans", id: "nav-scans" },
  { href: "/reports", icon: FileText, label: "reports", id: "nav-reports" },
  { href: "/alerts/ransomware", icon: ShieldAlert, label: "ransomware", id: "nav-alerts-ransomware" },
  { href: "/alerts/cve", icon: Bug, label: "cve", id: "nav-alerts-cve" },
];

/**
 * Tool pages gated behind API key configuration.
 * `requiresService` must match the service_name returned by the backend
 * (see SUPPORTED_SERVICES in api_keys.py).
 */
const TOOL_NAV_ITEMS: NavItem[] = [
  { href: "/tools/hibp",       icon: Mail,     label: "hibp",       id: "nav-tool-hibp",       requiresService: "hibp" },
  { href: "/tools/github",     icon: Github,   label: "github",     id: "nav-tool-github",     requiresService: "github" },
  { href: "/tools/ransomlook", icon: Activity, label: "ransomlook", id: "nav-tool-ransomlook", requiresService: "ransomlook_saas" },
  { href: "/tools/leakcheck",  icon: Database, label: "leakcheck",  id: "nav-tool-leakcheck",  requiresService: "leakcheck" },
  { href: "/tools/urlscan",    icon: Globe,    label: "urlscan",    id: "nav-tool-urlscan",    requiresService: "urlscan" },
];

const BOTTOM_ITEMS: NavItem[] = [
  { href: "/changelog", icon: ScrollText, label: "changelog", id: "nav-changelog" },
  { href: "/profile",   icon: User,       label: "profile",   id: "nav-profile" },
];

const ADMIN_ITEMS: NavItem[] = [
  { href: "/admin/users",       icon: Users,         label: "users",       id: "nav-admin-users",       adminOnly: true },
  { href: "/admin/api-keys",    icon: Key,           label: "api_keys",    id: "nav-admin-api-keys",    adminOnly: true },
  { href: "/admin/smtp",        icon: Mail,          label: "smtp",        id: "nav-admin-smtp",        adminOnly: true },
  { href: "/admin/scheduling",  icon: Clock,         label: "scheduling",  id: "nav-admin-scheduling",  adminOnly: true },
  { href: "/admin/audit",       icon: ClipboardList, label: "audit",       id: "nav-admin-audit",       adminOnly: true },
  { href: "/admin/settings",    icon: Settings,      label: "settings",    id: "nav-admin-settings",    adminOnly: true },
];

// ─── NavIcon ───────────────────────────────────────────────────────────────────

function NavIcon({
  item,
  isActive,
  isExpanded,
  onClick,
  dimmed = false,
}: {
  item: NavItem;
  isActive: boolean;
  isExpanded: boolean;
  onClick?: () => void;
  /** True for items in the "disconnected" accordion — rendered slightly muted. */
  dimmed?: boolean;
}) {
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
        isActive
          ? "bg-accent text-accent-foreground"
          : dimmed
          ? "hover:bg-accent/40 text-muted-foreground/60 hover:text-muted-foreground"
          : "hover:bg-accent/50 text-muted-foreground hover:text-foreground"
      )}
    >
      <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
      <span
        className={cn(
          "text-sm font-medium whitespace-nowrap transition-all duration-300 overflow-hidden",
          isExpanded ? "opacity-100 w-auto translate-x-0" : "opacity-0 w-0 -translate-x-4"
        )}
      >
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

// ─── CollapsibleSection ────────────────────────────────────────────────────────

/**
 * Generic accordion section used for both the Admin panel and the
 * "Disconnected Pages" block.
 */
function CollapsibleSection({
  icon: Icon,
  label,
  isExpanded,
  isHighlighted,
  defaultOpen,
  children,
  id,
}: {
  icon: React.ElementType;
  label: string;
  /** Whether the sidebar itself is wide (hovered / mobile open). */
  isExpanded: boolean;
  /** True when the current route is inside this section. */
  isHighlighted: boolean;
  defaultOpen: boolean;
  children: React.ReactNode;
  id: string;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="w-full mt-4">
      <button
        id={id}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "group relative flex items-center gap-3 w-full px-3 py-2 rounded-md transition-all duration-200",
          isHighlighted
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <Icon className="w-5 h-5 flex-shrink-0" strokeWidth={1.5} />
        <span
          className={cn(
            "text-sm font-medium whitespace-nowrap flex-1 text-left transition-all duration-300 overflow-hidden",
            isExpanded ? "opacity-100 w-auto" : "opacity-0 w-0"
          )}
        >
          {label}
        </span>
        {isExpanded && (
          <ChevronDown
            className={cn(
              "w-4 h-4 transition-transform duration-200",
              open && "rotate-180"
            )}
          />
        )}
        {/* Tooltip when sidebar is collapsed */}
        {!isExpanded && (
          <span className="lg:flex hidden absolute left-14 top-1/2 -translate-y-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded border border-border whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50 shadow-md">
            {label}
          </span>
        )}
      </button>

      {open && (
        <div
          className={cn(
            "flex flex-col gap-1 mt-1 transition-all",
            !isExpanded && "items-center"
          )}
        >
          {children}
        </div>
      )}
    </div>
  );
}

// ─── Sidebar ───────────────────────────────────────────────────────────────────

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("Navigation");
  const [isHovered, setIsHovered] = useState(false);
  const { isOpen, close } = useSidebarStore();

  // API key status store
  const { configuredStatus, loading, setConfiguredStatus, setLoading } =
    useApiKeyStatusStore();

  // Fetch configured status once on mount (if not already loaded).
  useEffect(() => {
    if (configuredStatus !== null || loading) return;

    setLoading(true);
    apiKeysPublicApi
      .getConfiguredStatus()
      .then((statuses) => {
        const map: Record<string, boolean> = {};
        for (const s of statuses) {
          map[s.service_name] = s.configured;
        }
        setConfiguredStatus(map);
      })
      .catch(() => {
        // On error (e.g. not authenticated yet), keep configuredStatus null.
        // All tools will fall into the "disconnected" bucket — safe default.
        setLoading(false);
      });
  }, [configuredStatus, loading, setConfiguredStatus, setLoading]);

  const isActive = (item: NavItem) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

  const isExpanded = isHovered || isOpen;

  // Split tool items into connected / disconnected based on API key status.
  // While loading or if status is unknown, treat all tools as disconnected.
  const connectedTools = TOOL_NAV_ITEMS.filter(
    (item) =>
      item.requiresService && configuredStatus?.[item.requiresService] === true
  );
  const disconnectedTools = TOOL_NAV_ITEMS.filter(
    (item) =>
      !item.requiresService || configuredStatus?.[item.requiresService] !== true
  );

  // Whether any disconnected tool is currently active (to highlight the accordion)
  const isDisconnectedSectionActive = disconnectedTools.some(isActive);

  const sidebarContent = (
    <>
      {/* Logo Section */}
      <div
        className={cn(
          "flex items-center mb-6 px-2 transition-all duration-300 h-16 overflow-hidden",
          isExpanded ? "justify-start" : "justify-center"
        )}
      >
        <div className="relative h-12 w-full flex items-center">
          <Image
            src="/images/logo_only-nobg.png"
            alt="BreachRadar"
            width={48}
            height={48}
            className={cn(
              "object-contain transition-all duration-300 flex-shrink-0 absolute",
              isExpanded ? "opacity-0 -translate-x-10" : "opacity-100 translate-x-0"
            )}
            style={{
              left: isExpanded ? "0" : "50%",
              transform: isExpanded ? "translateX(0)" : "translateX(-50%)",
              width: "auto",
              height: "36px",
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
              isExpanded
                ? "opacity-100 translate-x-0 scale-100"
                : "opacity-0 translate-x-10 scale-90"
            )}
            style={{
              width: "auto",
              height: "48px",
              maxWidth: "calc(100% - 16px)",
            }}
            priority
          />
        </div>
        {isOpen && (
          <button
            onClick={close}
            className="lg:hidden p-1 rounded-md hover:bg-accent ml-auto"
          >
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        )}
      </div>

      {/* Main navigation */}
      <nav className="flex-1 flex flex-col gap-1 px-2 overflow-y-auto overflow-x-hidden scrollbar-hide">
        {/* Always-visible core pages */}
        {CORE_NAV_ITEMS.map((item) => (
          <NavIcon
            key={item.href}
            item={item}
            isActive={isActive(item)}
            isExpanded={isExpanded}
            onClick={isOpen ? close : undefined}
          />
        ))}

        {/* Connected tool pages — shown directly in the main nav */}
        {connectedTools.map((item) => (
          <NavIcon
            key={item.href}
            item={item}
            isActive={isActive(item)}
            isExpanded={isExpanded}
            onClick={isOpen ? close : undefined}
          />
        ))}

        {/* Disconnected Pages accordion */}
        {disconnectedTools.length > 0 && (
          <CollapsibleSection
            id="nav-disconnected-pages"
            icon={WifiOff}
            label={t("disconnectedPages")}
            isExpanded={isExpanded}
            isHighlighted={isDisconnectedSectionActive}
            defaultOpen={isDisconnectedSectionActive}
          >
            {disconnectedTools.map((item) => (
              <NavIcon
                key={item.href}
                item={item}
                isActive={isActive(item)}
                isExpanded={isExpanded}
                onClick={isOpen ? close : undefined}
                dimmed
              />
            ))}
          </CollapsibleSection>
        )}

        {/* Administration accordion */}
        <CollapsibleSection
          id="nav-administration"
          icon={Lock}
          label={t("administration")}
          isExpanded={isExpanded}
          isHighlighted={pathname.startsWith("/admin")}
          defaultOpen={pathname.startsWith("/admin")}
        >
          {ADMIN_ITEMS.map((item) => (
            <NavIcon
              key={item.href}
              item={item}
              isActive={isActive(item)}
              isExpanded={isExpanded}
              onClick={isOpen ? close : undefined}
            />
          ))}
        </CollapsibleSection>
      </nav>

      {/* Footer */}
      <div className="flex flex-col gap-1 px-2 mt-auto pt-4 border-t border-border/50">
        {BOTTOM_ITEMS.map((item) => (
          <NavIcon
            key={item.href}
            item={item}
            isActive={isActive(item)}
            isExpanded={isExpanded}
            onClick={isOpen ? close : undefined}
          />
        ))}
        <div className="flex items-center justify-center py-2 h-8">
          <span className="text-[10px] font-data text-muted-foreground/30 whitespace-nowrap">
            {isExpanded ? "BreachRadar Version 0.5.0.1" : "v0.5.0.1"}
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
