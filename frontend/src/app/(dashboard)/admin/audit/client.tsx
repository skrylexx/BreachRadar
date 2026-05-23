"use client";

/**
 * AuditClient — Audit Trail (Admin)
 *
 * Fonctionnalités :
 *   - Tableau paginé (date, utilisateur, action, IP)
 *   - Filtres : utilisateur, type d'action, période
 *   - Pagination côté serveur
 *   - Export CSV de l'audit trail
 */

import { useState, useEffect, useCallback } from "react";
import {
  ShieldCheck,
  Search,
  Download,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Filter,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { auditApi, type AuditLogEntry } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { TimeFilter } from "@/components/ui/time-filter";

// ─── Types d'actions connues ──────────────────────────────────────────────────

const ACTION_LABELS: Record<string, { label: string; color: string }> = {
  login: { label: "Connexion", color: "text-green-400 border-green-400/30 bg-green-400/10" },
  logout: { label: "Déconnexion", color: "text-muted-foreground border-border/50" },
  scan_trigger: { label: "Scan lancé", color: "text-radar border-radar/30 bg-radar/10" },
  scan_complete: { label: "Scan terminé", color: "text-blue-400 border-blue-400/30 bg-blue-400/10" },
  report_export: { label: "Export rapport", color: "text-purple-400 border-purple-400/30 bg-purple-400/10" },
  report_generate: { label: "Génération rapport", color: "text-purple-400 border-purple-400/30 bg-purple-400/10" },
  user_create: { label: "Utilisateur créé", color: "text-green-400 border-green-400/30 bg-green-400/10" },
  user_disable: { label: "Utilisateur désactivé", color: "text-red-400 border-red-400/30 bg-red-400/10" },
  password_reset: { label: "Reset MDP", color: "text-yellow-400 border-yellow-400/30 bg-yellow-400/10" },
  mfa_reset: { label: "Reset MFA", color: "text-yellow-400 border-yellow-400/30 bg-yellow-400/10" },
  api_key_set: { label: "Clé API définie", color: "text-orange-400 border-orange-400/30 bg-orange-400/10" },
  api_key_delete: { label: "Clé API supprimée", color: "text-red-400 border-red-400/30 bg-red-400/10" },
  settings_update: { label: "Paramètres modifiés", color: "text-blue-400 border-blue-400/30 bg-blue-400/10" },
};

const ACTION_OPTIONS = [
  { value: "all", label: "Toutes les actions" },
  ...Object.entries(ACTION_LABELS).map(([k, v]) => ({ value: k, label: v.label })),
];

const PERIOD_OPTIONS = [
  { value: "7d", label: "7 derniers jours" },
  { value: "1m", label: "1 mois" },
  { value: "6m", label: "6 mois" },
  { value: "all", label: "Tout" },
];

// ─── Formatters ──────────────────────────────────────────────────────────────

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("fr-FR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// ─── CSV Export ───────────────────────────────────────────────────────────────

function exportCsv(entries: AuditLogEntry[]) {
  const header = "Date,Utilisateur,Action,IP";
  const rows = entries.map((e) =>
    [
      `"${formatDateTime(e.timestamp)}"`,
      `"${e.user_email}"`,
      `"${e.action}"`,
      `"${e.ip_address}"`,
    ].join(",")
  );
  const csv = [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `breachradar-audit-${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── Toast ────────────────────────────────────────────────────────────────────

function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const show = useCallback((message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }, []);
  return { toast, show };
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const PAGE_SIZE = 25;

export function AuditClient() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filtres
  const [userFilter, setUserFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("all");
  const [period, setPeriod] = useState("7d");

  const { toast, show: showToast } = useToast();

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    try {
      const response = await auditApi.list({
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
        user: userFilter || undefined,
        action: actionFilter !== "all" ? actionFilter : undefined,
        period,
      });
      setEntries(response.items);
      setTotal(response.total);
    } catch {
      showToast("Impossible de charger l'audit trail.", "error");
    } finally {
      setLoading(false);
    }
  }, [page, userFilter, actionFilter, period, showToast]);

  useEffect(() => {
    setPage(1);
  }, [userFilter, actionFilter, period]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  // ─── Colonnes ───────────────────────────────────────────────────────────────

  const columns: DataTableColumn<AuditLogEntry>[] = [
    {
      key: "timestamp",
      header: "Date",
      sortable: true,
      accessor: (e) => e.timestamp,
      render: (e) => (
        <span className="font-data text-xs text-muted-foreground">
          {formatDateTime(e.timestamp)}
        </span>
      ),
    },
    {
      key: "user_email",
      header: "Utilisateur",
      sortable: true,
      accessor: (e) => e.user_email,
      render: (e) => (
        <span className="text-sm text-foreground font-data">{e.user_email}</span>
      ),
    },
    {
      key: "action",
      header: "Action",
      render: (e) => {
        const meta = ACTION_LABELS[e.action];
        return (
          <Badge
            variant="outline"
            className={`text-[11px] ${meta?.color ?? "text-muted-foreground border-border/50"}`}
          >
            {meta?.label ?? e.action}
          </Badge>
        );
      },
    },
    {
      key: "ip_address",
      header: "IP",
      render: (e) => (
        <span className="font-data text-xs text-muted-foreground">
          {e.ip_address}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg border text-sm font-medium shadow-lg animate-in slide-in-from-bottom-4 ${
            toast.type === "success"
              ? "bg-green-500/10 border-green-500/30 text-green-400"
              : "bg-destructive/10 border-destructive/30 text-destructive"
          }`}
        >
          {toast.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
          {toast.message}
        </div>
      )}

      <PageHeader
        title="Audit Trail"
        description="Journal des actions utilisateurs — traçabilité RGPD."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "Audit Trail" },
        ]}
      >
        <Button
          id="export-audit-csv"
          variant="outline"
          size="sm"
          onClick={() => exportCsv(entries)}
          disabled={entries.length === 0}
          className="border-border/50 hover:border-radar/30 hover:text-radar text-xs"
        >
          <Download className="w-4 h-4 mr-2" />
          Exporter CSV
        </Button>
        <Button
          id="refresh-audit"
          variant="ghost"
          size="sm"
          onClick={fetchEntries}
          disabled={loading}
          className="text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </PageHeader>

      {/* Filtres */}
      <div className="card-soc p-4 flex flex-wrap items-center gap-3">
        <Filter className="w-4 h-4 text-muted-foreground flex-shrink-0" />

        {/* Filtre utilisateur */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="audit-user-filter"
            type="text"
            placeholder="Filtrer par email…"
            value={userFilter}
            onChange={(e) => setUserFilter(e.target.value)}
            className="pl-8 bg-secondary border-border/50 focus:border-radar/50 text-sm h-9"
          />
        </div>

        {/* Filtre action */}
        <Select
          value={actionFilter}
          onValueChange={(value) => setActionFilter(value ?? "all")}
        >
          <SelectTrigger
            id="audit-action-filter"
            className="w-48 bg-secondary border-border/50 h-9 text-sm"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="card-soc border-border/60 max-h-60">
            {ACTION_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value} className="text-sm">
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Filtre période */}
        <Select value={period} onValueChange={(value) => setPeriod(value ?? "7d")}>
          <SelectTrigger
            id="audit-period-filter"
            className="w-40 bg-secondary border-border/50 h-9 text-sm"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="card-soc border-border/60">
            {PERIOD_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value} className="text-sm">
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Tableau */}
      <div className="card-soc p-0 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-radar" />
            <span className="text-sm font-medium text-foreground">
              {total} entrée{total !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
        <DataTable<AuditLogEntry>
          columns={columns}
          data={entries}
          rowKey={(e) => e.id}
          loading={loading}
          emptyMessage="Aucune entrée d'audit pour les filtres sélectionnés."
          className="border-0 rounded-none"
          pagination={{
            page,
            pageSize: PAGE_SIZE,
            total,
            onPageChange: setPage,
          }}
        />
      </div>
    </div>
  );
}
