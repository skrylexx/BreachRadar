"use client";

import { Globe } from "lucide-react";
import { useTranslations } from "next-intl";

interface DomainBannerProps {
  /** Monitored domain, passed from server side. */
  domain?: string;
}

export function DomainBanner({ domain }: DomainBannerProps) {
  const t = useTranslations("DomainBanner");
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
      <span className="text-muted-foreground">{t("monitored_domain")}</span>
      <span className="font-semibold tracking-wide">
        {isConfigured ? domain : t("not_configured")}
      </span>
      {!isConfigured && (
        <span className="ml-2 text-yellow-400/70">
          {t.rich("define_env", {
            env1: (chunks) => <code className="bg-yellow-500/10 px-1 rounded">TARGET_DOMAIN</code>,
            env2: (chunks) => <code className="bg-yellow-500/10 px-1 rounded">NEXT_PUBLIC_TARGET_DOMAIN</code>,
          })}
        </span>
      )}
    </div>
  );
}
