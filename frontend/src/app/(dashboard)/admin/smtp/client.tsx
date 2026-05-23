"use client";

/**
 * SmtpClient — Configuration SMTP (Admin)
 *
 * Fonctionnalités :
 *   - Formulaire SMTP : host, port, TLS/SSL toggle, user, password (masqué), from, reply-to
 *   - Bouton "Envoyer un mail de test" → feedback toast
 *   - Indicateur de statut de la configuration
 */

import { useState, useCallback } from "react";
import {
  Mail,
  Save,
  Send,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  ShieldCheck,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

// ─── Types ────────────────────────────────────────────────────────────────────

interface SmtpConfig {
  host: string;
  port: number;
  use_tls: boolean;
  use_ssl: boolean;
  username: string;
  password: string;
  from_email: string;
  reply_to: string;
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

export function SmtpClient() {
  const [config, setConfig] = useState<SmtpConfig>({
    host: "",
    port: 587,
    use_tls: true,
    use_ssl: false,
    username: "",
    password: "",
    from_email: "",
    reply_to: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testEmail, setTestEmail] = useState("");
  const { toast, show: showToast } = useToast();

  const update = (key: keyof SmtpConfig, value: string | number | boolean) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/api/v1/settings/smtp", config);
      showToast("Configuration SMTP sauvegardée.");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors de la sauvegarde.", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    if (!testEmail) {
      showToast("Entrez une adresse email de test.", "error");
      return;
    }
    setTesting(true);
    try {
      const result = await api.post<{ ok: boolean; message: string }>("/api/v1/settings/smtp/test", {
        to: testEmail,
      });
      showToast(
        result.ok ? `Email de test envoyé à ${testEmail}.` : result.message,
        result.ok ? "success" : "error"
      );
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : "Erreur lors du test SMTP.", "error");
    } finally {
      setTesting(false);
    }
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
        title="Configuration SMTP"
        description="Paramètres du serveur de messagerie pour les alertes et notifications."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "SMTP" },
        ]}
      />

      <form onSubmit={handleSave} className="space-y-4 max-w-2xl">
        <div className="card-soc p-6 space-y-6">
          {/* Serveur */}
          <div>
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
              <Mail className="w-3.5 h-3.5" />
              Serveur
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 sm:col-span-1 space-y-2">
                <Label htmlFor="smtp-host" className="text-xs text-muted-foreground uppercase tracking-wider">
                  Hôte SMTP
                </Label>
                <Input
                  id="smtp-host"
                  type="text"
                  value={config.host}
                  onChange={(e) => update("host", e.target.value)}
                  placeholder="smtp.gmail.com"
                  className="bg-secondary border-border/50 focus:border-radar/50 font-data"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp-port" className="text-xs text-muted-foreground uppercase tracking-wider">
                  Port
                </Label>
                <Input
                  id="smtp-port"
                  type="number"
                  value={config.port}
                  onChange={(e) => update("port", parseInt(e.target.value) || 587)}
                  className="bg-secondary border-border/50 focus:border-radar/50 font-data"
                />
              </div>
            </div>
          </div>

          <Separator className="bg-border/30" />

          {/* Chiffrement */}
          <div>
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5" />
              Chiffrement
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="smtp-tls" className="text-sm text-foreground">STARTTLS</Label>
                  <p className="text-xs text-muted-foreground">Recommandé pour le port 587</p>
                </div>
                <Switch
                  id="smtp-tls"
                  checked={config.use_tls}
                  onCheckedChange={(v) => update("use_tls", v)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="smtp-ssl" className="text-sm text-foreground">SSL/TLS</Label>
                  <p className="text-xs text-muted-foreground">Recommandé pour le port 465</p>
                </div>
                <Switch
                  id="smtp-ssl"
                  checked={config.use_ssl}
                  onCheckedChange={(v) => update("use_ssl", v)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-border/30" />

          {/* Authentification */}
          <div>
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
              Authentification
            </h2>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="smtp-user" className="text-xs text-muted-foreground uppercase tracking-wider">
                  Utilisateur
                </Label>
                <Input
                  id="smtp-user"
                  type="text"
                  value={config.username}
                  onChange={(e) => update("username", e.target.value)}
                  placeholder="user@example.com"
                  autoComplete="username"
                  className="bg-secondary border-border/50 focus:border-radar/50"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp-password" className="text-xs text-muted-foreground uppercase tracking-wider">
                  Mot de passe
                </Label>
                <div className="relative">
                  <Input
                    id="smtp-password"
                    type={showPassword ? "text" : "password"}
                    value={config.password}
                    onChange={(e) => update("password", e.target.value)}
                    placeholder="••••••••••••"
                    autoComplete="new-password"
                    className="bg-secondary border-border/50 focus:border-radar/50 font-data pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <Separator className="bg-border/30" />

          {/* Expéditeur */}
          <div>
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
              Expéditeur
            </h2>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="smtp-from" className="text-xs text-muted-foreground uppercase tracking-wider">
                  From
                </Label>
                <Input
                  id="smtp-from"
                  type="email"
                  value={config.from_email}
                  onChange={(e) => update("from_email", e.target.value)}
                  placeholder="breachradar@example.com"
                  className="bg-secondary border-border/50 focus:border-radar/50"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp-replyto" className="text-xs text-muted-foreground uppercase tracking-wider">
                  Reply-To <span className="text-muted-foreground/50 normal-case">(optionnel)</span>
                </Label>
                <Input
                  id="smtp-replyto"
                  type="email"
                  value={config.reply_to}
                  onChange={(e) => update("reply_to", e.target.value)}
                  placeholder="security@example.com"
                  className="bg-secondary border-border/50 focus:border-radar/50"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            id="save-smtp"
            type="submit"
            disabled={saving}
            className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Sauvegarder
          </Button>
        </div>
      </form>

      {/* Test */}
      <div className="card-soc p-6 max-w-2xl">
        <h2 className="text-sm font-medium text-foreground mb-4 flex items-center gap-2">
          <Send className="w-4 h-4 text-radar" />
          Envoyer un email de test
        </h2>
        <div className="flex items-center gap-3">
          <Input
            id="smtp-test-email"
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="destinataire@example.com"
            className="bg-secondary border-border/50 focus:border-radar/50 flex-1"
          />
          <Button
            id="smtp-test-btn"
            onClick={handleTest}
            disabled={testing || !config.host}
            variant="outline"
            className="border-border/50 hover:border-radar/30 hover:text-radar whitespace-nowrap"
          >
            {testing ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            Envoyer le test
          </Button>
        </div>
        {!config.host && (
          <p className="text-xs text-muted-foreground mt-2">
            Configurez et sauvegardez d'abord le serveur SMTP.
          </p>
        )}
      </div>
    </div>
  );
}
