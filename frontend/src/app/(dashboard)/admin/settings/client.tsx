"use client";

/**
 * SettingsClient — Paramètres globaux de l'instance BreachRadar (Admin)
 *
 * Onglets :
 *   - Général : TARGET_DOMAIN, langue par défaut, mode maintenance
 *   - Surveillance CVE : toggles par catégorie (NVD / OSV / GitHub / CVEFeed)
 *   - Notifications : alertes email CVE, seuil, destinataires
 *   - Sources Custom : flux RSS/Atom personnalisés
 *   - Avancé : polling interval, inclure CVE sans score, vider cache
 *
 * Phase 10 du TODO.md.
 */

import { useState, useEffect } from "react";
import {
  Settings,
  Globe,
  Bell,
  Shield,
  ChevronRight,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Trash2,
  AlertTriangle,
  Eye,
  EyeOff,
  Save,
  Plus,
  Link as LinkIcon,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { cveApi, api, type CVESettings } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

// ─── Catégories CVE ────────────────────────────────────────────────────────────

const CVE_CATEGORIES = [
  { group: "NVD", id: "nvd_windows", label: "Windows (Microsoft)" },
  { group: "NVD", id: "nvd_linux", label: "Linux Kernel" },
  { group: "NVD", id: "nvd_macos", label: "macOS / iOS (Apple)" },
  { group: "OSV.dev", id: "osv_npm", label: "Open Source (npm)" },
  { group: "OSV.dev", id: "osv_pypi", label: "Open Source (PyPI)" },
  { group: "OSV.dev", id: "osv_go", label: "Open Source (Go)" },
  { group: "OSV.dev", id: "osv_maven", label: "Open Source (Maven/Java)" },
  { group: "OSV.dev", id: "osv_rubygems", label: "Open Source (RubyGems)" },
  { group: "OSV.dev", id: "osv_nuget", label: "Open Source (NuGet/.NET)" },
  { group: "GitHub Advisories", id: "github_advisories", label: "GitHub Advisories" },
  { group: "CVEFeed.io", id: "cvefeed_critical", label: "CVE Critiques (toutes)" },
  { group: "CVEFeed.io", id: "cvefeed_high", label: "CVE Hautes (toutes)" },
];

const CVE_GROUPS = ["NVD", "OSV.dev", "GitHub Advisories", "CVEFeed.io"];

// ─── Toast ────────────────────────────────────────────────────────────────────

function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const show = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };
  return { toast, show };
}

// ─── Tab Général ─────────────────────────────────────────────────────────────

function TabGeneral({ showToast }: { showToast: (msg: string, type?: "success" | "error") => void }) {
  const [domain, setDomain] = useState("");
  const [lang, setLang] = useState("fr");
  const [maintenance, setMaintenance] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/api/v1/settings/general", { domain, default_language: lang, maintenance_mode: maintenance });
      showToast("Paramètres généraux sauvegardés.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors de la sauvegarde.", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="space-y-6">
      <div className="card-soc p-6 space-y-6">
        {/* TARGET_DOMAIN */}
        <div className="space-y-2">
          <Label htmlFor="target-domain" className="text-xs text-muted-foreground uppercase tracking-wider">
            Domaine cible (TARGET_DOMAIN)
          </Label>
          <Input
            id="target-domain"
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            className="bg-secondary border-border/50 focus:border-radar/50 font-data"
          />
          <p className="text-xs text-muted-foreground">
            Utilisé dans les rapports et la bannière de l'interface.
          </p>
        </div>

        <Separator className="bg-border/30" />

        {/* Langue */}
        <div className="space-y-2">
          <Label htmlFor="default-lang" className="text-xs text-muted-foreground uppercase tracking-wider">
            Langue par défaut
          </Label>
          <Select value={lang} onValueChange={(value) => setLang(value ?? "fr")}>
            <SelectTrigger id="default-lang" className="w-40 bg-secondary border-border/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="card-soc border-border/60">
              <SelectItem value="fr">Français</SelectItem>
              <SelectItem value="en">English</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator className="bg-border/30" />

        {/* Mode maintenance */}
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="maintenance-mode" className="text-sm text-foreground">
              Mode maintenance
            </Label>
            <p className="text-xs text-muted-foreground mt-0.5">
              Affiche une bannière d'avertissement à tous les utilisateurs.
            </p>
          </div>
          <Switch
            id="maintenance-mode"
            checked={maintenance}
            onCheckedChange={setMaintenance}
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button
          id="save-general"
          type="submit"
          disabled={saving}
          className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
          Sauvegarder
        </Button>
      </div>
    </form>
  );
}

