"use client";

import { Key, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { ToolPageLayout } from "@/components/layout/ToolPageLayout";
import { type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import { scansApi, type PaginatedResponse, type Finding } from "@/lib/api";
import { useState } from "react";

export function HIBPClient({
  initialData,
  chartData,
  initialPage,
  period,
}: {
  initialData: PaginatedResponse<Finding> | null;
  chartData: any[];
  initialPage: number;
  period: string;
}) {
  const router = useRouter();
  const [isScanning, setIsScanning] = useState(false);

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString("en-GB", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).replace(",", "");
  };

  const columns: DataTableColumn<Finding>[] = [
    {
      key: "discovered_at",
      header: "Date",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.discovered_at),
      sortable: false,
      accessor: (row) => row.discovered_at,
    },
    {
      key: "domain",
      header: "Compromised Email",
      className: "font-data font-medium text-foreground",
      sortable: false,
      accessor: (row) => row.domain, // Email is likely stored here or in metadata
    },
    {
      key: "title",
      header: "Breach Name",
      className: "text-xs truncate max-w-[200px]",
      sortable: false,
      accessor: (row) => row.title,
    },
    {
      key: "severity",
      header: "Severity",
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      sortable: false,
      accessor: (row) => row.severity,
    },
  ];

  const handlePageChange = (page: number) => {
    router.push(`/tools/hibp?period=${period}&page=${page}`);
  };

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

  return (
    <ToolPageLayout<Finding>
      title="HIBP & Breaches"
      description="Monitor compromised emails and data breaches via HaveIBeenPwned."
      icon={Key}
      breadcrumb={[
        { label: "Dashboard", href: "/" },
        { label: "Tools", href: "#" },
        { label: "HIBP", active: true },
      ]}
      period={period}
      chartData={chartData}
      tableData={initialData?.items || []}
      tableColumns={columns}
      tableEmptyMessage="No compromised emails detected in this period."
      pagination={initialData ? {
        page: initialPage,
        pageSize: 25,
        totalItems: initialData.total,
        totalPages: initialData.pages,
        onPageChange: handlePageChange,
      } : undefined}
      actions={
        <button
          onClick={handleTriggerScan}
          disabled={isScanning}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md
                     bg-radar/10 hover:bg-radar/20 border border-radar/30
                     text-radar text-xs font-semibold transition-colors duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className={`w-3.5 h-3.5 ${isScanning ? "animate-spin" : ""}`} />
          {isScanning ? "Scanning..." : "Rescan"}
        </button>
      }
    />
  );
}
