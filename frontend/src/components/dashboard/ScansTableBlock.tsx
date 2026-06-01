"use client";

import { Activity, ChevronRight } from "lucide-react";
import Link from "next/link";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import { StatusDot, type SourceStatus } from "@/components/ui/status-dot";
import type { Scan } from "@/lib/api";
import { useTranslations, useLocale } from "next-intl";

export function ScansTableBlock({ scans = [] }: { scans?: Scan[] }) {
  const t = useTranslations();
  const locale = useLocale();

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString(locale === 'en' ? 'en-GB' : 'fr-FR', {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).replace(",", "");
  };

  const columns: DataTableColumn<Scan>[] = [
    {
      key: "started_at",
      header: t("Common.date"),
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.started_at),
      sortable: false,
      accessor: (row) => row.started_at,
    },
    {
      key: "status",
      header: t("Common.status"),
      render: (row) => (
        <div className="flex items-center gap-2">
          <StatusDot status={row.status === "completed" ? "ok" : row.status === "failed" ? "error" : "warning"} />
          <span className="capitalize text-xs text-muted-foreground">{row.status}</span>
        </div>
      ),
      sortable: false,
      accessor: (row) => row.status,
    },
    {
      key: "duration_seconds",
      header: t("Common.duration"),
      className: "font-data text-xs text-muted-foreground",
      render: (row) => row.duration_seconds ? `${row.duration_seconds}${t("Common.unit_s")}` : "-",
      sortable: false,
      accessor: (row) => row.duration_seconds,
    },
    {
      key: "findings_count",
      header: t("Common.count"),
      className: "font-data font-semibold text-foreground",
      sortable: false,
      accessor: (row) => row.findings_count,
    },
    {
      key: "severity",
      header: t("Common.severity"),
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      sortable: false,
      accessor: (row) => row.severity,
    },
    {
      key: "actions",
      header: "",
      render: (row) => (
        <div className="flex justify-end">
          <Link
            href={`/scans/${row.id}`}
            className="p-1 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
            title={t("Common.view_details")}
          >
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      ),
      sortable: false,
      accessor: () => null,
    },
  ];

  return (
    <div className="card-soc">
      {/* En-tête */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-radar" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold text-foreground">{t("ScansTable.title")}</h3>
        </div>
        <Link 
          href="/scans" 
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
        >
          {t("ScansTable.view_all")} <ChevronRight className="w-3 h-3" />
        </Link>
      </div>

      <DataTable<Scan>
        columns={columns}
        data={scans}
        rowKey={(row) => row.id}
        emptyMessage={t("ScansTable.empty")}
        className="border-0 rounded-none"
      />
    </div>
  );
}
