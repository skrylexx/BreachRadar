import { ScrollText, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";

/**
 * Page Changelog
 * Affiche l'historique des versions de BreachRadar.
 */

const RELEASES = [
  {
    version: "v0.5.0.1",
    date: "2026-06-04",
    type: "UI & i18n Polish",
    description: "Mise à jour de finition axée sur la cohérence visuelle, la confidentialité utilisateur et l'internationalisation complète des bannières.",
    changes: [
      { type: "feat", text: "Internationalisation complète de la bannière de surveillance du domaine (FR/EN)." },
      { type: "fix", text: "Suppression du placeholder d'email codé en dur dans le header pour une meilleure confidentialité." },
      { type: "fix", text: "Alignement des versions système dans l'ensemble de l'interface (Sidebar v0.5.0.1)." },
      { type: "fix", text: "Nettoyage de la Roadmap globale et suppression des tâches terminées." },
    ],
  },
  {
    version: "v0.5.0",
    date: "2026-06-03",
    type: "Open Source Launch",
    description: "Version historique marquant l'ouverture de BreachRadar en Open Source et l'introduction de configurations de sécurité dynamiques.",
    changes: [
      { type: "feat", text: "Ouverture officielle du projet en Open Source pour la communauté cyber." },
      { type: "feat", text: "Implémentation d'une Content Security Policy (CSP) dynamique basée sur les variables d'environnement." },
      { type: "feat", text: "Mises à jour fonctionnelles globales du code pour une meilleure modularité et extensibilité." },
      { type: "fix", text: "Optimisation de la configuration Next.js pour faciliter les déploiements multi-environnements." },
    ],
  },
  {
    version: "v0.4.1",
    date: "2026-06-03",
    type: "Security Hardening",
    description: "Mise à jour mineure axée sur le durcissement de la sécurité de l'application et la consolidation des flux CI/CD.",
    changes: [
      { type: "feat", text: "Durcissement des stratégies de validation des entrées et du contrôle d'accès basé sur les rôles (RBAC)." },
      { type: "fix", text: "Audit et débogage de la pipeline CI/CD pour garantir une livraison continue cohérente et sécurisée." },
    ],
  },
  {
    version: "v0.4.0",
    date: "2026-06-03",
    type: "Production Ready & Persistence",
    description: "Version majeure apportant la persistance des menaces ransomware, l'internationalisation complète et un durcissement de la sécurité (CI/CD, SCA).",
    changes: [
      { type: "feat", text: "Persistance locale des détections Ransomware positives en base de données pour un historique fiable." },
      { type: "feat", text: "Internationalisation intégrale (i18n FR/EN) sur l'ensemble du parcours utilisateur." },
      { type: "feat", text: "Pipeline de sécurité CI/CD : intégration de Bandit (SCA), Mypy (Typing) et audit de secrets." },
      { type: "fix", text: "Fiabilisation des permissions administrateur pour le déclenchement des scans (RBAC Hardening)." },
      { type: "fix", text: "Sécurisation du compte admin initial : reset automatique du MFA et des sessions au démarrage." },
      { type: "fix", text: "Correction des conflits de démarrage multi-workers via verrouillage distribué Redis robuste." },
    ],
  },
  {
    version: "v0.3.0",
    date: "2026-05-23",
    type: "Major Fixes & UX Overhaul",
    description: "Correction massive des bugs de navigation, stabilisation de l'admin et améliorations visuelles du dashboard.",
    changes: [
      { type: "fix", text: "Résolution de la boucle de déconnexion infinie sur la page changelog via middleware intelligent." },
      { type: "feat", text: "Nouveau centre de notifications interactif basé sur le flux de veille numérique." },
      { type: "feat", text: "Traduction intégrale de la Sidebar (i18n) et fiabilisation du changement de langue." },
      { type: "fix", text: "Correction d'un bug critique bloquant la finalisation des scans et la génération de rapports." },
      { type: "fix", text: "Stabilisation des interfaces Admin : suppression des boucles infinies de re-chargement." },
      { type: "ui", text: "Alignement et harmonisation du Dashboard (Grille 50/50 pour connecteurs et volumes)." },
      { type: "ui", text: "Indicateurs visuels de statut dynamiques (Vert/Rouge/Orange) sur les en-têtes d'outils." },
      { type: "ui", text: "Refonte de la mise en page des paramètres (Tabs) pour une meilleure lisibilité." },
    ],
  },
  {
    version: "v0.2.3",
    date: "2026-05-23",
    type: "Cyber Watch & Intelligence",
    description: "Déploiement complet du moteur de veille numérique et de renseignements cyber.",
    changes: [
      { type: "feat", text: "Nouveau moteur 'Intelligence Monitor' automatisant la collecte RSS, GitHub et Paste sites." },
      { type: "feat", text: "Vue 'Feed' temps réel avec triage par sévérité et statut de traitement (Lu/Non-lu)." },
      { type: "feat", text: "Alerting critique : notifications instantanées lors de la détection de menaces majeures (0-day, fuites)." },
      { type: "feat", text: "Intégration de sources majeures dont IT-Connect, CERT-FR, CISA et The Hacker News." },
      { type: "fix", text: "Optimisation du collecteur : gestion des redirections HTTP et émulation de navigateur." },
    ],
  },
  {
    version: "v0.2.2",
    date: "2026-05-23",
    type: "Security & Experience",
    description: "Renforcement de l'authentification multi-facteurs (MFA) et optimisation de l'expérience utilisateur.",
    changes: [
      { type: "feat", text: "Implémentation d'un flux de secours MFA complet avec codes de récupération (Recovery Codes)." },
      { type: "feat", text: "Ajout d'un popup intelligent de réactivation MFA post-secours avec option de persistance 'Plus tard'." },
      { type: "fix", text: "Correction des déconnexions prématurées lors des changements de paramètres de sécurité." },
      { type: "fix", text: "Stabilisation du menu profil (Header) et résolution des problèmes de superposition (z-index)." },
      { type: "feat", text: "Amélioration UX : focus automatique sur les champs de saisie et validation par touche 'Entrée'." },
      { type: "fix", text: "Mise à jour du schéma backend pour une synchronisation parfaite des statuts MFA requis." },
    ],
  },
  {
    version: "v0.2.1",
    date: "2026-05-19",
    type: "Maintenance & Connectivity",
    description: "Fiabilisation du connecteur RansomLook et synchronisation des métadonnées de statut.",
    changes: [
      { type: "feat", text: "Amélioration de la résilience du connecteur RansomLook (Healthcheck local)." },
      { type: "fix", text: "Synchronisation des noms de champs entre l'API et la WebUI (Statut RansomLook)." },
      { type: "feat", text: "Ajout de l'affichage du mode de connexion (Local/SaaS) dans le dashboard ransomware." },
    ],
  },
  {
    version: "v0.2.0",
    date: "2026-05-17",
    type: "Feature Update",
    description: "Améliorations majeures de l'interface utilisateur et des fonctionnalités de recherche RansomLook.",
    changes: [
      { type: "feat", text: "Recherche dynamique par domaine dans l'outil RansomLook." },
      { type: "feat", text: "Menu latéral extensible (Hover Expand) avec affichage fluide des labels." },
      { type: "fix", text: "Correction des permissions administratives (Rôle manquant dans le JWT)." },
      { type: "fix", text: "Suppression du scroll horizontal parasite dans la sidebar." },
      { type: "fix", text: "Correction du déclenchement manuel des scans (Rescan)." },
      { type: "feat", text: "Mise à jour dynamique du logo (Logo complet au survol du menu)." },
      { type: "feat", text: "Amélioration du connecteur RansomLook." },
      { type: "feat", text: "Mise à jour des connecteurs non disponibles." },
      { type: "feat", text: "Design responsive avec Menu Burger pour mobiles." },
      { type: "fix", text: "Redimensionnement et stabilisation du logo sidebar." },
    ],
  },
  {
    version: "v0.1.1",
    date: "2026-05-15",
    type: "Maintenance",
    description: "Version de transition et correctifs mineurs sur le moteur de détection.",
    changes: [
      { type: "feat", text: "Dashboard interactif avec volume de détection par sévérité." },
      { type: "feat", text: "Monitoring complet des Ransomwares (RansomLook integration)." },
      { type: "feat", text: "Veille CVE & Exploits agrégée (NVD, OSV, GitHub)." },
      { type: "fix", text: "Optimisation des performances des scans asynchrones." },
    ],
  },
  {
    version: "v0.1",
    date: "2026-05-01",
    type: "Backend Update",
    description: "Initialisation des connecteurs OSINT et amélioration de l'infrastructure.",
    changes: [
      { type: "feat", text: "Gestion initiale des utilisateurs et RBAC." },
      { type: "feat", text: "Système de rapports multi-formats (PDF, JSON, HTML)." },
      { type: "feat", text: "Ajout du connecteur IntelX et LeakCheck." },
    ],
  },
  {
    version: "v0.1",
    date: "2026-05-01",
    type: "Initial",
    description: "Initialisation des connecteurs principaux et de l'infrastructure de base.",
    changes: [
      { type: "feat", text: "Version initiale du design." },
      { type: "feat", text: "Intégration du connecteur RansomLook." },
      { type: "feat", text: "Premier ajout des connecteurs GitHub, GitLab et Bitbucket, HIBP." },
    ],
  },
];

export default function ChangelogPage() {
  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <PageHeader title="Changelog" icon={ScrollText} />

      <div className="max-w-4xl space-y-8">
        {RELEASES.map((release, idx) => (
          <div key={release.version} className="relative pl-8">
            {/* Ligne de timeline */}
            {idx < RELEASES.length - 1 && (
              <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border/50" />
            )}
            
            {/* Point de timeline */}
            <div className="absolute left-0 top-1.5 w-[23px] h-[23px] rounded-full bg-background border-2 border-radar flex items-center justify-center z-10">
              <div className="w-1.5 h-1.5 rounded-full bg-radar" />
            </div>

            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <h2 className="text-xl font-bold text-foreground">{release.version}</h2>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-radar/10 text-radar text-[10px] font-semibold uppercase border border-radar/20">
                    {release.type}
                  </span>
                  <span className="text-xs text-muted-foreground font-data">{release.date}</span>
                </div>
              </div>

              <Card className="p-6 bg-card/30 space-y-4">
                <p className="text-sm text-foreground/80 leading-relaxed">
                  {release.description}
                </p>

                <div className="space-y-3">
                  {release.changes.map((change, cIdx) => (
                    <div key={cIdx} className="flex gap-3 text-sm">
                      <div className="mt-0.5">
                        {change.type === "feat" ? (
                          <CheckCircle2 className="w-4 h-4 text-green-400" />
                        ) : change.type === "fix" ? (
                          <AlertCircle className="w-4 h-4 text-orange-400" />
                        ) : (
                          <Info className="w-4 h-4 text-blue-400" />
                        )}
                      </div>
                      <span className="text-muted-foreground">
                        <span className={`font-semibold mr-1 ${
                          change.type === "feat" ? "text-green-400/80" : 
                          change.type === "fix" ? "text-orange-400/80" : "text-blue-400/80"
                        }`}>
                          [{change.type.toUpperCase()}]
                        </span>
                        {change.text}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
