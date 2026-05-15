import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { DomainBanner } from "@/components/layout/DomainBanner";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  /**
   * Lecture côté SERVEUR (Server Component) — process.env a toujours
   * accès aux variables injectées par Docker / dotenv au démarrage.
   *
   * Priorité :
   *   1. TARGET_DOMAIN              (variable sans préfixe, serveur uniquement)
   *   2. NEXT_PUBLIC_TARGET_DOMAIN  (fallback si définie avec préfixe)
   *
   * La valeur est passée en prop à DomainBanner (Client Component)
   * — on évite ainsi tout appel à process.env côté client.
   */
  const domain =
    process.env.TARGET_DOMAIN ||
    process.env.NEXT_PUBLIC_TARGET_DOMAIN ||
    "";

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <DomainBanner domain={domain} />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
