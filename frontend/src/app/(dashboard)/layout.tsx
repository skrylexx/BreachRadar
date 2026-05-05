import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { DomainBanner } from "@/components/layout/DomainBanner";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Lecture côté SERVEUR — process.env a toujours accès aux variables
  // du process Node, quelle que soit la position du .env
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