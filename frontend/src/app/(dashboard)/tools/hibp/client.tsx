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
  isMock,
}: {
  initialData: PaginatedResponse<Finding> | null;
  chartData: any[];
  initialPage: number;
  period: string;
  isMock?: boolean;
}) {
  const router = useRouter();
// ... (rest of component unchanged)
  return (
    <ToolPageLayout
      icon={Key}
      title="Have I Been Pwned"
      description="Monitor compromised emails and data breaches via HaveIBeenPwned."
      breadcrumb={[
        { label: "Dashboard", href: "/" },
        { label: "Tools", href: "#" },
        { label: "HIBP" },
      ]}
      period={period}
      chartData={chartData}
      tableData={initialData?.items || []}
      tableColumns={columns}
      tableEmptyMessage="No compromised emails detected in this period."
      isMock={isMock}
      pagination={initialData ? {
// ... (rest of props unchanged)
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
