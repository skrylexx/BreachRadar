/**
 * not-found.tsx — Page 404 custom
 * Cohérente avec le design SOC de BreachRadar.
 */

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "404 — Page introuvable | BreachRadar",
};

export default function NotFoundPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-6">
        {/* Code d'erreur stylisé */}
        <div className="relative">
          <p className="text-[120px] font-bold font-data text-radar/10 leading-none select-none">
            404
          </p>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-radar/10 border border-radar/20 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-radar/60"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-foreground">Page introuvable</h1>
          <p className="text-sm text-muted-foreground">
            La page que vous cherchez n&apos;existe pas ou a été déplacée.
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
