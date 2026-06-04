"use client";

/**
 * UsersClient — User Management Page (Admin)
 *
 * Features:
 *   - Paginated table (email, role, MFA, last login, password expiration)
 *   - User creation modal (email + password + role)
 *   - Actions: disable, reset password via email, reset MFA
 *   - Password rotation indicator (alert if expired)
 */

import { useState, useEffect, useCallback } from "react";
import {
  Users,
  UserPlus,
  ShieldCheck,
  ShieldOff,
  ShieldAlert,
  KeyRound,
  Smartphone,
  SmartphoneNfc,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { usersApi, type User } from "@/lib/api";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("fr-FR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isExpired(iso: string | null): boolean {
  if (!iso) return false;
  return new Date(iso) < new Date();
}

// ─── Mini Toast ─────────────────────────────────────────────────────────────

function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const show = useCallback((message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }, []);

  return { toast, show };
}

// ─── CreateUserModal ─────────────────────────────────────────────────────────

interface CreateUserModalProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

function CreateUserModal({ open, onClose, onCreated }: CreateUserModalProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"admin" | "viewer">("viewer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const minLength = role === "admin" ? 16 : 12;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < minLength) {
      setError(`Le mot de passe doit contenir au moins ${minLength} caractères pour le rôle ${role}.`);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await usersApi.create({ email, password, role });
      onCreated();
      onClose();
      setEmail("");
      setPassword("");
      setRole("viewer");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur lors de la création.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="card-soc border-border/60 max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <UserPlus className="w-4 h-4 text-radar" />
            Créer un utilisateur
          </DialogTitle>
          <DialogDescription className="text-muted-foreground text-xs">
            Le mot de passe doit respecter la politique de sécurité :
            min <strong>16 chars</strong> (Admin) / <strong>12 chars</strong> (Viewer).
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="space-y-2">
            <Label htmlFor="create-email" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Email
            </Label>
            <Input
              id="create-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="bg-secondary border-border/50 focus:border-radar/50"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="create-password" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Mot de passe
            </Label>
            <Input
              id="create-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={`Minimum ${minLength} caractères`}
              className="bg-secondary border-border/50 focus:border-radar/50 font-data"
            />
            <p className="text-xs text-muted-foreground">
              {password.length < minLength ? (
                <span className="text-yellow-500">
                  {minLength - password.length} caractère(s) manquant(s)
                </span>
              ) : (
                <span className="text-green-500 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Longueur valide
                </span>
              )}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="create-role" className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Rôle
            </Label>
            <Select value={role} onValueChange={(v) => setRole(v as "admin" | "viewer")}>
              <SelectTrigger id="create-role" className="bg-secondary border-border/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="card-soc border-border/60">
                <SelectItem value="viewer">Viewer</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 border border-destructive/30 text-destructive text-sm">
              <XCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <DialogFooter className="mt-6">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={loading}
              className="text-muted-foreground"
            >
              Annuler
            </Button>
            <Button
              id="create-user-submit"
              type="submit"
              disabled={loading}
              className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <UserPlus className="w-4 h-4 mr-2" />
                  Créer
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── ConfirmModal ─────────────────────────────────────────────────────────────

interface ConfirmModalProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  onConfirm: () => Promise<void>;
  onClose: () => void;
}

function ConfirmModal({ open, title, description, confirmLabel = "Confirmer", onConfirm, onClose }: ConfirmModalProps) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="card-soc border-border/60 max-w-sm">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            {title}
          </DialogTitle>
          <DialogDescription className="text-muted-foreground text-sm mt-2">
            {description}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4">
          <Button variant="ghost" onClick={onClose} disabled={loading} className="text-muted-foreground">
            Annuler
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={loading}
            className="bg-destructive/20 hover:bg-destructive/30 text-destructive border border-destructive/30"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function UsersClient() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    description: string;
    label: string;
    fn: () => Promise<void>;
  } | null>(null);
  const { toast, show: showToast } = useToast();

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await usersApi.list();
      setUsers(data);
    } catch {
      showToast("Impossible de charger les utilisateurs.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDisable = (user: User) => {
    setConfirmAction({
      title: `Désactiver ${user.email}`,
      description: "L'utilisateur ne pourra plus se connecter. Cette action est réversible depuis la base de données.",
      label: "Désactiver",
      fn: async () => {
        await usersApi.disable(user.id);
        showToast(`${user.email} désactivé.`);
        setConfirmAction(null);
        fetchUsers();
      },
    });
  };

  const handleResetPassword = (user: User) => {
    setConfirmAction({
      title: "Reset mot de passe",
      description: `Un email de réinitialisation sera envoyé à ${user.email}. Assurez-vous que le SMTP est configuré.`,
      label: "Envoyer le reset",
      fn: async () => {
        await usersApi.resetPassword(user.id);
        showToast(`Email de reset envoyé à ${user.email}.`);
        setConfirmAction(null);
      },
    });
  };

  const handleResetMfa = (user: User) => {
    setConfirmAction({
      title: "Reset MFA",
      description: `Cela supprimera le secret TOTP de ${user.email}. L'utilisateur devra reconfigurer son application d'authentification.`,
      label: "Reset MFA",
      fn: async () => {
        await usersApi.resetMfa(user.id);
        showToast(`MFA réinitialisé pour ${user.email}.`);
        setConfirmAction(null);
        fetchUsers();
      },
    });
  };

  const handleRequireMfa = (user: User) => {
    setConfirmAction({
      title: "Forcer le MFA",
      description: `L'utilisateur ${user.email} devra obligatoirement configurer et valider son MFA lors de sa prochaine connexion.`,
      label: "Forcer le MFA",
      fn: async () => {
        await usersApi.requireMfa(user.id);
        showToast(`MFA désormais requis pour ${user.email}.`);
        setConfirmAction(null);
        fetchUsers();
      },
    });
  };

  // ─── Columns ─────────────────────────────────────────────────────────────

  const columns: DataTableColumn<User>[] = [
    {
      key: "email",
      header: "Email",
      sortable: true,
      accessor: (u) => u.email,
      render: (u) => (
        <span className="font-data text-sm text-foreground">
          {u.email}
          {!u.is_active && (
            <Badge variant="outline" className="ml-2 text-[10px] text-red-400 border-red-400/30">
              Désactivé
            </Badge>
          )}
        </span>
      ),
    },
    {
      key: "role",
      header: "Rôle",
      width: "100px",
      render: (u) => (
        <Badge
          variant="outline"
          className={
            u.role === "admin"
              ? "text-radar border-radar/30 bg-radar/10"
              : "text-muted-foreground border-border/50"
          }
        >
          {u.role}
        </Badge>
      ),
    },
    {
      key: "mfa",
      header: "MFA",
      width: "80px",
      render: (u) => (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <span className="flex items-center gap-1">
                {u.mfa_enabled ? (
                  <ShieldCheck className="w-4 h-4 text-green-400" />
                ) : u.mfa_required ? (
                  <ShieldAlert className="w-4 h-4 text-yellow-400 animate-pulse" />
                ) : (
                  <ShieldOff className="w-4 h-4 text-muted-foreground" />
                )}
              </span>
            </TooltipTrigger>
            <TooltipContent side="top" className="text-xs">
              {u.mfa_enabled ? "MFA activé" : u.mfa_required ? "MFA Obligatoire (En attente)" : "MFA désactivé"}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ),
    },
    {
      key: "last_login",
      header: "Dernière connexion",
      sortable: true,
      accessor: (u) => u.last_login_at ?? "",
      render: (u) => (
        <span className="font-data text-xs text-muted-foreground">
          {formatDate(u.last_login_at)}
        </span>
      ),
    },
    {
      key: "password_expires",
      header: "Expiration MDP",
      render: (u) => {
        const expired = isExpired(u.password_expires_at);
        return (
          <span className={`font-data text-xs flex items-center gap-1 ${expired ? "text-red-400" : "text-muted-foreground"}`}>
            {expired && <AlertTriangle className="w-3 h-3" />}
            {formatDate(u.password_expires_at)}
          </span>
        );
      },
    },
    {
  key: "actions",
  header: "Actions",
  width: "140px",
  render: (u) => (
    <div className="flex items-center gap-1">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>
            <button
              id={`reset-password-${u.id}`}
              onClick={(e) => { e.stopPropagation(); handleResetPassword(u); }}
              className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
            >
              <KeyRound className="w-3.5 h-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" className="text-xs">Reset MDP</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger>
            <button
              id={`require-mfa-${u.id}`}
              onClick={(e) => { e.stopPropagation(); handleRequireMfa(u); }}
              className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-yellow-400 transition-colors"
              disabled={u.mfa_enabled || u.mfa_required}
            >
              <SmartphoneNfc className="w-3.5 h-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" className="text-xs">Forcer MFA</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger>
            <button
              id={`reset-mfa-${u.id}`}
              onClick={(e) => { e.stopPropagation(); handleResetMfa(u); }}
              className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
              disabled={!u.mfa_enabled}
            >
              <Smartphone className="w-3.5 h-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" className="text-xs">Reset MFA</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger>
            <button
              id={`disable-user-${u.id}`}
              onClick={(e) => { e.stopPropagation(); handleDisable(u); }}
              className="p-1.5 rounded hover:bg-destructive/20 text-muted-foreground hover:text-red-400 transition-colors"
              disabled={!u.is_active}
            >
              <XCircle className="w-3.5 h-3.5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="top" className="text-xs">Désactiver</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  ),
},
  ];

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg border text-sm font-medium shadow-lg transition-all animate-in slide-in-from-bottom-4 ${
            toast.type === "success"
              ? "bg-green-500/10 border-green-500/30 text-green-400"
              : "bg-destructive/10 border-destructive/30 text-destructive"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircle2 className="w-4 h-4" />
          ) : (
            <XCircle className="w-4 h-4" />
          )}
          {toast.message}
        </div>
      )}

      <PageHeader
        title="Gestion des utilisateurs"
        description="Créer, désactiver et gérer les accès des utilisateurs de l'instance."
        breadcrumb={[
          { label: "Admin", href: "/admin/users" },
          { label: "Utilisateurs" },
        ]}
      >
        <Button
          id="refresh-users"
          variant="ghost"
          size="sm"
          onClick={fetchUsers}
          className="text-muted-foreground hover:text-foreground"
        >
          <RefreshCw className="w-4 h-4" />
        </Button>
        <Button
          id="create-user-btn"
          onClick={() => setCreateOpen(true)}
          className="bg-radar/20 hover:bg-radar/30 text-radar border border-radar/30 text-sm"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Créer un utilisateur
        </Button>
      </PageHeader>

      {/* Politique MDP */}
      <div className="card-soc p-4 flex items-start gap-3 border-l-2 border-l-radar/40">
        <ShieldCheck className="w-4 h-4 text-radar mt-0.5 flex-shrink-0" />
        <div className="text-xs text-muted-foreground space-y-1">
          <p className="font-medium text-foreground/80">Politique de mot de passe</p>
          <p>Admin : minimum <strong className="text-foreground">16 caractères</strong> · Rotation tous les <strong className="text-foreground">180 jours</strong></p>
          <p>Viewer : minimum <strong className="text-foreground">12 caractères</strong> · Rotation tous les <strong className="text-foreground">180 jours</strong></p>
          <p className="text-foreground/50">Exception : rotation non requise si le MDP dépasse 24 caractères.</p>
        </div>
      </div>

      {/* Tableau */}
      <div className="card-soc p-0 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-radar" />
            <span className="text-sm font-medium text-foreground">
              {users.length} utilisateur{users.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
        <DataTable<User>
          columns={columns}
          data={users}
          rowKey={(u) => u.id}
          loading={loading}
          emptyMessage="Aucun utilisateur trouvé."
          className="border-0 rounded-none"
        />
      </div>

      {/* Modals */}
      <CreateUserModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={() => { fetchUsers(); showToast("Utilisateur créé avec succès."); }}
      />

      {confirmAction && (
        <ConfirmModal
          open={true}
          title={confirmAction.title}
          description={confirmAction.description}
          confirmLabel={confirmAction.label}
          onConfirm={confirmAction.fn}
          onClose={() => setConfirmAction(null)}
        />
      )}
    </div>
  );
}
