"use client";

import { Lock, Play, Search } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { ToolPageLayout } from "@/components/layout/ToolPageLayout";
import { type DataTableColumn } from "@/components/ui/data-table";
import { scansApi, type PaginatedResponse, type RansomwareAlert } from "@/lib/api";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function RansomLookClient({
  initialData,
  chartData,
  initialPage,
  period,
  search: initialSearch,
  isMock,
  isConfigured,
}: {
  initialData: PaginatedResponse<RansomwareAlert> | null;
  chartData: any[];
  initialPage: number;
  period: string;
  search: string;
  isMock?: boolean;
  isConfigured?: boolean;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isScanning, setIsScanning] = useState(false);
  const [searchTerm, setSearchTerm] = useState(initialSearch);

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
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", page.toString());
    router.push(`/tools/ransomlook?${params.toString()}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (searchTerm) {
      params.set("search", searchTerm);
    } else {
      params.delete("search");
    }
    params.set("page", "1");
    router.push(`/tools/ransomlook?${params.toString()}`);
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
      icon={Lock}
      title="RansomLook"
      description="Monitor ransomware group activities and victims."
      breadcrumb={[
        { label: "Dashboard", href: "/" },
        { label: "Tools", href: "#" },
        { label: "RansomLook" },
      ]}
      period={period}
      chartData={chartData}
      tableData={initialData?.items || []}
      tableColumns={columns}
      tableEmptyMessage="No ransomware alerts detected in this period."
      isMock={isMock}
      pagination={initialData ? {
        page: initialPage,
        pageSize: 25,
        totalItems: initialData.total,
        totalPages: Math.ceil(initialData.total / initialData.page_size),
        onPageChange: handlePageChange,
      } : undefined}
      actions={
        <div className="flex items-center gap-3">
          {isConfigured && (
            <form onSubmit={handleSearch} className="relative hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search domain..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-1.5 bg-card border border-border/50 rounded-md text-xs focus:outline-none focus:ring-1 focus:ring-radar/50 w-48 transition-all"
              />
            </form>
          )}
          <button
            onClick={handleTriggerScan}
            disabled={isScanning || !isConfigured}
            className={cn(
              "inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-semibold transition-colors duration-200 disabled:cursor-not-allowed",
              isConfigured 
                ? "bg-radar/10 hover:bg-radar/20 border border-radar/30 text-radar"
                : "bg-muted text-muted-foreground border border-border opacity-70"
            )}
          >
            {isConfigured ? (
              <>
                <Play className={`w-3.5 h-3.5 ${isScanning ? "animate-spin" : ""}`} />
                {isScanning ? "Scanning..." : "Rescan"}
              </>
            ) : (
              "Activez le connecteur d'abord"
            )}
          </button>
        </div>
      }
    />
  );
}
