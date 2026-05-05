"use client";

/**
 * DomainBanner — BreachRadar WebUI
 * Affiche le domaine cible configuré (TARGET_DOMAIN via NEXT_PUBLIC_TARGET_DOMAIN).
 * Bannière compacte affichée en haut du dashboard pour rappel immédiat du périmètre.
 *
 * ⚠️  "use client" est OBLIGATOIRE : les variables NEXT_PUBLIC_* sont injectées
 *     dans le bundle client au build. Un Server Component ne les lit pas de la même
 *     façon et renvoie undefined au runtime si la valeur n'est pas statiquement
 *     connue au moment du build Next.js.
 */

import { Globe } from "lucide-react";

export function DomainBanner() {
  const domain = process.env.NEXT_PUBLIC_TARGET_DOMAIN;
  const isConfigured = Boolean(domain);

  return (
    <div
      className={`flex items-center gap-2 px-6 py-2 text-xs font-data border-b
        ${
          isConfigured
            ? "bg-radar/5 border-radar/20 text-radar"
            : "bg-yellow-500/5 border-yellow-500/20 text-yellow-400"
        }`}
      role="status"
      aria-label="Domaine cible surveillé"
    >
      <Globe className="w-3.5 h-3.5 flex-shrink-0" strokeWidth={1.5} />
      <span className="text-muted-foreground">Domaine surveillé&nbsp;:</span>
      <span className="font-semibold tracking-wide">
        {isConfigured ? domain : "(domaine non configuré)"}
      </span>
      {!isConfigured && (
        <span className="ml-2 text-yellow-400/70">
          — définir{" "}
          <code className="bg-yellow-500/10 px-1 rounded">
            NEXT_PUBLIC_TARGET_DOMAIN
          </code>{" "}
          dans le .env
        </span>
      )}
    </div>
  );
}
