"use client";

/**
 * SchedulingClient — Configuration du scheduler de scans (Admin)
 *
 * Fonctionnalités :
 *   - Toggle activation/désactivation du cron
 *   - Champ expression cron avec validation et affichage lisible
 *   - Affichage du prochain run prévu
 *   - Historique des 5 dernières exécutions planifiées
 */

import { useState, useEffect, useCallback } from "react";
import {
  Clock,
  Play,
  Pause,
  RefreshCw,
  CheckCircle2,
  XCircle,
  CalendarDays,
  History,
  ChevronRight,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

// ─── Types ────────────────────────────────────────────────────────────────────

interface SchedulerStatus {
  enabled: boolean;
  cron_expression: string;
  next_run_at: string | null;
  last_run_at: string | null;
  history: Array<{
    id: string;
    started_at: string;
    status: "completed" | "failed" | "running";
    duration_seconds: number | null;
    findings_count: number;
  }>;
}

// ─── Cron → lisible ──────────────────────────────────────────────────────────

function cronToHuman(expr: string): string {
  // Patterns courants
  const patterns: Record<string, string> = {
    "0 * * * *": "Toutes les heures",
    "0 */6 * * *": "Toutes les 6 heures",
    "0 */12 * * *": "Toutes les 12 heures",
    "0 0 * * *": "Tous les jours à minuit",
    "0 8 * * *": "Tous les jours à 08h00",
    "0 8 * * 1": "Tous les lundis à 08h00",
    "0 8 * * 1-5": "Du lundi au vendredi à 08h00",
    "0 0 * * 0": "Tous les dimanches à minuit",
    "0 0 1 * *": "Le 1er de chaque mois à minuit",
  };
  return patterns[expr] ?? `Expression cron : ${expr}`;
}

// ─── Toast ────────────────────────────────────────────────────────────────────

function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const show = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };
  return { toast, show };
}

// ─── Formatters ──────────────────────────────────────────────────────────────

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("fr-FR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDuration(s: number | null): string {
  if (!s) return "—";
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}min ${s % 60}s`;
}

// ─── Preset crons ────────────────────────────────────────────────────────────

const PRESETS = [
  { label: "Toutes les heures", value: "0 * * * *" },
  { label: "Toutes les 6h", value: "0 */6 * * *" },
  { label: "Tous les jours à 08h00", value: "0 8 * * *" },
  { label: "Lundi à 08h00", value: "0 8 * * 1" },
  { label: "Lun-Ven à 08h00", value: "0 8 * * 1-5" },
  { label: "1er du mois", value: "0 0 1 * *" },
];

// ─── Main ─────────────────────────────────────────────────────────────────────

export function SchedulingClient() {
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [cronExpr, setCronExpr] = useState("0 8 * * 1");
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast, show: showToast } = useToast();

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<SchedulerStatus>("/api/v1/scheduler/status");
      setStatus(data);
      setCronExpr(data.cron_expression);
      setEnabled(data.enabled);
    } catch {
      showToast("Impossible de charger le statut du scheduler.", "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/api/v1/scheduler/config", {
        enabled,
        cron_expression: cronExpr,
      });
      showToast("Configuration du scheduler sauvegardée.");
      fetchStatus();
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors de la sauvegarde.", "error");
    } finally {
      setSaving(false);
    }
  };

  const statusColors = {
    completed: "text-green-400 border-green-400/30 bg-green-400/10",
    failed: "text-red-400 border-red-400/30 bg-red-400/10",
    running: "text-radar border-radar/30 bg-radar/10",
  };

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
        title="Planification des scans"
        description="Configurer le scheduler automatique des scans OSINT."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "Scheduling" },
        ]}
      >
        <Button
          id="refresh-scheduler"
          variant="ghost"
          size="sm"
          onClick={fetchStatus}
          disabled={loading}
          className="text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Statut rapide */}
        <div className="card-soc p-4 flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${enabled ? "bg-green-400/10" : "bg-border/30"}`}>
            {enabled ? (
              <Play className="w-5 h-5 text-green-400" />
            ) : (
              <Pause className="w-5 h-5 text-muted-foreground" />
            )}
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Statut</p>
            <p className={`text-sm font-medium ${enabled ? "text-green-400" : "text-muted-foreground"}`}>
              {enabled ? "Actif" : "Inactif"}
            </p>
          </div>
        </div>

        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-radar/10 flex items-center justify-center">
            <CalendarDays className="w-5 h-5 text-radar" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Prochain run</p>
            <p className="text-sm font-medium font-data text-foreground">
              {formatDateTime(status?.next_run_at ?? null)}
            </p>
          </div>
        </div>

        <div className="card-soc p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
            <History className="w-5 h-5 text-muted-foreground" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Dernier run</p>
            <p className="text-sm font-medium font-data text-foreground">
              {formatDateTime(status?.last_run_at ?? null)}
            </p>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <form onSubmit={handleSave} className="card-soc p-6 space-y-6 max-w-2xl">
        <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-3.5 h-3.5" />
          Configuration
        </h2>

        {/* Toggle activation */}
        <div className="flex items-center justify-between py-3 border-b border-border/30">
          <div>
            <Label htmlFor="scheduler-enabled" className="text-sm text-foreground">
              Activer le scheduler
            </Label>
            <p className="text-xs text-muted-foreground mt-0.5">
              Lorsqu'il est désactivé, aucun scan automatique n'est lancé.
            </p>
          </div>
          <Switch
            id="scheduler-enabled"
            checked={enabled}
            onCheckedChange={setEnabled}
          />
        </div>

        {/* Expression cron */}
        <div className="space-y-3">
          <Label htmlFor="cron-expr" className="text-xs text-muted-foreground uppercase tracking-wider">
            Expression Cron
          </Label>
          <div className="flex items-center gap-3">
            <Input
              id="cron-expr"
              type="text"
              value={cronExpr}
              onChange={(e) => setCronExpr(e.target.value)}
              placeholder="0 8 * * 1"
              className="bg-secondary border-border/50 focus:border-radar/50 font-data flex-1"
            />
          </div>
          <p className="text-xs text-radar/80 flex items-center gap-1">
            <ChevronRight className="w-3 h-3" />
            {cronToHuman(cronExpr)}
          </p>
        </div>

        {/* Presets */}
        <div>
          <p className="text-xs text-muted-foreground mb-2">Raccourcis :</p>
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((preset) => (
              <button
                key={preset.value}
                type="button"
                onClick={() => setCronExpr(preset.value)}
                className={`px-3 py-1.5 rounded-md text-xs transition-colors border ${
                  cronExpr === preset.value
                    ? "bg-radar/10 text-radar border-radar/30"
                    : "text-muted-foreground border-border/50 hover:border-radar/20 hover:text-foreground"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            id="save-scheduler"
            type="submit"
            disabled={saving}
            className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Clock className="w-4 h-4 mr-2" />
            )}
            Sauvegarder
          </Button>
        </div>
      </form>

      {/* Historique */}
      {status?.history && status.history.length > 0 && (
        <div className="card-soc p-0 overflow-hidden max-w-2xl">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
            <History className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">
              5 dernières exécutions planifiées
            </span>
          </div>
          <div className="divide-y divide-border/30">
            {status.history.map((run) => (
              <div key={run.id} className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-3">
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${statusColors[run.status]}`}
                  >
                    {run.status}
                  </Badge>
                  <span className="text-sm font-data text-muted-foreground">
                    {formatDateTime(run.started_at)}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs font-data text-muted-foreground">
                  <span>{formatDuration(run.duration_seconds)}</span>
                  <span>{run.findings_count} findings</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
