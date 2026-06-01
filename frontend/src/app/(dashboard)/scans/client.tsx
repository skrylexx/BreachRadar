"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Radar, Play } from "lucide-react";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import { StatusDot } from "@/components/ui/status-dot";
import { scansApi, type Scan, type PaginatedResponse } from "@/lib/api";
import { useTranslations, useLocale } from "next-intl";

export function ScansClient({ 
  initialData, 
  initialPage 
}: { 
  initialData: PaginatedResponse<Scan> | null;
  initialPage: number;
}) {
  const router = useRouter();
  const t = useTranslations("Scans");
  const tc = useTranslations("Common");
  const locale = useLocale();
  const [isScanning, setIsScanning] = useState(false);

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
      key: "id",
      header: t("col_id"),
      className: "font-data text-xs font-medium truncate max-w-[150px]",
      sortable: false,
      accessor: (row) => row.id,
    },
    {
      key: "status",
      header: t("col_status"),
      render: (row) => (
        <div className="flex items-center gap-2">
          <StatusDot status={row.status === "completed" ? "ok" : row.status === "failed" ? "error" : "warning"} />
          <span className="capitalize text-xs font-medium">{row.status}</span>
        </div>
      ),
      sortable: false,
      accessor: (row) => row.status,
    },
    {
      key: "started_at",
      header: t("col_started"),
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.started_at),
      sortable: false,
      accessor: (row) => row.started_at,
    },
    {
      key: "duration_seconds",
      header: t("col_duration"),
      className: "font-data text-muted-foreground",
      render: (row) => row.duration_seconds ? `${row.duration_seconds}${tc("unit_s")}` : "-",
      sortable: false,
      accessor: (row) => row.duration_seconds,
    },
    {
      key: "findings_count",
      header: t("col_findings"),
      className: "font-data font-bold",
      sortable: false,
      accessor: (row) => row.findings_count,
    },
    {
      key: "severity",
      header: t("col_severity"),
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      sortable: false,
      accessor: (row) => row.severity,
    },
    {
      key: "triggered_by",
      header: t("col_trigger"),
      className: "capitalize text-muted-foreground text-xs",
      sortable: false,
      accessor: (row) => row.triggered_by,
    },
  ];

  const handleTriggerScan = async () => {
    try {
      setIsScanning(true);
      await scansApi.trigger();
      setTimeout(() => {
        router.refresh();
        setIsScanning(false);
      }, 2000);
    } catch (error) {
      console.error("Failed to trigger scan", error);
      setIsScanning(false);
    }
  };

  const handlePageChange = (page: number) => {
    router.push(`/scans?page=${page}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          onClick={handleTriggerScan}
          disabled={isScanning}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md
                     bg-radar/10 hover:bg-radar/20 border border-radar/30
                     text-radar text-sm font-semibold transition-colors duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isScanning ? (
            <Radar className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {isScanning ? t("btn_starting") : t("btn_trigger")}
        </button>
      </div>

      <div className="card-soc p-0">
        <DataTable<Scan>
          columns={columns}
          data={initialData?.items || []}
          rowKey={(row) => row.id}
          emptyMessage={t("empty")}
          className="border-0 rounded-none"
          pagination={initialData ? {
            page: initialPage,
            pageSize: 25,
            totalItems: initialData.total,
            totalPages: Math.ceil(initialData.total / initialData.page_size),
            onPageChange: handlePageChange,
          } : undefined}
        />
      </div>
    </div>
  );
}
