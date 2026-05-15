import { Suspense } from "react";
import CVEClient from "./client";

/**
 * Page Veille CVE & Exploits (Server Component)
 * Route : /alerts/cve
 */

export const metadata = {
  title: "Veille CVE & Exploits | BreachRadar",
  description: "Surveillance des vulnérabilités critiques et des exploits 0-day.",
};

export default function CVEPage() {
  return (
    <Suspense fallback={<div className="p-8 text-muted-foreground animate-pulse">Chargement de la veille CVE...</div>}>
      <CVEClient />
    </Suspense>
  );
}
