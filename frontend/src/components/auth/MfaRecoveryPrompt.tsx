"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { ShieldAlert, CheckCircle2 } from "lucide-react";
import { authApi } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export function MfaRecoveryPrompt() {
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    // Ne pas afficher si on est déjà sur le profil
    if (pathname === "/profile") return;

    const checkMfaStatus = async () => {
      if (checking) return;
      
      // Ne pas afficher si déjà ignoré durant cette session
      if (sessionStorage.getItem("mfa_prompt_dismissed") === "true") {
        return;
      }

      setChecking(true);
      try {
        const user = await authApi.me();
        
        // Afficher le popup si MFA requis (post-recovery) et pas encore activé
        if (user.mfa_required && !user.mfa_enabled) {
          setOpen(true);
        }
      } catch (error) {
        // Silently fail
      } finally {
        setChecking(false);
      }
    };

    // Petit délai pour laisser le temps au middleware/cookies de se stabiliser
    const timer = setTimeout(checkMfaStatus, 1000);
    return () => clearTimeout(timer);
  }, [pathname]);

  const handleDismiss = () => {
    sessionStorage.setItem("mfa_prompt_dismissed", "true");
    setOpen(false);
  };

  const handleAccept = () => {
    setOpen(false);
    router.push("/profile?setup_mfa=true");
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => {
      if (!isOpen) handleDismiss();
      setOpen(isOpen);
    }}>
      <DialogContent className="card-soc border-radar/30 max-w-md">
        <DialogHeader>
          <div className="w-12 h-12 rounded-full bg-radar/10 flex items-center justify-center mb-4 mx-auto">
            <ShieldAlert className="w-6 h-6 text-radar animate-pulse" />
          </div>
          <DialogTitle className="text-center text-lg">Sécurisez votre compte</DialogTitle>
          <DialogDescription className="text-center text-sm pt-2 text-muted-foreground">
            Vous vous êtes connecté via un code de secours. <br />
            <span className="text-foreground">Votre authentification à deux facteurs est actuellement <strong>désactivée</strong>.</span>
            <br /><br />
            Voulez-vous réactiver votre MFA maintenant ?
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="flex flex-col sm:flex-row gap-2 pt-4">
          <Button 
            variant="ghost" 
            className="flex-1 text-xs text-muted-foreground" 
            onClick={handleDismiss}
          >
            Plus tard
          </Button>
          <Button 
            className="flex-1 bg-radar text-background font-bold hover:bg-radar-glow gap-2"
            onClick={handleAccept}
          >
            <CheckCircle2 className="w-4 h-4" />
            Réactiver maintenant
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
