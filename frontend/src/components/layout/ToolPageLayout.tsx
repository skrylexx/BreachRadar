import { LucideIcon } from "lucide-react";
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
  pagination,
}: ToolPageLayoutProps<T>) {
  return (
    <div className="space-y-6">
      <PageHeader
        title={title}
        description={description}
        breadcrumb={breadcrumb}
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
