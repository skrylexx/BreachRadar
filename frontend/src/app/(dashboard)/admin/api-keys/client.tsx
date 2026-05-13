"use client";

/**
 * ApiKeysClient — Page de gestion des clés API connecteurs (Admin)
 *
 * Fonctionnalités :
 *   - Grille de cartes par source (nom, statut is_set, date MAJ)
 *   - Dialog "Définir / Remplacer" : input password vide (jamais pré-rempli)
 *   - Dialog "Supprimer" : confirmation modale
 *   - Bouton "Tester" → health-check → toast résultat
 *   - Avertissement sécurité affiché en permanence
 *
 * SÉCURITÉ : Aucune valeur de clé n'est jamais affichée — uniquement is_set: bool + date
 */

import { useState, useEffect, useCallback } from "react";
import {
  Key,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Trash2,
  FlaskConical,
  Eye,
  EyeOff,
  AlertTriangle,
  Shield,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { apiKeysApi, type ApiKeyStatus } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

// ─── Sources catalogue (ordre d'affichage) ────────────────────────────────────

const SOURCES = [
  { id: "hibp", label: "HaveIBeenPwned", variable: "HIBP_API_KEY", tier: "free" },
  { id: "github", label: "GitHub", variable: "GITHUB_TOKEN", tier: "free" },
  { id: "gitlab", label: "GitLab", variable: "GITLAB_TOKEN", tier: "free" },
  { id: "urlscan", label: "URLScan.io", variable: "URLSCAN_API_KEY", tier: "free" },
  { id: "otx", label: "AlienVault OTX", variable: "OTX_API_KEY", tier: "free" },
  { id: "leakcheck", label: "LeakCheck.io", variable: "LEAKCHECK_API_KEY", tier: "paid" },
  { id: "dehashed_email", label: "Dehashed (email)", variable: "DEHASHED_EMAIL", tier: "paid" },
  { id: "dehashed", label: "Dehashed (clé)", variable: "DEHASHED_API_KEY", tier: "paid" },
  { id: "intelx", label: "Intelligence X", variable: "INTELX_API_KEY", tier: "paid" },
  { id: "shodan", label: "Shodan", variable: "SHODAN_API_KEY", tier: "paid" },
  { id: "hunter", label: "Hunter.io", variable: "HUNTER_API_KEY", tier: "paid" },
  { id: "ransomlook_saas", label: "RansomLook SaaS", variable: "RANSOMLOOK_SAAS_API_KEY", tier: "saas" },
  { id: "nvd", label: "NVD (NIST)", variable: "CVE_NVD_API_KEY", tier: "free" },
];

// ─── Toast ────────────────────────────────────────────────────────────────────

function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const show = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };
  return { toast, show };
}

// ─── SetKeyModal ──────────────────────────────────────────────────────────────

interface SetKeyModalProps {
  source: typeof SOURCES[number] | null;
  onClose: () => void;
  onSaved: () => void;
  showToast: (msg: string, type?: "success" | "error") => void;
}