// ─── Tab Surveillance CVE ─────────────────────────────────────────────────────

function TabCVE({ showToast }: { showToast: (msg: string, type?: "success" | "error") => void }) {
  const [settings, setSettings] = useState<CVESettings | null>(null);
  const [nvdKey, setNvdKey] = useState("");
  const [showNvdKey, setShowNvdKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingKey, setSavingKey] = useState(false);

  useEffect(() => {
    cveApi.getSettings().then((data) => setSettings(data)).catch(() => {});
  }, []);

  const toggleCategory = (id: string) => {
    if (!settings) return;
    const active = settings.active_categories.includes(id);
    const next = active
      ? settings.active_categories.filter((c) => c !== id)
      : [...settings.active_categories, id];
    setSettings({ ...settings, active_categories: next });
  };

  const activeCount = settings?.active_categories.length ?? 0;

  const handleSaveCategories = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await cveApi.updateSettings(settings);
      showToast("Configuration CVE sauvegardée.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNvdKey = async () => {
    if (!nvdKey.trim()) return;
    setSavingKey(true);
    try {
      await api.put("/api/v1/settings/nvd-key", { value: nvdKey.trim() });
      showToast("Clé NVD enregistrée.");
      setNvdKey("");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setSavingKey(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Clé NVD */}
      <div className="card-soc p-4 flex items-start gap-3 border-l-2 border-l-radar/40">
        <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-xs font-medium text-foreground/80 mb-1">Clé API NVD (optionnelle)</p>
          <p className="text-xs text-muted-foreground mb-3">
            Sans clé : 5 requêtes / 30s. Avec clé : 50 requêtes / 30s.
          </p>
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Input
                id="nvd-api-key"
                type={showNvdKey ? "text" : "password"}
                value={nvdKey}
                onChange={(e) => setNvdKey(e.target.value)}
                placeholder="Nouvelle valeur…"
                autoComplete="off"
                className="bg-secondary border-border/50 focus:border-radar/50 font-data pr-10 text-sm"
              />
              <button
                type="button"
                onClick={() => setShowNvdKey(!showNvdKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showNvdKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </button>
            </div>
            <Button
              id="save-nvd-key"
              onClick={handleSaveNvdKey}
              disabled={savingKey || !nvdKey.trim()}
              size="sm"
              className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
            >
              {savingKey ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : "Enregistrer"}
            </Button>
          </div>
        </div>
      </div>

      {/* Catégories */}
      <div className="card-soc p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Catégories actives
          </h2>
          <span className="text-xs text-muted-foreground">
            <span className="text-foreground font-medium">{activeCount}</span> / {CVE_CATEGORIES.length} active{activeCount !== 1 ? "s" : ""}
          </span>
        </div>

        {CVE_GROUPS.map((group) => (
          <div key={group}>
            <p className="text-xs text-radar/70 font-medium mb-3 flex items-center gap-1">
              <ChevronRight className="w-3 h-3" />
              {group}
            </p>
            <div className="space-y-2 ml-4">
              {CVE_CATEGORIES.filter((c) => c.group === group).map((cat) => (
                <div key={cat.id} className="flex items-center justify-between py-2">
                  <Label htmlFor={`cve-cat-${cat.id}`} className="text-sm text-foreground cursor-pointer">
                    {cat.label}
                  </Label>
                  <Switch
                    id={`cve-cat-${cat.id}`}
                    checked={settings?.active_categories.includes(cat.id) ?? false}
                    onCheckedChange={() => toggleCategory(cat.id)}
                  />
                </div>
              ))}
            </div>
            <Separator className="bg-border/20 mt-4" />
          </div>
        ))}

        <div className="flex justify-end">
          <Button
            id="save-cve-categories"
            onClick={handleSaveCategories}
            disabled={saving}
            className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
          >
            {saving ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Sauvegarder
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Tab Notifications ────────────────────────────────────────────────────────

function TabNotifications({ showToast }: { showToast: (msg: string, type?: "success" | "error") => void }) {
  const [enabled, setEnabled] = useState(false);
  const [threshold, setThreshold] = useState<"CRITICAL" | "HIGH" | "MEDIUM">("CRITICAL");
  const [recipients, setRecipients] = useState("");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/api/v1/settings/notifications", {
        cve_alerts_enabled: enabled,
        min_severity: threshold,
        recipients: recipients.split(",").map((r) => r.trim()).filter(Boolean),
      });
      showToast("Configuration des notifications sauvegardée.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      await api.post("/api/v1/settings/notifications/test");
      showToast("Email de test envoyé.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setTesting(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="space-y-4">
      <div className="card-soc p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="notif-enabled" className="text-sm text-foreground">
              Alertes email CVE critiques
            </Label>
            <p className="text-xs text-muted-foreground mt-0.5">Requiert un SMTP configuré dans l'onglet SMTP.</p>
          </div>
          <Switch id="notif-enabled" checked={enabled} onCheckedChange={setEnabled} />
        </div>

        <Separator className="bg-border/30" />

        <div className="space-y-2">
          <Label htmlFor="notif-threshold" className="text-xs text-muted-foreground uppercase tracking-wider">
            Sévérité minimale d'alerte
          </Label>
          <Select value={threshold} onValueChange={(v) => setThreshold(v as typeof threshold)}>
            <SelectTrigger id="notif-threshold" className="w-48 bg-secondary border-border/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="card-soc border-border/60">
              <SelectItem value="CRITICAL">CRITICAL uniquement</SelectItem>
              <SelectItem value="HIGH">HIGH et supérieur</SelectItem>
              <SelectItem value="MEDIUM">MEDIUM et supérieur</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="notif-recipients" className="text-xs text-muted-foreground uppercase tracking-wider">
            Destinataires
          </Label>
          <Input
            id="notif-recipients"
            type="text"
            value={recipients}
            onChange={(e) => setRecipients(e.target.value)}
            placeholder="sec@example.com, admin@example.com"
            className="bg-secondary border-border/50 focus:border-radar/50"
          />
          <p className="text-xs text-muted-foreground">Séparer les adresses par des virgules.</p>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Button
          type="button"
          id="test-notification"
          variant="outline"
          onClick={handleTest}
          disabled={testing || !enabled}
          className="border-border/50 hover:border-radar/30 text-sm"
        >
          {testing ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Bell className="w-4 h-4 mr-2" />}
          Envoyer un test
        </Button>
        <Button
          id="save-notifications"
          type="submit"
          disabled={saving}
          className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
          Sauvegarder
        </Button>
      </div>
    </form>
  );
}

// ─── Tab Sources Custom ───────────────────────────────────────────────────────

function TabCustomSources({ showToast }: { showToast: (msg: string, type?: "success" | "error") => void }) {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newSource, setNewSource] = useState({ name: "", url: "", category: "General" });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>("/api/v1/settings/custom-sources");
      setSources(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleAdd = async () => {
    if (!newSource.name || !newSource.url) return;
    try {
      await api.post("/api/v1/settings/custom-sources", newSource);
      showToast("Source ajoutée avec succès.");
      setDialogOpen(false);
      setNewSource({ name: "", url: "", category: "General" });
      setTestResult(null);
      fetchSources();
    } catch (err: any) {
      showToast(err.message || "Erreur lors de l'ajout.", "error");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/api/v1/settings/custom-sources/${id}`);
      showToast("Source supprimée.");
      fetchSources();
    } catch (err: any) {
      showToast("Erreur lors de la suppression.", "error");
    }
  };

  const handleTest = async () => {
    if (!newSource.url) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.post<any>("/api/v1/settings/custom-sources/test", { url: newSource.url });
      setTestResult(res);
      if (!res.ok) showToast(res.message || "Test échoué.", "error");
    } catch (err) {
      showToast("Erreur réseau lors du test.", "error");
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="card-soc p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Sources RSS / Atom personnalisées
          </h2>
          <Button
            size="sm"
            onClick={() => setDialogOpen(true)}
            className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30 h-7 text-[10px]"
          >
            <Plus className="w-3 h-3 mr-1" />
            Ajouter
          </Button>
        </div>

        {loading ? (
          <div className="py-8 text-center text-muted-foreground animate-pulse">Chargement...</div>
        ) : sources.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <LinkIcon className="w-8 h-8 text-muted-foreground/20 mx-auto" />
            <p className="text-xs text-muted-foreground">Aucune source personnalisée configurée.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sources.map((src) => (
              <div key={src.id} className="flex items-center justify-between p-3 rounded-md bg-secondary/30 border border-border/40">
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{src.name}</span>
                  <span className="text-[10px] text-muted-foreground font-data truncate max-w-xs">{src.url}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] bg-radar/10 text-radar px-1.5 py-0.5 rounded border border-radar/20">
                    {src.category}
                  </span>
                  <button
                    onClick={() => handleDelete(src.id)}
                    className="p-1.5 text-muted-foreground hover:text-red-400 transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="card-soc border-border/60 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-foreground">Ajouter une source personnalisée</DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              Entrez l'URL d'un flux RSS ou Atom pour l'intégrer à la veille CVE.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label htmlFor="src-name" className="text-xs">Nom de la source</Label>
              <Input
                id="src-name"
                placeholder="ex: CERT-FR Avis"
                value={newSource.name}
                onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                className="bg-secondary border-border/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="src-url" className="text-xs">URL du flux</Label>
              <div className="flex gap-2">
                <Input
                  id="src-url"
                  placeholder="https://..."
                  value={newSource.url}
                  onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                  className="bg-secondary border-border/50 font-data flex-1"
                />
                <Button
                  variant="outline"
                  onClick={handleTest}
                  disabled={testing || !newSource.url}
                  className="border-border/50 h-9"
                >
                  {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : "Tester"}
                </Button>
              </div>
            </div>

            {testResult && (
              <div className={`p-3 rounded-md border text-[10px] space-y-2 ${testResult.ok ? "bg-green-500/5 border-green-500/20" : "bg-red-500/5 border-red-500/20"}`}>
                <div className="flex items-center justify-between">
                  <span className="font-bold">{testResult.ok ? "Test Réussi" : "Test Échoué"}</span>
                  {testResult.ok && <span className="text-muted-foreground">{testResult.item_count} items trouvés</span>}
                </div>
                {!testResult.ok && <p className="text-red-400">{testResult.message}</p>}
                {testResult.ok && testResult.preview && (
                  <ul className="space-y-1 list-disc list-inside text-muted-foreground">
                    {testResult.preview.map((item: any, i: number) => (
                      <li key={i} className="truncate">{item.title}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => setDialogOpen(false)} className="text-muted-foreground">
              Annuler
            </Button>
            <Button
              onClick={handleAdd}
              disabled={!newSource.name || !newSource.url || (testResult && !testResult.ok)}
              className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
            >
              Ajouter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// ─── Tab Avancé ──────────────────────────────────────────────────────────────

function TabAdvanced({ showToast }: { showToast: (msg: string, type?: "success" | "error") => void }) {
  const [pollingInterval, setPollingInterval] = useState(60);
  const [includeUnscored, setIncludeUnscored] = useState(false);
  const [saving, setSaving] = useState(false);
  const [clearConfirm, setClearConfirm] = useState(false);
  const [clearing, setClearing] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/api/v1/settings/advanced", {
        cve_polling_interval: pollingInterval,
        include_unscored_cve: includeUnscored,
      });
      showToast("Paramètres avancés sauvegardés.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleClearCache = async () => {
    setClearing(true);
    try {
      await api.delete("/api/v1/cve/cache");
      showToast("Cache CVE vidé.");
      setClearConfirm(false);
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur.", "error");
    } finally {
      setClearing(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSave} className="space-y-4">
        <div className="card-soc p-6 space-y-6">
          <div className="space-y-2">
            <Label htmlFor="polling-interval" className="text-xs text-muted-foreground uppercase tracking-wider">
              Intervalle de polling CVE (minutes)
            </Label>
            <Input
              id="polling-interval"
              type="number"
              min={5}
              max={1440}
              value={pollingInterval}
              onChange={(e) => setPollingInterval(parseInt(e.target.value) || 60)}
              className="w-32 bg-secondary border-border/50 focus:border-radar/50 font-data"
            />
            <p className="text-xs text-muted-foreground">Défaut : 60 min. Minimum : 5 min.</p>
          </div>

          <Separator className="bg-border/30" />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="include-unscored" className="text-sm text-foreground">
                Inclure les CVE sans score CVSS
              </Label>
              <p className="text-xs text-muted-foreground mt-0.5">Désactivé par défaut.</p>
            </div>
            <Switch id="include-unscored" checked={includeUnscored} onCheckedChange={setIncludeUnscored} />
          </div>

          <Separator className="bg-border/30" />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="mock-data" className="text-sm text-foreground">
                Données de démonstration (Mocks)
              </Label>
              <p className="text-xs text-muted-foreground mt-0.5">
                Affiche des données factices pour les connecteurs non configurés.
              </p>
            </div>
            <Switch id="mock-data" checked={mockData} onCheckedChange={setMockData} />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Button
            type="button"
            id="clear-cve-cache"
            variant="outline"
            onClick={() => setClearConfirm(true)}
            className="border-destructive/30 text-destructive hover:bg-destructive/10 text-sm"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Vider le cache CVE
          </Button>
          <Button
            id="save-advanced"
            type="submit"
            disabled={saving}
            className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
          >
            {saving ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Sauvegarder
          </Button>
        </div>
      </form>

      {/* Confirmation vider cache */}
      <Dialog open={clearConfirm} onOpenChange={(v) => !v && setClearConfirm(false)}>
        <DialogContent className="card-soc border-border/60 max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-foreground">
              <Trash2 className="w-4 h-4 text-red-400" />
              Vider le cache CVE
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground mt-2">
              Toutes les CVE en cache seront supprimées. Elles seront re-fetched lors du prochain polling.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="ghost" onClick={() => setClearConfirm(false)} disabled={clearing} className="text-muted-foreground">
              Annuler
            </Button>
            <Button
              id="confirm-clear-cache"
              onClick={handleClearCache}
              disabled={clearing}
              className="bg-destructive/20 hover:bg-destructive/30 text-destructive border border-destructive/30"
            >
              {clearing ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Vider"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export function SettingsClient() {
  const { toast, show: showToast } = useToast();

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
        title="Paramètres de l'instance"
        description="Configuration globale de BreachRadar."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "Paramètres" },
        ]}
      />

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="bg-secondary border border-border/50 h-auto p-1 gap-1">
          <TabsTrigger
            value="general"
            className="text-xs data-[state=active]:bg-radar/10 data-[state=active]:text-radar data-[state=active]:border data-[state=active]:border-radar/20"
          >
            <Globe className="w-3.5 h-3.5 mr-1.5" />
            Général
          </TabsTrigger>
          <TabsTrigger
            value="cve"
            className="text-xs data-[state=active]:bg-radar/10 data-[state=active]:text-radar data-[state=active]:border data-[state=active]:border-radar/20"
          >
            <Shield className="w-3.5 h-3.5 mr-1.5" />
            Surveillance CVE
          </TabsTrigger>
          <TabsTrigger
            value="notifications"
            className="text-xs data-[state=active]:bg-radar/10 data-[state=active]:text-radar data-[state=active]:border data-[state=active]:border-radar/20"
          >
            <Bell className="w-3.5 h-3.5 mr-1.5" />
            Notifications
          </TabsTrigger>
          <TabsTrigger
            value="custom"
            className="text-xs data-[state=active]:bg-radar/10 data-[state=active]:text-radar data-[state=active]:border data-[state=active]:border-radar/20"
          >
            <LinkIcon className="w-3.5 h-3.5 mr-1.5" />
            Sources Custom
          </TabsTrigger>
          <TabsTrigger
            value="advanced"
            className="text-xs data-[state=active]:bg-radar/10 data-[state=active]:text-radar data-[state=active]:border data-[state=active]:border-radar/20"
          >
            <Settings className="w-3.5 h-3.5 mr-1.5" />
            Avancé
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <TabGeneral showToast={showToast} />
        </TabsContent>
        <TabsContent value="cve">
          <TabCVE showToast={showToast} />
        </TabsContent>
        <TabsContent value="notifications">
          <TabNotifications showToast={showToast} />
        </TabsContent>
        <TabsContent value="custom">
          <TabCustomSources showToast={showToast} />
        </TabsContent>
        <TabsContent value="advanced">
          <TabAdvanced showToast={showToast} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
