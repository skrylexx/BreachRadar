/**
 * i18n — Internationalisation BreachRadar WebUI
 * Langues supportées : English (défaut), Français
 * Implémentation : dictionnaire statique (next-intl à intégrer phase suivante)
 */

export type Locale = "en" | "fr";

export const defaultLocale: Locale = "en";

export const translations = {
  en: {
    // Navigation
    "nav.dashboard": "Dashboard",
    "nav.scans": "Scans",
    "nav.api_keys": "API Keys",
    "nav.users": "Users",
    "nav.changelog": "Changelog",

    // Auth
    "auth.sign_in": "Sign in",
    "auth.sign_out": "Sign out",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.mfa_code": "Authenticator code",
    "auth.forgot_password": "Forgot password?",
    "auth.error.invalid_credentials": "Invalid email or password",
    "auth.error.account_disabled": "Account disabled",
    "auth.error.password_expired": "Password expired - please reset",

    // Dashboard
    "dashboard.title": "Dashboard",
    "dashboard.last_scan": "Last scan",
    "dashboard.total_findings": "Total findings",
    "dashboard.critical": "Critical",
    "dashboard.detection_volume": "Detection Volume",
    "dashboard.connectors": "Connectors",
    "dashboard.latest_findings": "Latest Findings",

    // Severities
    "severity.critical": "CRITICAL",
    "severity.high": "HIGH",
    "severity.medium": "MEDIUM",
    "severity.low": "LOW",
    "severity.none": "NONE",

    // Scans
    "scans.trigger": "Trigger scan",
    "scans.running": "Scan in progress...",
    "scans.completed": "Completed",
    "scans.failed": "Failed",

    // Common
    "common.loading": "Loading...",
    "common.error": "An error occurred",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.confirm": "Confirm",
  },

  fr: {
    // Navigation
    "nav.dashboard": "Tableau de bord",
    "nav.scans": "Scans",
    "nav.api_keys": "Clés API",
    "nav.users": "Utilisateurs",
    "nav.changelog": "Changelog",

    // Auth
    "auth.sign_in": "Se connecter",
    "auth.sign_out": "Se déconnecter",
    "auth.email": "Email",
    "auth.password": "Mot de passe",
    "auth.mfa_code": "Code authentificateur",
    "auth.forgot_password": "Mot de passe oublié ?",
    "auth.error.invalid_credentials": "Email ou mot de passe incorrect",
    "auth.error.account_disabled": "Compte désactivé",
    "auth.error.password_expired": "Mot de passe expiré - veuillez le renouveler",

    // Dashboard
    "dashboard.title": "Tableau de bord",
    "dashboard.last_scan": "Dernier scan",
    "dashboard.total_findings": "Trouvailles totales",
    "dashboard.critical": "Critique",
    "dashboard.detection_volume": "Volume de détections",
    "dashboard.connectors": "Connecteurs",
    "dashboard.latest_findings": "Dernières trouvailles",

    // Severities
    "severity.critical": "CRITIQUE",
    "severity.high": "ÉLEVÉ",
    "severity.medium": "MOYEN",
    "severity.low": "FAIBLE",
    "severity.none": "AUCUN",

    // Scans
    "scans.trigger": "Lancer un scan",
    "scans.running": "Scan en cours...",
    "scans.completed": "Terminé",
    "scans.failed": "Échec",

    // Common
    "common.loading": "Chargement...",
    "common.error": "Une erreur est survenue",
    "common.save": "Enregistrer",
    "common.cancel": "Annuler",
    "common.delete": "Supprimer",
    "common.confirm": "Confirmer",
  },
} satisfies Record<Locale, Record<string, string>>;

type TranslationKey = keyof typeof translations.en;

export function t(key: TranslationKey, locale: Locale = defaultLocale): string {
  return translations[locale][key] ?? translations.en[key] ?? key;
}
