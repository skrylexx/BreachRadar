"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { User, Mail, Shield, Lock, Save, Loader2, Key, CheckCircle2, AlertCircle, DownloadCloud, Copy } from "lucide-react";
import { authApi, User as UserType } from "@/lib/api";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function ProfilePage() {
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Password Change State
  const [pwdDialogOpen, setPwdDialogOpen] = useState(false);
  const [pwdData, setPwdData] = useState({ current: "", new: "", confirm: "" });
  const [pwdLoading, setPwdLoading] = useState(false);

  // MFA State
  const [mfaDialogOpen, setMfaDialogOpen] = useState(false);
  const [mfaStep, setMfaStep] = useState<"setup" | "confirm" | "backup">("setup");
  const [mfaSetupData, setMfaSetupData] = useState<{ qrcode_base64: string; manual_entry_key: string; backup_codes: string[] } | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [mfaLoading, setMfaLoading] = useState(false);

  // MFA Disable State
  const [mfaDisableDialogOpen, setMfaDisableDialogOpen] = useState(false);
  const [mfaDisableCode, setMfaDisableCode] = useState("");

  const fetchUser = async () => {
    try {
      const data = await authApi.me();
      setUser(data);
    } catch (error) {
      console.error("Error fetching user profile:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  // Détection du paramètre setup_mfa pour lancement automatique
  const searchParams = useSearchParams();
  useEffect(() => {
    if (searchParams.get("setup_mfa") === "true" && user && !user.mfa_enabled) {
      setMfaDialogOpen(true);
      startMfaSetup();
    }
  }, [searchParams, user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      // Simulate profile update (only specific fields if implemented)
      await new Promise((resolve) => setTimeout(resolve, 800));
      setMessage({ type: "success", text: "Profil mis à jour avec succès." });
    } catch {
      setMessage({ type: "error", text: "Erreur lors de la mise à jour." });
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (pwdData.new !== pwdData.confirm) {
      alert("Les mots de passe ne correspondent pas.");
      return;
    }
    setPwdLoading(true);
    try {
      const updatedUser = await authApi.passwordChange({
        current_password: pwdData.current,
        new_password: pwdData.new,
        new_password_confirm: pwdData.confirm,
      });
      setUser(updatedUser);
      setPwdDialogOpen(false);
      setPwdData({ current: "", new: "", confirm: "" });
      alert("Mot de passe modifié avec succès.");
    } catch (err: any) {
      alert(err.message || "Erreur lors du changement de mot de passe.");
    } finally {
      setPwdLoading(false);
    }
  };

  const startMfaSetup = async () => {
    setMfaLoading(true);
    try {
      const data = await authApi.mfaSetup();
      setMfaSetupData(data);
      setMfaStep("confirm");
    } catch (err: any) {
      alert("Erreur lors de l'initialisation du MFA.");
    } finally {
      setMfaLoading(false);
    }
  };

  const handleMfaConfirm = async () => {
    setMfaLoading(true);
    try {
      const updatedUser = await authApi.mfaConfirm(mfaCode);
      setUser(updatedUser);
      setMfaStep("backup"); // Passer à l'étape des backup codes
      setMfaCode("");
    } catch (err: any) {
      alert("Code invalide. Veuillez réessayer.");
    } finally {
      setMfaLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    if (!mfaSetupData?.backup_codes) return;
    const content = `BREACHRADAR - CODES DE SECOURS MFA\nGénéré le: ${new Date().toLocaleString()}\n\n${mfaSetupData.backup_codes.join("\n")}\n\nGardez ces codes précieusement. Chaque code est à usage unique.`;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `breachradar-backup-codes-${user?.email}.txt`;
    link.click();
  };

  const handleMfaDisable = async () => {
    setMfaLoading(true);
    try {
      const updatedUser = await authApi.mfaDisable(mfaDisableCode);
      setUser(updatedUser);
      setMfaDisableDialogOpen(false);
      setMfaDisableCode("");
      alert("MFA désactivé avec succès.");
    } catch (err: any) {
      alert(err.message || "Code invalide. Impossible de désactiver le MFA.");
    } finally {
      setMfaLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-muted-foreground animate-pulse">Chargement du profil...</div>;
  }

  if (!user) {
    return <div className="p-8 text-red-400">Impossible de charger le profil utilisateur.</div>;
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <PageHeader title="Mon Profil" icon={User} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne gauche : Infos générales */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6 bg-card/30">
            <h3 className="text-sm font-semibold mb-6 flex items-center gap-2">
              <Shield className="w-4 h-4 text-radar" />
              Informations Personnelles
            </h3>

            <form onSubmit={handleSave} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Adresse Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                      type="email"
                      value={user.email}
                      disabled
                      className="w-full pl-10 pr-4 py-2 bg-secondary/50 border border-border rounded-md
                                 text-sm font-data opacity-50 cursor-not-allowed text-foreground"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Rôle</label>
                  <div className="relative">
                    <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                      type="text"
                      value={user.role.toUpperCase()}
                      disabled
                      className="w-full pl-10 pr-4 py-2 bg-secondary/50 border border-border rounded-md
                                 text-sm font-data opacity-50 cursor-not-allowed text-foreground"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-border/50 flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  L'adresse email et le rôle ne peuvent être modifiés que par un administrateur.
                </p>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-2 px-4 py-2 bg-radar text-background
                             rounded-md text-sm font-semibold hover:bg-radar-glow
                             disabled:opacity-50 transition-all"
                >
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  Enregistrer
                </button>
              </div>
              
              {message && (
                <p className={`text-xs mt-2 ${message.type === "success" ? "text-green-400" : "text-red-400"}`}>
                  {message.text}
                </p>
              )}
            </form>
          </Card>

          <Card className="p-6 bg-card/30">
            <h3 className="text-sm font-semibold mb-6 flex items-center gap-2">
              <Lock className="w-4 h-4 text-radar" />
              Sécurité & Mot de passe
            </h3>

            <div className="space-y-4">
              <p className="text-xs text-muted-foreground">
                Votre mot de passe doit comporter au moins 16 caractères (Admin) ou 12 caractères (Viewer).
                Il expire tous les 180 jours.
              </p>
              
              <Button
                variant="secondary"
                onClick={() => setPwdDialogOpen(true)}
                className="flex items-center gap-2"
              >
                <Key className="w-4 h-4" />
                Changer de mot de passe
              </Button>
            </div>
          </Card>
        </div>

        {/* Colonne droite : Status MFA / Sessions */}
        <div className="space-y-6">
          <Card className="p-6 bg-card/30">
            <h3 className="text-sm font-semibold mb-6 flex items-center gap-2">
              <Shield className="w-4 h-4 text-radar" />
              Authentification MFA
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Double Authentification (TOTP)</p>
                  <p className="text-xs text-muted-foreground">
                    {user.mfa_enabled ? "Activé" : "Non activé"}
                  </p>
                </div>
                <div className={`w-2 h-2 rounded-full ${user.mfa_enabled ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500"}`} />
              </div>

              {!user.mfa_enabled && (
                <Button
                  variant="outline"
                  onClick={() => setMfaDialogOpen(true)}
                  className="w-full border-radar/20 text-radar hover:bg-radar/5"
                >
                  Activer le MFA
                </Button>
              )}

              {user.mfa_enabled && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="w-full">
                        <Button
                          variant="outline"
                          onClick={() => setMfaDisableDialogOpen(true)}
                          disabled={user.mfa_required}
                          className="w-full border-destructive/20 text-destructive hover:bg-destructive/5 disabled:opacity-50"
                        >
                          Désactiver le MFA
                        </Button>
                      </div>
                    </TooltipTrigger>
                    {user.mfa_required && (
                      <TooltipContent side="top" className="text-xs bg-destructive text-destructive-foreground">
                        Le MFA est obligatoire pour votre compte (politique admin).
                      </TooltipContent>
                    )}
                  </Tooltip>
                </TooltipProvider>
              )}
            </div>
          </Card>

          <Card className="p-6 bg-card/30">
            <h3 className="text-sm font-semibold mb-6">Dernière Connexion</h3>
            <div className="space-y-1">
              <p className="text-sm font-data">
                {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "Première connexion"}
              </p>
              <p className="text-[10px] text-muted-foreground font-data uppercase">
                IP: 127.0.0.1 (Local)
              </p>
            </div>
          </Card>
        </div>
      </div>

      {/* ─── Dialog Changement de Mot de Passe ──────────────────────────────── */}
      <Dialog open={pwdDialogOpen} onOpenChange={setPwdDialogOpen}>
        <DialogContent className="card-soc border-border/60 max-w-md">
          <DialogHeader>
            <DialogTitle>Changer mon mot de passe</DialogTitle>
            <DialogDescription className="text-xs">
              Saisissez votre mot de passe actuel ainsi que le nouveau.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-1.5">
              <Label className="text-xs">Mot de passe actuel</Label>
              <Input
                type="password"
                autoFocus
                value={pwdData.current}
                onChange={(e) => setPwdData({ ...pwdData, current: e.target.value })}
                className="bg-secondary/50 border-border/50"
              />
            </div>
            <Separator className="bg-border/20" />
            <div className="space-y-1.5">
              <Label className="text-xs">Nouveau mot de passe</Label>
              <Input
                type="password"
                value={pwdData.new}
                onChange={(e) => setPwdData({ ...pwdData, new: e.target.value })}
                className="bg-secondary/50 border-border/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Confirmer le nouveau mot de passe</Label>
              <Input
                type="password"
                value={pwdData.confirm}
                onChange={(e) => setPwdData({ ...pwdData, confirm: e.target.value })}
                className="bg-secondary/50 border-border/50"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => setPwdDialogOpen(false)}>Annuler</Button>
            <Button
              onClick={handlePasswordChange}
              disabled={pwdLoading || !pwdData.current || !pwdData.new}
              className="bg-radar/20 text-radar border border-radar/30"
            >
              {pwdLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
              Mettre à jour
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ─── Dialog Activation MFA ─────────────────────────────────────────── */}
      <Dialog open={mfaDialogOpen} onOpenChange={(open) => {
        if (!open && mfaStep === "backup") {
          // Si on ferme alors qu'on est aux backup codes, on reset tout
          setMfaStep("setup");
        }
        setMfaDialogOpen(open);
      }}>
        <DialogContent className="card-soc border-border/60 max-w-md">
          <DialogHeader>
            <DialogTitle>
              {mfaStep === "backup" ? "Sauvegardez vos codes de secours" : "Configuration Double Authentification"}
            </DialogTitle>
            <DialogDescription className="text-xs">
              {mfaStep === "backup" ? "C'est votre seule chance de les voir." : "Renforcez la sécurité de votre compte avec TOTP."}
            </DialogDescription>
          </DialogHeader>

          {mfaStep === "setup" ? (
            <div className="py-8 text-center space-y-4">
              <Shield className="w-12 h-12 text-radar mx-auto opacity-50" />
              <p className="text-sm text-muted-foreground px-4">
                Une clé secrète va être générée. Vous devrez la scanner avec votre application (Google Authenticator, Bitwarden, etc.).
              </p>
              <Button onClick={startMfaSetup} disabled={mfaLoading}>
                {mfaLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Générer ma clé secrète"}
              </Button>
            </div>
          ) : mfaStep === "confirm" ? (
            <div className="space-y-6 py-4">
              <div className="flex justify-center bg-white p-4 rounded-lg">
                <img src={mfaSetupData?.qrcode_base64} alt="MFA QR Code" className="w-48 h-48" />
              </div>
              
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Clé manuelle : <span className="font-data text-foreground select-all">{mfaSetupData?.manual_entry_key}</span></Label>
                <Separator className="bg-border/20 my-4" />
                <Label className="text-xs">Code de vérification (6 chiffres)</Label>
                <Input
                  placeholder="000000"
                  maxLength={6}
                  autoFocus
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && mfaCode.length === 6) {
                      e.preventDefault();
                      handleMfaConfirm();
                    }
                  }}
                  className="bg-secondary/50 border-border/50 text-center text-lg tracking-[0.5em] font-data"
                />
              </div>
              
              <DialogFooter>
                <Button variant="ghost" onClick={() => { setMfaStep("setup"); setMfaDialogOpen(false); }}>Annuler</Button>
                <Button
                  onClick={handleMfaConfirm}
                  disabled={mfaLoading || mfaCode.length !== 6}
                  className="bg-radar/20 text-radar border border-radar/30"
                >
                  {mfaLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle2 className="w-4 h-4 mr-2" />}
                  Vérifier et Activer
                </Button>
              </DialogFooter>
            </div>
          ) : (
            <div className="space-y-6 py-4">
              <div className="p-4 rounded-md bg-green-500/5 border border-green-500/20 text-center">
                <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <h4 className="text-sm font-semibold text-green-400">MFA Activé avec succès !</h4>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Codes de secours</Label>
                  <Button variant="ghost" size="sm" className="h-7 text-[10px]" onClick={downloadBackupCodes}>
                    <DownloadCloud className="w-3 h-3 mr-1" /> Télécharger (.txt)
                  </Button>
                </div>
                
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  Conservez ces codes en lieu sûr. Ils vous permettront d'accéder à votre compte si vous perdez votre appareil.
                  <strong> Chaque code n'est utilisable qu'une seule fois.</strong>
                </p>

                <div className="grid grid-cols-2 gap-2 bg-secondary/30 p-3 rounded border border-border/40 font-data text-xs">
                  {mfaSetupData?.backup_codes.map(code => (
                    <div key={code} className="p-1 select-all hover:text-radar transition-colors">{code}</div>
                  ))}
                </div>
              </div>

              <DialogFooter>
                <Button className="w-full bg-radar text-background font-bold hover:bg-radar-glow" onClick={() => { setMfaDialogOpen(false); setMfaStep("setup"); }}>
                  J'ai enregistré mes codes
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
      {/* ─── Dialog Désactivation MFA ────────────────────────────────────────── */}
      <Dialog open={mfaDisableDialogOpen} onOpenChange={setMfaDisableDialogOpen}>
        <DialogContent className="card-soc border-border/60 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-destructive flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Désactiver le MFA
            </DialogTitle>
            <DialogDescription className="text-xs">
              La désactivation du MFA réduit la sécurité de votre compte.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <p className="text-sm text-muted-foreground">
              Pour confirmer la désactivation, veuillez saisir le code TOTP actuel de votre application.
            </p>
            <div className="space-y-1.5">
              <Label className="text-xs">Code de vérification (6 chiffres)</Label>
              <Input
                placeholder="000000"
                maxLength={6}
                autoFocus
                value={mfaDisableCode}
                onChange={(e) => setMfaDisableCode(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && mfaDisableCode.length === 6) {
                    e.preventDefault();
                    handleMfaDisable();
                  }
                }}
                className="bg-secondary/50 border-border/50 text-center text-lg tracking-[0.5em] font-data"
              />
            </div>
            
            <div className="p-3 rounded-md bg-yellow-500/5 border border-yellow-500/20">
              <p className="text-[11px] text-yellow-500/80 leading-relaxed">
                <strong>Accès perdu ?</strong> Si vous n'avez plus accès à votre application TOTP, 
                veuillez contacter un administrateur pour réinitialiser votre MFA manuellement.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => setMfaDisableDialogOpen(false)}>Annuler</Button>
            <Button
              onClick={handleMfaDisable}
              disabled={mfaLoading || mfaDisableCode.length !== 6}
              className="bg-destructive/20 text-destructive border border-destructive/30"
            >
              {mfaLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Confirmer la désactivation"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
