import { LucideIcon, AlertTriangle } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { RiskHeatmap } from "@/components/dashboard/RiskHeatmap";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { ReactNode } from "react";

interface ToolPageLayoutProps<T> {
  title: string;
  description: string;
  icon: LucideIcon;
  breadcrumb: { label: string; href?: string; active?: boolean }[];
  period: string;
  chartData: any[]; // RiskHeatmap data format
  tableData: T[];
  tableColumns: DataTableColumn<T>[];
  tableEmptyMessage?: string;
  actions?: ReactNode;
  children?: ReactNode;
  isMock?: boolean;
  isConfigured?: boolean;
  pagination?: {
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
}

export function ToolPageLayout<T>({
  title,
  description,
  icon,
  breadcrumb,
  period,
  chartData,
  tableData,
  tableColumns,
  tableEmptyMessage,
  actions,
  children,
  isMock,
  isConfigured = true,
  pagination,
}: ToolPageLayoutProps<T>) {
  const status = isMock ? "mock" : !isConfigured ? "down" : "up";

  return (
    <div className="space-y-6">
      {isMock && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 flex items-center gap-3 text-orange-400 animate-pulse">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div className="text-sm">
            <span className="font-bold uppercase mr-2">Mode Démonstration :</span>
            Ce connecteur n'est pas configuré. Les données affichées ci-dessous sont des exemples (Mocks).
          </div>
        </div>
      )}

      <PageHeader
        title={title}
        description={description}
        icon={icon}
        breadcrumb={breadcrumb}
        status={status}
      >
        {actions}
      </PageHeader>

      <div className="grid grid-cols-1 gap-6">
        {/* Chart section */}
        <div>
          <RiskHeatmap data={chartData} initialPeriod={period as any} />
        </div>

        {/* Optional custom children */}
        {children}

        {/* Data Table section */}
        <div className="card-soc p-0 overflow-hidden">
          <DataTable<T>
            columns={tableColumns}
            data={tableData}
            rowKey={(row: any) => row.id || JSON.stringify(row)}
            emptyMessage={tableEmptyMessage || "No data available."}
            className="border-0 rounded-none"
            pagination={pagination}
          />
        </div>
      </div>
    </div>
  );
}
