"use client";

import { FileText, Download, Loader2, FileDown, FileJson } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { TimeFilter, type TimePeriod } from "@/components/ui/time-filter";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import { reportsApi, type PaginatedResponse, type Report } from "@/lib/api";
import { useTranslations, useLocale } from "next-intl";

export function ReportsClient({
  initialData,
  initialPage,
  period,
}: {
  initialData: PaginatedResponse<Report> | null;
  initialPage: number;
  period: string;
}) {
  const router = useRouter();
  const t = useTranslations("Reports");
  const tc = useTranslations("Common");
  const locale = useLocale();
  const [isGenerating, setIsGenerating] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // Pour le modal de génération
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [generateError, setGenerateError] = useState("");

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString(locale === 'en' ? 'en-GB' : 'fr-FR', {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).replace(",", "");
  };

  const handlePageChange = (page: number) => {
    router.push(`/reports?period=${period}&page=${page}`);
  };

  const handlePeriodChange = (newPeriod: TimePeriod) => {
    router.push(`/reports?period=${newPeriod}&page=1`);
  };

  const handleExportPDF = (id: string) => {
    window.open(reportsApi.exportPdf(id), "_blank");
  };

  const handleExportJSON = (id: string) => {
    window.open(`${reportsApi.exportPdf(id).replace("format=pdf", "format=json")}`, "_blank");
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerateError("");
    
    if (!startDate || !endDate) {
      setGenerateError(t("error_dates"));
      return;
    }

    try {
      setIsGenerating(true);
      await reportsApi.generate(startDate, endDate);
      setShowGenerateModal(false);
      setTimeout(() => {
        router.refresh();
      }, 1500);
    } catch (err: any) {
      setGenerateError(err.message || t("error_failed"));
    } finally {
      setIsGenerating(false);
    }
  };

  const columns: DataTableColumn<Report>[] = [
    {
      key: "generated_at",
      header: t("col_date"),
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.generated_at),
      sortable: false,
      accessor: (row) => row.generated_at,
    },
    {
      key: "domain",
      header: t("col_domain"),
      className: "font-data font-medium text-foreground",
      sortable: false,
      accessor: (row) => row.domain,
    },
    {
      key: "type",
      header: t("col_type"),
      className: "capitalize text-xs text-muted-foreground tracking-wider",
      sortable: false,
      accessor: (row) => row.type,
    },
    {
      key: "severity",
      header: t("col_risk"),
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      sortable: false,
      accessor: (row) => row.severity,
    },
    {
      key: "emails_compromised",
      header: t("col_compromised"),
      className: "font-data text-center",
      sortable: false,
      accessor: (row) => row.emails_compromised,
    },
    {
      key: "has_ransomware_alert",
      header: t("col_ransomware"),
      className: "text-center",
      render: (row) => (
        <span className={row.has_ransomware_alert ? "text-red-400 font-bold" : "text-muted-foreground"}>
          {row.has_ransomware_alert ? t("yes") : t("no")}
        </span>
      ),
      sortable: false,
      accessor: (row) => (row.has_ransomware_alert ? "yes" : "no"),
    },
    {
      key: "actions",
      header: t("col_export"),
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={() => handleExportJSON(row.id)}
            className="p-1.5 rounded bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            title={t("tip_json")}
          >
            <FileJson className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleExportPDF(row.id)}
            className="p-1.5 rounded bg-radar/10 text-radar hover:bg-radar/20 transition-colors"
            title={t("tip_pdf")}
          >
            <FileDown className="w-4 h-4" />
          </button>
        </div>
      ),
      sortable: false,
      accessor: () => null,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("title")}
        description={t("description")}
        breadcrumb={[
          { label: tc("dashboard"), href: "/" },
          { label: t("title") },
        ]}
      >
        <div className="flex items-center gap-4">
          <TimeFilter value={period as TimePeriod} onChange={handlePeriodChange} />
          <button
            onClick={() => setShowGenerateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-md
                       bg-radar text-black text-sm font-bold transition-all hover:brightness-110"
          >
            <Download className="w-4 h-4" />
            {t("btn_generate")}
          </button>
        </div>
      </PageHeader>

      <div className="card-soc p-0">
        <DataTable<Report>
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

      {/* ─── Modal de Génération ─────────────────────────────────────────────── */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="card-soc p-6 w-full max-w-md animate-in fade-in zoom-in-95 duration-200">
            <h3 className="text-lg font-semibold text-foreground mb-1">{t("dialog_title")}</h3>
            <p className="text-xs text-muted-foreground mb-6">{t("dialog_desc")}</p>
            
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground">{t("label_start")}</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-secondary/50 border border-border/50 rounded-md px-3 py-2 text-sm text-foreground font-data focus:border-radar/50 focus:ring-1 focus:ring-radar/50 outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground">{t("label_end")}</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-secondary/50 border border-border/50 rounded-md px-3 py-2 text-sm text-foreground font-data focus:border-radar/50 focus:ring-1 focus:ring-radar/50 outline-none"
                  />
                </div>
              </div>

              {generateError && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md">
                  <p className="text-xs text-red-400">{generateError}</p>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-border/50">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  disabled={isGenerating}
                  className="px-4 py-2 text-sm font-medium text-foreground bg-secondary/50 hover:bg-secondary rounded-md transition-colors"
                >
                  {t("btn_cancel")}
                </button>
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-radar text-black text-sm font-bold rounded-md hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isGenerating && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t("btn_submit")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
