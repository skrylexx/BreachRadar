import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { DomainBanner } from "@/components/layout/DomainBanner";
import { MfaRecoveryPrompt } from "@/components/auth/MfaRecoveryPrompt";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const domain =
    process.env.TARGET_DOMAIN ||
    process.env.NEXT_PUBLIC_TARGET_DOMAIN ||
    "";

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar - Fixe sur desktop, overlay sur mobile */}
      <Sidebar />
      
      {/* Contenu principal */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative">
        <Header />
        <DomainBanner domain={domain} />
        <MfaRecoveryPrompt />
        <main className="flex-1 overflow-auto p-4 sm:p-6 pb-20 sm:pb-6">{children}</main>
      </div>
    </div>
  );
}
