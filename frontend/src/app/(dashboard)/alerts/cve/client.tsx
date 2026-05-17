"use client";

import { useEffect, useState } from "react";
import {
  Bug,
  ExternalLink,
  RefreshCw,
  Search,
  Filter,
  AlertTriangle,
} from "lucide-react";
import {
  cveApi,
  CVEAlert,
  CVESourceStatus,
  DashboardChartPoint,
  Severity,
} from "@/lib/api";
import { PageHeader } from "@/components/ui/page-header";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { StatusDot } from "@/components/ui/status-dot";
import { DataTable } from "@/components/ui/data-table";
import { TimeFilter, type TimePeriod } from "@/components/ui/time-filter";
import { Card } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function CVEClient() {
  const [alerts, setAlerts] = useState<CVEAlert[]>([]);
  const [status, setStatus] = useState<CVESourceStatus[]>([]);
  const [trend, setTrend] = useState<DashboardChartPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  const [period, setPeriod] = useState<TimePeriod>("7d");
  const [severityFilter, setSeverityFilter] = useState<Severity | "ALL">("ALL");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const isMock = alerts.length > 0 && alerts[0].id.startsWith("mock-");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [alertsRes, statusRes, trendRes] = await Promise.all([
        cveApi.getAlerts({ 
          limit: 25, 
          offset: (page - 1) * 25,
          severity: severityFilter === "ALL" ? undefined : severityFilter,
          period 
        }),
        cveApi.getStatus(),
        cveApi.getTrend(period),
      ]);
      setAlerts(alertsRes.items);
      setTotal(alertsRes.total);
      setStatus(statusRes);
      setTrend(trendRes);
    } catch (error) {
      console.error("Error fetching CVE data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [page, period, severityFilter]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const columns = [
    {
      key: "cve_id",
      header: "CVE ID",
      render: (item: CVEAlert) => {
        const url = item.source === "GitHub" 
          ? `https://github.com/advisories/${item.cve_id}`
          : `https://nvd.nist.gov/vuln/detail/${item.cve_id}`;
        return (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-radar hover:underline font-data"
          >
            {item.cve_id}
            <ExternalLink className="w-3 h-3" />
          </a>
        );
      },
    },
    {
      key: "title",
      header: "Titre / Description",
      render: (item: CVEAlert) => (
        <div className="max-w-md">
          <p className="font-medium text-foreground truncate" title={item.title}>
            {item.title}
          </p>
          <p className="text-xs text-muted-foreground line-clamp-1" title={item.description}>
            {item.description}
          </p>
        </div>
      ),
    },
    {
      key: "severity",
      header: "Sévérité",
      render: (item: CVEAlert) => <SeverityBadge level={item.severity} />,
    },
    {
      key: "cvss_score",
      header: "Score CVSS",
      render: (item: CVEAlert) => (
        <span className="font-data text-sm">
          {item.cvss_score?.toFixed(1) || "N/A"}
        </span>
      ),
    },
    {
      key: "category",
      header: "Catégorie",
      render: (item: CVEAlert) => (
        <span className="px-2 py-0.5 rounded-full bg-secondary text-[10px] font-medium border border-border">
          {item.category}
        </span>
      ),
    },
    {
      key: "source",
      header: "Source",
      render: (item: CVEAlert) => (
        <span className="text-xs text-muted-foreground uppercase">{item.source}</span>
      ),
    },
    {
      key: "published_at",
      header: "Publication",
      render: (item: CVEAlert) => (
        <span className="text-xs font-data">
          {new Date(item.published_at).toLocaleDateString()}
        </span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {isMock && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 flex items-center gap-3 text-orange-400">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div className="text-sm">
            <span className="font-bold uppercase mr-2">Mode Démonstration :</span>
            Aucune CVE réelle n'est encore en base. Des données de démonstration sont affichées.
          </div>
        </div>
      )}
      <PageHeader
        title="Veille CVE & Exploits"
        icon={Bug}
      >
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-1.5 bg-secondary hover:bg-accent
                     border border-border rounded-md text-xs font-medium transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
          Rafraîchir
        </button>
      </PageHeader>

      {/* ─── Statut des sources ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {status.map((src) => (
          <Card key={src.source} className="p-4 flex items-center justify-between bg-card/30">
            <div className="flex items-center gap-3">
              <StatusDot status={src.status === "ok" ? "ok" : "error"} />
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground">
                  {src.source}
                </p>
                <p className="text-lg font-bold text-foreground">{src.item_count}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-muted-foreground">Synchro</p>
              <p className="text-[10px] font-data">
                {src.last_synced_at ? new Date(src.last_synced_at).toLocaleTimeString() : "Jamais"}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* ─── Graphique d'évolution ─────────────────────────────────────── */}
      <Card className="p-6 bg-card/30">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            Volume des détections
            <span className="text-xs font-normal text-muted-foreground">
              (par sévérité)
            </span>
          </h3>
          <TimeFilter value={period} onChange={setPeriod} />
        </div>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
              <XAxis
                dataKey="date"
                stroke="#71717a"
                fontSize={10}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#71717a"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#18181b",
                  border: "1px solid #27272a",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                cursor={{ fill: "#27272a", opacity: 0.4 }}
              />
              <Legend iconType="circle" wrapperStyle={{ fontSize: "10px", paddingTop: "20px" }} />
              <Bar dataKey="critical" name="Critique" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
              <Bar dataKey="high" name="Haut" stackId="a" fill="#f97316" radius={[0, 0, 0, 0]} />
              <Bar dataKey="medium" name="Moyen" stackId="a" fill="#eab308" radius={[0, 0, 0, 0]} />
              <Bar dataKey="low" name="Bas" stackId="a" fill="#3b82f6" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* ─── Filtres et Tableau ────────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Rechercher une CVE..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-secondary border border-border rounded-md
                         text-sm focus:outline-none focus:ring-1 focus:ring-radar transition-all"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as Severity | "ALL")}
              className="bg-secondary border border-border rounded-md text-xs px-3 py-2 outline-none"
            >
              <option value="ALL">Toutes les sévérités</option>
              <option value="CRITICAL">Critique</option>
              <option value="HIGH">Haut</option>
              <option value="MEDIUM">Moyen</option>
              <option value="LOW">Bas</option>
            </select>
          </div>
        </div>

        <Card className="overflow-hidden border-border/50">
          <DataTable
            columns={columns}
            data={alerts}
            rowKey={(item: CVEAlert) => item.id}
            loading={loading}
            pagination={{
              page,
              pageSize: 25,
              total,
              onPageChange: setPage,
            }}
          />
        </Card>
      </div>
    </div>
  );
}
