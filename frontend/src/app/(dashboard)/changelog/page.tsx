import { ScrollText, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";

/**
 * Page Changelog
 * Affiche l'historique des versions de BreachRadar.
 */

const RELEASES = [
  {
    version: "v1.0.0",
    date: "2026-05-15",
    type: "Stable",
    description: "Version initiale stable de la WebUI BreachRadar — Gouvernance SOC.",
    changes: [
      { type: "feat", text: "Dashboard interactif avec volume de détection par sévérité." },
      { type: "feat", text: "Monitoring complet des Ransomwares (RansomLook integration)." },
      { type: "feat", text: "Gestion des utilisateurs avec RBAC (Admin/Viewer) et MFA TOTP." },
      { type: "feat", text: "Système de rapports multi-formats (PDF, JSON, HTML)." },
      { type: "feat", text: "Veille CVE & Exploits agrégée (NVD, OSV, GitHub)." },
      { type: "fix", text: "Optimisation des performances des scans asynchrones." },
      { type: "fix", text: "Correction des fuites de données dans les logs de production." },
    ],
  },
  {
    version: "v0.9.0-rc1",
    date: "2026-05-01",
    type: "Release Candidate",
    description: "Finalisation des connecteurs OSINT et de l'infrastructure Docker.",
    changes: [
      { type: "feat", text: "Ajout du connecteur IntelX et LeakCheck." },
      { type: "feat", text: "Nouveau système de scheduling basé sur APScheduler." },
      { type: "fix", text: "Amélioration de la sanitization des données sensibles." },
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
