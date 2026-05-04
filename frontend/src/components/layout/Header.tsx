"use client";

/**
 * Header — BreachRadar WebUI
 * Contenu : titre de la page courante, dark mode switch (toujours dark),
 *           indicateur de langue (EN/FR), menu utilisateur.
 */

import { Bell, Globe, LogOut, Settings, User } from "lucide-react";
import { usePathname } from "next/navigation";

// Mapping des chemins vers les titres de page
const PAGE_TITLES: Record<string, string> = {
  "/":          "Dashboard",
  "/scans":     "Scan Results",
  "/api-keys":  "API Keys",
  "/users":     "User Management",
  "/changelog": "Changelog",
};

function getPageTitle(pathname: string): string {
  return PAGE_TITLES[pathname] ?? "BreachRadar";
}

// ─── Composant ────────────────────────────────────────────────────────────────
export function Header() {
  const pathname = usePathname();
  const title = getPageTitle(pathname);

  return (
    <header
      className="h-14 flex-shrink-0 flex items-center justify-between
                 px-6 border-b border-border/50 bg-card/50 backdrop-blur-sm"
    >
      {/* Titre de la page */}
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-foreground">{title}</h2>
        {/* Breadcrumb minimaliste */}
        <span className="text-xs text-muted-foreground/50 font-data hidden sm:block">
          breachradar / {title.toLowerCase()}
        </span>
      </div>

      {/* Actions droite */}
      <div className="flex items-center gap-2">

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
  return (
    <div className="relative group">
      <button
        id="header-language"
        className="sidebar-icon gap-1"
        title="Language"
        aria-label="Change language"
      >
        <Globe className="w-4 h-4" strokeWidth={1.5} />
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
            className="w-full text-left px-3 py-2 text-xs text-foreground
                       hover:bg-accent transition-colors first:rounded-t-md last:rounded-b-md"
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
