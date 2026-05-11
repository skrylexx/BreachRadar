"use client";

import { Lock, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { ToolPageLayout } from "@/components/layout/ToolPageLayout";
import { type DataTableColumn } from "@/components/ui/data-table";
import { scansApi, type PaginatedResponse, type RansomwareAlert } from "@/lib/api";
import { useState } from "react";

export function RansomLookClient({
  initialData,
  chartData,
  initialPage,
  period,
}: {
  initialData: PaginatedResponse<RansomwareAlert> | null;
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

  const columns: DataTableColumn<RansomwareAlert>[] = [
    {
      key: "discovered_at",
      header: "Date",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.discovered_at),
      sortable: false,
      accessor: (row) => row.discovered_at,
    },
    {
      key: "group",
      header: "Group",
      className: "font-data font-bold text-red-400 uppercase tracking-wide",
      sortable: false,
      accessor: (row) => row.group,
    },
    {
      key: "victim",
      header: "Victim",
      className: "font-medium text-foreground truncate max-w-[200px]",
      sortable: false,
      accessor: (row) => row.victim,
    },
    {
      key: "status",
      header: "Status",
      className: "text-xs font-semibold",
      render: (row) => (
        <span className={row.status === "PUBLISHED" ? "text-red-400" : "text-yellow-400"}>
          {row.status}
        </span>
      ),
      sortable: false,
      accessor: (row) => row.status,
    },
  ];

  const handlePageChange = (page: number) => {
    router.push(`/tools/ransomlook?period=${period}&page=${page}`);
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
    <ToolPageLayout<RansomwareAlert>
      title="RansomLook"
      description="Monitor ransomware group activities and victims."
      icon={Lock}
      breadcrumb={[
        { label: "Dashboard", href: "/" },
        { label: "Tools", href: "#" },
        { label: "RansomLook", active: true },
      ]}
      period={period}
      chartData={chartData}
      tableData={initialData?.items || []}
      tableColumns={columns}
      tableEmptyMessage="No ransomware alerts detected in this period."
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
