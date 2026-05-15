/**
 * not-found.tsx — Page 404 custom
 * Cohérente avec le design SOC de BreachRadar.
 */

import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "404 — Page introuvable | BreachRadar",
};

export default function NotFoundPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-6">

        {/* Logo + code d'erreur */}
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            {/* Halo cyan derrière le logo */}
            <div className="absolute inset-0 rounded-full bg-radar/10 blur-xl scale-150" />
            <Image
              src="/images/logo_only-nobg.png"
              alt="BreachRadar"
              width={56}
              height={56}
              className="relative w-14 h-14 object-contain opacity-60"
              priority
            />
          </div>
          <p className="text-[80px] font-bold font-data text-radar/15 leading-none select-none">
            404
          </p>
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
