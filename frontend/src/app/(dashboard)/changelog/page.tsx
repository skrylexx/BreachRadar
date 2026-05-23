import { ScrollText, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";

/**
 * Page Changelog
 * Affiche l'historique des versions de BreachRadar.
 */

const RELEASES = [
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
