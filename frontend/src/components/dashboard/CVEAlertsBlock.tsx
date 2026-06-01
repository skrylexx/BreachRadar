"use client";

import { Bug, ChevronRight } from "lucide-react";
import Link from "next/link";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import type { CVEAlert } from "@/lib/api";
import { useTranslations, useLocale } from "next-intl";

export function CVEAlertsBlock({ alerts = [] }: { alerts?: CVEAlert[] }) {
  const t = useTranslations();
  const locale = useLocale();
  if (!alerts || alerts.length === 0) return null;

  const isMock = alerts.length > 0 && alerts[0].id.startsWith("mock-");

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleDateString(locale === 'en' ? 'en-GB' : 'fr-FR', {
      day: "2-digit",
      month: "2-digit",
    });
  };

  const columns: DataTableColumn<CVEAlert>[] = [
    {
      key: "published_at",
      header: t("Common.date"),
      className: "font-data text-muted-foreground whitespace-nowrap",
      render: (row) => formatDate(row.published_at),
    },
    {
      key: "cve_id",
      header: "ID",
      className: "font-data font-bold text-foreground",
    },
    {
      key: "title",
      header: t("Common.type"), // Reusing Type for Title in this context or I could use Common.title if I added it
      className: "truncate max-w-[300px]",
    },
    {
      key: "severity",
      header: t("Common.severity"),
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      className: "text-right",
    },
  ];

  return (
    <div className="card-soc">
      {/* En-tête */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-orange-400" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold text-foreground">{t("CVEAlerts.title")}</h3>
          {isMock && (
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20">
              {t("CVEAlerts.mock")}
            </span>
          )}
        </div>
        <Link 
          href="/alerts/cve"
          className="text-[11px] font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
        >
          {t("CVEAlerts.view_all")}
          <ChevronRight className="w-3 h-3" />
        </Link>
      </div>

      <DataTable<CVEAlert>
        columns={columns}
        data={alerts}
        rowKey={(row) => row.id}
        emptyMessage={t("CVEAlerts.empty")}
        className="border-0 rounded-none"
      />
    </div>
  );
}
