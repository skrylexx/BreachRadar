"use client";

import { Github, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { ToolPageLayout } from "@/components/layout/ToolPageLayout";
import { type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import { scansApi, type PaginatedResponse, type Finding } from "@/lib/api";
import { useState } from "react";

export function GitHubClient({
  initialData,
  chartData,
  initialPage,
  period,
  isMock,
}: {
  initialData: PaginatedResponse<Finding> | null;
  chartData: any[];
  initialPage: number;
  period: string;
  isMock?: boolean;
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
      header: "Repository",
      className: "font-data font-medium text-foreground truncate max-w-[200px]",
      sortable: false,
      accessor: (row) => (row as any).domain || (row as any).url || "N/A",
    },
    {
      key: "type",
      header: "Type",
      className: "text-xs uppercase text-muted-foreground tracking-wider",
      sortable: false,
      accessor: (row) => row.type, // secret, credential, token
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
    router.push(`/tools/github?period=${period}&page=${page}`);
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
    <ToolPageLayout
      icon={Github}
      title="GitHub & GitLab"
      description="Monitor exposed secrets and credentials in public repositories."
      breadcrumb={[
        { label: "Dashboard", href: "/" },
        { label: "Tools", href: "#" },
        { label: "GitHub" },
      ]}
      period={period}
      chartData={chartData}
      tableData={initialData?.items || []}
      tableColumns={columns}
      tableEmptyMessage="No exposed secrets detected in this period."
      isMock={isMock}
      pagination={initialData ? {
        page: initialPage,
        pageSize: 25,
        totalItems: initialData.total,
        totalPages: Math.ceil(initialData.total / initialData.page_size),
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