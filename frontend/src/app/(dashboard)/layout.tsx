import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { DomainBanner } from "@/components/layout/DomainBanner";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard",
};

/**
 * Layout du dashboard authentifié.
 * Structure : Sidebar fixe fine (icônes) + Header + DomainBanner + zone de contenu principale.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* ─── Sidebar fine (icônes uniquement) ──────────────────────────────── */}
      <Sidebar />

      {/* ─── Zone principale ────────────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />

        {/* Bannière domaine cible */}
        <DomainBanner />

        {/* Contenu scrollable */}
        <main
          className="flex-1 overflow-y-auto custom-scrollbar p-6"
          id="main-content"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
