"use client";

import { Bug, ChevronRight } from "lucide-react";
import Link from "next/link";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge, type SeverityLevel } from "@/components/ui/severity-badge";
import type { CVEAlert } from "@/lib/api";

export function CVEAlertsBlock({ alerts = [] }: { alerts?: CVEAlert[] }) {
  if (!alerts || alerts.length === 0) return null;

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const columns: DataTableColumn<CVEAlert>[] = [
    {
      key: "cve_id",
      header: "CVE ID",
      className: "font-data font-bold text-foreground",
      sortable: false,
      accessor: (row) => row.cve_id,
    },
    {
      key: "severity",
      header: "Severity",
      render: (row) => <SeverityBadge level={row.severity as SeverityLevel} />,
      sortable: false,
      accessor: (row) => row.severity,
    },
    {
      key: "cvss_score",
      header: "CVSS",
      className: "font-data text-xs text-muted-foreground",
      render: (row) => row.cvss_score ? row.cvss_score.toFixed(1) : "-",
      sortable: false,
      accessor: (row) => row.cvss_score,
    },
    {
      key: "title",
      header: "Vulnerability",
      className: "text-xs text-foreground truncate max-w-[250px]",
      sortable: false,
      accessor: (row) => row.title,
    },
    {
      key: "published_at",
      header: "Published",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.published_at),
      sortable: false,
      accessor: (row) => row.published_at,
    },
  ];

  return (
    <div className="card-soc">
      {/* En-tête */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-orange-400" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold text-foreground">Latest CVEs & Exploits</h3>
        </div>
        <Link 
          href="/alerts/cve" 
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
        >
          View all <ChevronRight className="w-3 h-3" />
        </Link>
      </div>

      <DataTable<CVEAlert>
        columns={columns}
        data={alerts}
        rowKey={(row) => row.id}
        emptyMessage="No recent CVE alerts found."
        className="border-0 rounded-none"
      />
    </div>
  );
}
