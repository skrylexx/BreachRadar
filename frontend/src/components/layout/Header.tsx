"use client";

/**
 * Header — BreachRadar WebUI
 * Content: current page title, dark mode switch (always dark),
 *          language indicator (EN/FR), user menu.
 */

import { Bell, Globe, LogOut, Menu, Settings, User, X } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
import { useSidebarStore } from "@/lib/store";
import { NotificationDropdown } from "./NotificationDropdown";
import { useEffect, useState } from "react";

export function Header() {
  const pathname = usePathname();
  const t = useTranslations("Header");
  const { isOpen, toggle } = useSidebarStore();
  
  const getPageTitle = (path: string) => {
    if (path === "/") return t("dashboard");
    if (path.startsWith("/scans")) return t("scans");
    if (path.startsWith("/reports")) return t("reports");
    if (path.startsWith("/alerts/ransomware")) return t("alerts_ransomware");
    if (path.startsWith("/alerts/cve")) return t("alerts_cve");
    if (path.startsWith("/admin/users")) return t("admin_users");
    if (path.startsWith("/admin/api-keys")) return t("admin_api_keys");
    if (path.startsWith("/profile")) return t("profile");
    if (path.startsWith("/tools/hibp")) return t("tools_hibp");
    if (path.startsWith("/tools/github")) return t("tools_github");
    if (path.startsWith("/tools/ransomlook")) return t("tools_ransomlook");
    if (path.startsWith("/tools/leakcheck")) return t("tools_leakcheck");
    if (path.startsWith("/tools/urlscan")) return t("tools_urlscan");
    if (path.startsWith("/tools/dehashed")) return t("tools_dehashed");
    if (path.startsWith("/tools/otx")) return t("tools_otx");
    if (path.startsWith("/tools/intelx")) return t("tools_intelx");
    if (path.startsWith("/admin/smtp")) return t("admin_smtp");
    if (path.startsWith("/admin/scheduling")) return t("admin_scheduling");
    if (path.startsWith("/admin/audit")) return t("admin_audit");
    if (path.startsWith("/admin/settings")) return t("admin_settings");
    if (path === "/admin") return t("administration");
    if (path === "/changelog") return t("changelog");
    return "BreachRadar";
  };

  const title = getPageTitle(pathname);

  return (
    <header
      className="h-14 flex-shrink-0 flex items-center justify-between
                 px-4 sm:px-6 border-b border-border/50 bg-card/50 backdrop-blur-sm z-40 relative"
    >
      {/* Page title + Mobile Menu */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="lg:hidden p-2 -ml-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          aria-label={isOpen ? t("close_menu") : t("open_menu")}
        >
          {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        
        <h2 className="text-sm font-semibold text-foreground truncate max-w-[120px] sm:max-w-none">
          {title}
        </h2>
        {/* Minimalist Breadcrumb */}
        <span className="text-xs text-muted-foreground/50 font-data hidden md:block">
          breachradar / {title.toLowerCase()}
        </span>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-1 sm:gap-2">

        {/* Language selector */}
        <LanguageSelector />

        {/* Notifications */}
        <NotificationDropdown />

        {/* User menu */}
        <UserMenu />
      </div>
    </header>
  );
}

// ─── Language Selector ─────────────────────────────────────────────────────
function LanguageSelector() {
  const router = useRouter();
  const locale = useLocale();

  const changeLanguage = (newLocale: string) => {
    document.cookie = `NEXT_LOCALE=${newLocale}; path=/; max-age=31536000`;
    // A full refresh is more reliable to update Server Components
    window.location.reload();
  };

  return (
    <div className="relative group">
      <button
        id="header-language"
        className="sidebar-icon gap-1 flex items-center"
        title="Language"
        aria-label="Change language"
      >
        <Globe className="w-4 h-4" strokeWidth={1.5} />
        <span className="text-[10px] font-medium uppercase">{locale}</span>
      </button>

      {/* Language dropdown */}
      <div className="absolute right-0 top-full mt-1
                      bg-popover border border-border rounded-md shadow-lg
                      opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto
                      transition-opacity duration-150 z-50 min-w-[100px]">
        {[
          { code: "en", label: "English" },
          { code: "fr", label: "Français" },
        ].map((lang) => (
          <button
            key={lang.code}
            id={`lang-${lang.code}`}
            onClick={() => changeLanguage(lang.code)}
            className={`w-full text-left px-3 py-2 text-xs transition-colors first:rounded-t-md last:rounded-b-md ${
              locale === lang.code
                ? "bg-radar/15 text-radar font-medium"
                : "text-foreground hover:bg-accent"
            }`}
          >
            {lang.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── User Menu ─────────────────────────────────────────────────────────
function UserMenu() {
  const t = useTranslations("Common");
  const [email, setEmail] = useState<string>("admin@yourdomain.com");

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/auth/me`, {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          if (data.email) setEmail(data.email);
        }
      } catch (e) {
        console.error("Failed to fetch user in header", e);
      }
    };
    fetchUser();
  }, []);

  const handleLogout = async () => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    window.location.href = "/login";
  };

  return (
    <div className="relative group">
      <button
        id="header-user-menu"
        className="flex items-center justify-center w-9 h-9 rounded-md
                   hover:bg-accent transition-colors duration-150"
        aria-label="User menu"
      >
        <div className="w-7 h-7 rounded-full bg-radar/20 border border-radar/30
                        flex items-center justify-center flex-shrink-0">
          <User className="w-3.5 h-3.5 text-radar" strokeWidth={1.5} />
        </div>
      </button>

      {/* Invisible bridge to keep hover active between button and menu */}
      <div className="absolute top-full right-0 h-2 w-full pointer-events-auto" />

      {/* Dropdown */}
      <div className="absolute right-0 top-[calc(100%+4px)]
                      bg-popover border border-border rounded-md shadow-xl
                      opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto
                      transition-all duration-150 z-[100] min-w-[200px]
                      translate-y-1 group-hover:translate-y-0">
        <div className="px-4 py-3 border-b border-border/50">
          <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 mb-1">
            {t("connected_as")}
          </p>
          <p className="text-xs text-foreground font-data truncate">{email}</p>
        </div>

        <div className="p-1.5">
          <button
            id="user-menu-profile"
            onClick={() => window.location.href = "/profile"}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md
                       text-xs text-foreground hover:bg-accent transition-colors"
          >
            <User className="w-3.5 h-3.5" strokeWidth={1.5} />
            {t("my_profile")}
          </button>
          <button
            id="user-menu-settings"
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md
                       text-xs text-foreground hover:bg-accent transition-colors"
          >
            <Settings className="w-3.5 h-3.5" strokeWidth={1.5} />
            {t("settings")}
          </button>
          
          <div className="h-px bg-border/50 my-1.5" />
          
          <button
            id="user-menu-logout"
            onClick={handleLogout}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md
                       text-xs text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" strokeWidth={1.5} />
            {t("logout")}
          </button>
        </div>
      </div>
    </div>
  );
}
