"use client";

/**
 * Header — BreachRadar WebUI
 * Contenu : titre de la page courante, dark mode switch (toujours dark),
 *           indicateur de langue (EN/FR), menu utilisateur.
 */

import { Bell, Globe, LogOut, Menu, Settings, User, X } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useTranslations, useLocale } from "next-intl";
import { useSidebarStore } from "@/lib/store";

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
    // Fallbacks for tools and others can remain hardcoded or we can add them to translations later
    if (path.startsWith("/tools/hibp")) return "HIBP & Fuites Emails";
    if (path.startsWith("/tools/github")) return "GitHub & GitLab";
    if (path.startsWith("/tools/ransomlook")) return "RansomLook";
    if (path.startsWith("/tools/leakcheck")) return "LeakCheck";
    if (path.startsWith("/tools/urlscan")) return "URLScan";
    if (path.startsWith("/tools/dehashed")) return "Dehashed";
    if (path.startsWith("/tools/otx")) return "AlienVault OTX";
    if (path.startsWith("/tools/intelx")) return "Intelligence X";
    if (path.startsWith("/admin/smtp")) return "Configuration SMTP";
    if (path.startsWith("/admin/scheduling")) return "Scheduling";
    if (path.startsWith("/admin/audit")) return "Audit Trail";
    if (path.startsWith("/admin/settings")) return "Paramètres";
    if (path === "/admin") return "Administration";
    if (path === "/changelog") return "Changelog";
    return "BreachRadar";
  };

  const title = getPageTitle(pathname);

  return (
    <header
      className="h-14 flex-shrink-0 flex items-center justify-between
                 px-4 sm:px-6 border-b border-border/50 bg-card/50 backdrop-blur-sm"
    >
      {/* Titre de la page + Menu Mobile */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="lg:hidden p-2 -ml-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          aria-label={isOpen ? "Fermer le menu" : "Ouvrir le menu"}
        >
          {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        
        <h2 className="text-sm font-semibold text-foreground truncate max-w-[120px] sm:max-w-none">
          {title}
        </h2>
        {/* Breadcrumb minimaliste */}
        <span className="text-xs text-muted-foreground/50 font-data hidden md:block">
          breachradar / {title.toLowerCase()}
        </span>
      </div>

      {/* Actions droite */}
      <div className="flex items-center gap-1 sm:gap-2">

        {/* Sélecteur de langue */}
        <LanguageSelector />

        {/* Notifications (placeholder) */}
        <button
          id="header-notifications"
          className="sidebar-icon relative"
          title="Notifications"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" strokeWidth={1.5} />
          {/* Badge notification (exemple) */}
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full" />
        </button>

        {/* Menu utilisateur */}
        <UserMenu />
      </div>
    </header>
  );
}

// ─── Sélecteur de langue ─────────────────────────────────────────────────────
function LanguageSelector() {
  const router = useRouter();
  const locale = useLocale();

  const changeLanguage = (newLocale: string) => {
    document.cookie = `NEXT_LOCALE=${newLocale}; path=/; max-age=31536000`;
    router.refresh();
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

      {/* Dropdown langues */}
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

// ─── Menu utilisateur ─────────────────────────────────────────────────────────
function UserMenu() {
  const handleLogout = async () => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    window.location.href = "/login";
  };

  return (
    <div className="relative group">
      <button
        id="header-user-menu"
        className="flex items-center gap-2 px-2 py-1.5 rounded-md
                   hover:bg-accent transition-colors duration-150"
        aria-label="User menu"
      >
        <div className="w-7 h-7 rounded-full bg-radar/20 border border-radar/30
                        flex items-center justify-center">
          <User className="w-3.5 h-3.5 text-radar" strokeWidth={1.5} />
        </div>
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 top-full mt-1
                      bg-popover border border-border rounded-md shadow-lg
                      opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto
                      transition-opacity duration-150 z-50 min-w-[160px]">
        <div className="px-3 py-2 border-b border-border">
          <p className="text-xs font-medium text-foreground">Account</p>
          <p className="text-xs text-muted-foreground font-data truncate">admin@domain.com</p>
        </div>

        <div className="p-1">
          <button
            id="user-menu-settings"
            className="w-full flex items-center gap-2 px-2 py-1.5 rounded-sm
                       text-xs text-foreground hover:bg-accent transition-colors"
          >
            <Settings className="w-3.5 h-3.5" strokeWidth={1.5} />
            Settings
          </button>
          <button
            id="user-menu-logout"
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-2 py-1.5 rounded-sm
                       text-xs text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" strokeWidth={1.5} />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
