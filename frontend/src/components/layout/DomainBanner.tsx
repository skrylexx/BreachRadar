"use client";

import { Globe } from "lucide-react";

interface DomainBannerProps {
  /** Domaine surveillé, lu côté serveur et passé en prop. */
  domain?: string;
}

export function DomainBanner({ domain }: DomainBannerProps) {
  const isConfigured = Boolean(domain && domain.trim().length > 0);

  return (
    <div
      className={`flex items-center gap-2 px-6 py-2 text-xs font-data border-b ${
        isConfigured
          ? "bg-radar/5 border-radar/20 text-radar"
          : "bg-yellow-500/5 border-yellow-500/20 text-yellow-400"
      }`}
      role="status"
      aria-live="polite"
    >
      <Globe className="w-3.5 h-3.5 flex-shrink-0" strokeWidth={1.5} />
      <span className="text-muted-foreground">Domaine surveillé&nbsp;:</span>
      <span className="font-semibold tracking-wide">
        {isConfigured ? domain : "(domaine non configuré)"}
      </span>
      {!isConfigured && (
        <span className="ml-2 text-yellow-400/70">
          — définir{" "}
          <code className="bg-yellow-500/10 px-1 rounded">TARGET_DOMAIN</code>
          {" "}ou{" "}
          <code className="bg-yellow-500/10 px-1 rounded">NEXT_PUBLIC_TARGET_DOMAIN</code>
          {" "}dans le .env
        </span>
      )}
    </div>
  );
}