function SetKeyModal({ source, onClose, onSaved, showToast }: SetKeyModalProps) {
  const [value, setValue] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!source) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim()) return;
    setLoading(true);
    try {
      await apiKeysApi.set(source.id, value.trim());
      showToast(`Clé pour ${source.label} enregistrée.`);
      onSaved();
      onClose();
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors de l'enregistrement.", "error");
    } finally {
      setLoading(false);
      setValue("");
      setShow(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="card-soc border-border/60 max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <Key className="w-4 h-4 text-radar" />
            Définir la clé — {source.label}
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Variable : <code className="font-data text-radar/80">{source.variable}</code>
            <br />
            Le champ est toujours vide à l'ouverture — saisir remplace la valeur existante.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-2">
            <Label htmlFor="api-key-value" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Nouvelle valeur
            </Label>
            <div className="relative">
              <Input
                id="api-key-value"
                type={show ? "text" : "password"}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Nouvelle valeur…"
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
                className="bg-secondary border-border/50 focus:border-radar/50 font-data pr-10"
              />
              <button
                type="button"
                onClick={() => setShow(!show)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="ghost" onClick={onClose} disabled={loading} className="text-muted-foreground">
              Annuler
            </Button>
            <Button
              id={`save-key-${source.id}`}
              type="submit"
              disabled={loading || !value.trim()}
              className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Enregistrer"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── DeleteKeyModal ───────────────────────────────────────────────────────────

interface DeleteKeyModalProps {
  source: typeof SOURCES[number] | null;
  onClose: () => void;
  onDeleted: () => void;
  showToast: (msg: string, type?: "success" | "error") => void;
}

function DeleteKeyModal({ source, onClose, onDeleted, showToast }: DeleteKeyModalProps) {
  const [loading, setLoading] = useState(false);

  if (!source) return null;

  const handleDelete = async () => {
    setLoading(true);
    try {
      await apiKeysApi.delete(source.id);
      showToast(`Clé ${source.label} supprimée.`);
      onDeleted();
      onClose();
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors de la suppression.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="card-soc border-border/60 max-w-sm">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <Trash2 className="w-4 h-4 text-red-400" />
            Supprimer la clé — {source.label}
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground mt-2">
            La valeur en base sera supprimée. Si une clé est présente dans le <code className="font-data">.env</code>, elle reste active.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4">
          <Button variant="ghost" onClick={onClose} disabled={loading} className="text-muted-foreground">
            Annuler
          </Button>
          <Button
            id={`delete-key-${source.id}`}
            onClick={handleDelete}
            disabled={loading}
            className="bg-destructive/20 hover:bg-destructive/30 text-destructive border border-destructive/30"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Supprimer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ─── SourceCard ───────────────────────────────────────────────────────────────

interface SourceCardProps {
  source: typeof SOURCES[number];
  status?: ApiKeyStatus;
  onSet: () => void;
  onDelete: () => void;
  onTest: () => Promise<void>;
}

function SourceCard({ source, status, onSet, onDelete, onTest }: SourceCardProps) {
  const [testing, setTesting] = useState(false);
  const isSet = status?.is_set ?? false;

  const handleTest = async () => {
    setTesting(true);
    try {
      await onTest();
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className={`card-soc p-4 border transition-colors ${isSet ? "border-border/50 hover:border-radar/20" : "border-border/30 opacity-75 hover:opacity-100"}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">{source.label}</span>
            <Badge
              variant="outline"
              className={
                source.tier === "free"
                  ? "text-green-400 border-green-400/30 text-[10px]"
                  : source.tier === "paid"
                  ? "text-yellow-400 border-yellow-400/30 text-[10px]"
                  : "text-purple-400 border-purple-400/30 text-[10px]"
              }
            >
              {source.tier === "free" ? "Gratuit" : source.tier === "paid" ? "Payant" : "SaaS"}
            </Badge>
          </div>
          <code className="text-[11px] text-muted-foreground font-data">{source.variable}</code>
        </div>

        <div className="flex items-center gap-1.5">
          {isSet ? (
            <CheckCircle2 className="w-4 h-4 text-green-400" title="Clé définie" />
          ) : (
            <div className="w-4 h-4 rounded-full border-2 border-border/50" title="Clé absente" />
          )}
        </div>
      </div>

      {status?.updated_at && (
        <p className="text-[11px] text-muted-foreground font-data mb-3">
          Modifiée le {new Date(status.updated_at).toLocaleDateString("fr-FR")}
        </p>
      )}

      <div className="flex items-center gap-2 mt-auto">
        <Button
          id={`set-key-${source.id}`}
          size="sm"
          variant="outline"
          onClick={onSet}
          className="text-xs h-7 border-border/50 hover:border-radar/30 hover:text-radar"
        >
          <Key className="w-3 h-3 mr-1" />
          {isSet ? "Remplacer" : "Définir"}
        </Button>

        {isSet && (
          <>
            <Button
              id={`test-key-${source.id}`}
              size="sm"
              variant="ghost"
              onClick={handleTest}
              disabled={testing}
              className="text-xs h-7 text-muted-foreground hover:text-foreground"
            >
              {testing ? (
                <RefreshCw className="w-3 h-3 animate-spin mr-1" />
              ) : (
                <FlaskConical className="w-3 h-3 mr-1" />
              )}
              Tester
            </Button>

            <Button
              id={`delete-key-${source.id}`}
              size="sm"
              variant="ghost"
              onClick={onDelete}
              className="text-xs h-7 text-muted-foreground hover:text-red-400 ml-auto"
            >
              <Trash2 className="w-3 h-3" />
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export function ApiKeysClient() {
  const [statuses, setStatuses] = useState<ApiKeyStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [setTarget, setSetTarget] = useState<typeof SOURCES[number] | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<typeof SOURCES[number] | null>(null);
  const { toast, show: showToast } = useToast();

  const fetchStatuses = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiKeysApi.list();
      setStatuses(data);
    } catch {
      showToast("Impossible de charger les clés API.", "error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatuses();
  }, [fetchStatuses]);

  const getStatus = (id: string) => statuses.find((s) => s.source === id);

  const handleTest = async (source: typeof SOURCES[number]) => {
    try {
      const result = await apiKeysApi.test(source.id);
      showToast(
        result.ok ? `✅ ${source.label} : ${result.message}` : `❌ ${source.label} : ${result.message}`,
        result.ok ? "success" : "error"
      );
    } catch (err: unknown) {
      showToast(`Erreur test ${source.label}: ${err instanceof Error ? err.message : "inconnue"}`, "error");
    }
  };

  // Séparer free et paid
  const freeSources = SOURCES.filter((s) => s.tier === "free");
  const paidSources = SOURCES.filter((s) => s.tier !== "free");

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg border text-sm font-medium shadow-lg transition-all animate-in slide-in-from-bottom-4 max-w-sm ${
            toast.type === "success"
              ? "bg-green-500/10 border-green-500/30 text-green-400"
              : "bg-destructive/10 border-destructive/30 text-destructive"
          }`}
        >
          {toast.type === "success" ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> : <XCircle className="w-4 h-4 flex-shrink-0" />}
          {toast.message}
        </div>
      )}

      <PageHeader
        title="Clés API & Intégrations"
        description="Gérez les clés d'API pour chaque connecteur OSINT."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "Clés API" },
        ]}
      >
        <Button
          id="refresh-api-keys"
          variant="ghost"
          size="sm"
          onClick={fetchStatuses}
          disabled={loading}
          className="text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </PageHeader>

      {/* Avertissement sécurité */}
      <div className="card-soc p-4 flex items-start gap-3 border-l-2 border-l-yellow-500/50">
        <Shield className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-muted-foreground space-y-1">
          <p className="font-medium text-foreground/80">Sécurité des clés API</p>
          <p>Les clés sont stockées en base de données chiffrée. Elles seront <strong className="text-foreground">perdues si le volume Docker est supprimé</strong>.</p>
          <p>Pour une persistance garantie, renseignez-les dans votre <code className="font-data text-radar/70">.env</code>. Les valeurs <code className="font-data">.env</code> sont prioritaires sur celles de la base.</p>
        </div>
      </div>

      {/* Section gratuit */}
      <div>
        <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
          Sources gratuites
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {freeSources.map((source) => (
            <SourceCard
              key={source.id}
              source={source}
              status={getStatus(source.id)}
              onSet={() => setSetTarget(source)}
              onDelete={() => setDeleteTarget(source)}
              onTest={() => handleTest(source)}
            />
          ))}
        </div>
      </div>

      {/* Section payant */}
      <div>
        <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
          <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" />
          Sources payantes & SaaS
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {paidSources.map((source) => (
            <SourceCard
              key={source.id}
              source={source}
              status={getStatus(source.id)}
              onSet={() => setSetTarget(source)}
              onDelete={() => setDeleteTarget(source)}
              onTest={() => handleTest(source)}
            />
          ))}
        </div>
      </div>

      {/* Modals */}
      <SetKeyModal
        source={setTarget}
        onClose={() => setSetTarget(null)}
        onSaved={fetchStatuses}
        showToast={showToast}
      />
      <DeleteKeyModal
        source={deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onDeleted={fetchStatuses}
        showToast={showToast}
      />
    </div>
  );
}
