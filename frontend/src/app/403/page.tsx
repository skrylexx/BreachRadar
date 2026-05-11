/**
 * Page 403 — Accès refusé
 * Affichée quand un Viewer tente d'accéder à une route Admin.
 */

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "403 — Accès refusé | BreachRadar",
};

export default function ForbiddenPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-6">
        {/* Code d'erreur stylisé */}
        <div className="relative">
          <p className="text-[120px] font-bold font-data text-radar/10 leading-none select-none">
            403
          </p>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                  />
                </svg>
              </div>
            </div>
          </div>
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
