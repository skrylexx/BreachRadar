/**
 * Page 403 — Accès refusé
 * Affichée quand un Viewer tente d'accéder à une route Admin.
 */

import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "403 — Accès refusé | BreachRadar",
};

export default function ForbiddenPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-6">

        {/* Logo + code d'erreur */}
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            {/* Halo rouge derrière le logo */}
            <div className="absolute inset-0 rounded-full bg-red-500/10 blur-xl scale-150" />
            <Image
              src="/images/logo_only-nobg.png"
              alt="BreachRadar"
              width={56}
              height={56}
              className="relative w-14 h-14 object-contain opacity-80"
              priority
            />
          </div>
          <p className="text-[80px] font-bold font-data text-red-500/20 leading-none select-none">
            403
          </p>
        </div>

        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-foreground">Accès refusé</h1>
          <p className="text-sm text-muted-foreground">
            Vous n&apos;avez pas les permissions nécessaires pour accéder à cette page.
            <br />
            Cette section est réservée aux administrateurs.
          </p>
        </div>

        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
                     bg-radar/10 text-radar text-sm font-medium border border-radar/20
                     hover:bg-radar/20 transition-colors"
        >
          ← Retour au Dashboard
        </Link>
      </div>
    </div>
  );
}
