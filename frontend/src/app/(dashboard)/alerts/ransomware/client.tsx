"use client";

import { ShieldAlert, Server, Activity, Hash, Clock, FileText } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PageHeader } from "@/components/ui/page-header";
import { TimeFilter, type TimePeriod } from "@/components/ui/time-filter";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { SeverityBadge } from "@/components/ui/severity-badge";
import type { PaginatedResponse, RansomwareAlert } from "@/lib/api";

export function RansomwareAlertsClient({
  initialData,
  statusData,
  initialPage,
  period,
  currentFilters,
}: {
  initialData: PaginatedResponse<RansomwareAlert> | null;
  statusData: Record<string, any>;
  initialPage: number;
  period: string;
  currentFilters: { group?: string; status?: string };
}) {
  const router = useRouter();

  const formatDate = (iso?: string | null) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleString("en-GB", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).replace(",", "");
  };

  const handlePageChange = (page: number) => {
    const qs = new URLSearchParams(window.location.search);
    qs.set("page", page.toString());
    router.push(`/alerts/ransomware?${qs.toString()}`);
  };

  const handlePeriodChange = (newPeriod: TimePeriod) => {
    const qs = new URLSearchParams(window.location.search);
    qs.set("period", newPeriod);
    qs.set("page", "1");
    router.push(`/alerts/ransomware?${qs.toString()}`);
  };

  // Format Status Block Data
  const mode = statusData.mode || "SaaS";
  const groupsTracked = statusData.groups_tracked || 0;
  const totalPosts = statusData.total_posts || 0;
  const lastUpdated = statusData.last_update ? formatDate(statusData.last_update) : "Unknown";

  const columns: DataTableColumn<RansomwareAlert>[] = [
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
      key: "country",
      header: "Country",
      className: "text-xs text-muted-foreground",
      render: (row) => row.country || "—",
      sortable: false,
      accessor: (row) => row.country,
    },
    {
      key: "sector",
      header: "Sector",
      className: "text-xs text-muted-foreground",
      render: (row) => row.sector || "—",
      sortable: false,
      accessor: (row) => row.sector,
    },
    {
      key: "claim_size",
      header: "Claim Size",
      className: "font-data text-xs",
      render: (row) => row.claim_size || "—",
      sortable: false,
      accessor: (row) => row.claim_size,
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
    {
      key: "discovered_at",
      header: "Discovered",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.discovered_at),
      sortable: false,
      accessor: (row) => row.discovered_at,
    },
    {
      key: "published_at",
      header: "Published",
      className: "font-data whitespace-nowrap",
      render: (row) => formatDate(row.published_at),
      sortable: false,
      accessor: (row) => row.published_at,
    },
    {
      key: "actions",
      header: "Report",
      render: (row) => row.scan_id ? (
        <Link
          href={`/scans/${row.scan_id}`}
          className="inline-flex p-1.5 rounded bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          title="View related scan"
        >
          <FileText className="w-4 h-4" />
        </Link>
      ) : (
        <span className="text-muted-foreground">—</span>
      ),
      sortable: false,
      accessor: () => null,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Ransomware Alerts"
        description="Detailed view of ransomware victims, groups, and status."
        breadcrumb={[
          { label: "Dashboard", href: "/" },
          { label: "Alerts", href: "#" },
          { label: "Ransomware" },
        ]}
      >
        <TimeFilter value={period as TimePeriod} onChange={handlePeriodChange} />
      </PageHeader>

      {/* ─── RansomLook Instance State Block (Phase 4.1) ─────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-blue-500/10 flex items-center justify-center flex-shrink-0">
            <Server className="w-5 h-5 text-blue-400" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-lg font-bold text-foreground font-data">{mode}</p>
            <p className="text-xs text-muted-foreground">Mode</p>
          </div>
        </div>
        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
            <Activity className="w-5 h-5 text-emerald-400" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-lg font-bold text-foreground font-data">{groupsTracked}</p>
            <p className="text-xs text-muted-foreground">Groups Tracked</p>
          </div>
        </div>
        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-orange-500/10 flex items-center justify-center flex-shrink-0">
            <Hash className="w-5 h-5 text-orange-400" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-lg font-bold text-foreground font-data">{totalPosts}</p>
            <p className="text-xs text-muted-foreground">Total Posts</p>
          </div>
        </div>
        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-md bg-purple-500/10 flex items-center justify-center flex-shrink-0">
            <Clock className="w-5 h-5 text-purple-400" strokeWidth={1.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-foreground font-data">{lastUpdated}</p>
            <p className="text-xs text-muted-foreground">Last Updated</p>
          </div>
        </div>
      </div>

      {/* ─── Filters (Phase 4.3) ──────────────────────────────────────────────── */}
      <div className="card-soc p-4 flex items-center gap-4">
        <div className="flex-1 max-w-xs">
          <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">
            Filter by Group
          </label>
          <input 
            type="text" 
            placeholder="e.g. LockBit"
            className="w-full bg-secondary/50 border border-border/50 rounded-md px-3 py-1.5 text-xs text-foreground font-data focus:border-radar/50 focus:ring-1 focus:ring-radar/50 outline-none transition-colors"
            defaultValue={currentFilters.group || ""}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                const qs = new URLSearchParams(window.location.search);
                if (e.currentTarget.value) qs.set("group", e.currentTarget.value);
                else qs.delete("group");
                qs.set("page", "1");
                router.push(`/alerts/ransomware?${qs.toString()}`);
              }
            }}
          />
        </div>
        <div className="flex-1 max-w-xs">
          <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">
            Filter by Status
          </label>
          <select
            className="w-full bg-secondary/50 border border-border/50 rounded-md px-3 py-1.5 text-xs text-foreground font-data focus:border-radar/50 focus:ring-1 focus:ring-radar/50 outline-none transition-colors"
            defaultValue={currentFilters.status || ""}
            onChange={(e) => {
              const qs = new URLSearchParams(window.location.search);
              if (e.target.value) qs.set("status", e.target.value);
              else qs.delete("status");
              qs.set("page", "1");
              router.push(`/alerts/ransomware?${qs.toString()}`);
            }}
          >
            <option value="">All Statuses</option>
            <option value="LISTED">Listed</option>
            <option value="PUBLISHED">Published</option>
          </select>
        </div>
      </div>

      {/* ─── Alerts List (Phase 4.2) ────────────────────────────────────── */}
      <div className="card-soc p-0">
        <DataTable<RansomwareAlert>
          columns={columns}
          data={initialData?.items || []}
          rowKey={(row) => row.id}
          emptyMessage="No ransomware alerts detected with the current filters."
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
