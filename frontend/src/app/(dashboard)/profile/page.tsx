"use client";

import { useState, useEffect } from "react";
import { User, Mail, Shield, Lock, Save, Loader2, Key } from "lucide-react";
import { authApi, User as UserType } from "@/lib/api";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";

export default function ProfilePage() {
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
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
    fetchUser();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      // Simulate save (Endpoint to be implemented if needed)
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessage({ type: "success", text: "Profil mis à jour avec succès." });
    } catch {
      setMessage({ type: "error", text: "Erreur lors de la mise à jour." });
    } finally {
      setSaving(false);
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
                                 text-sm font-data opacity-50 cursor-not-allowed"
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
                                 text-sm font-data opacity-50 cursor-not-allowed"
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
              
              <button
                className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-accent
                           border border-border rounded-md text-sm transition-colors"
              >
                <Key className="w-4 h-4" />
                Changer de mot de passe
              </button>
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
                <button
                  className="w-full py-2 bg-radar/10 text-radar border border-radar/20
                             rounded-md text-sm font-medium hover:bg-radar/20 transition-all"
                >
                  Activer le MFA
                </button>
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
    </div>
  );
}
