import { Metadata } from "next";
import { ScansClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, Scan } from "@/lib/api";
import { PageHeader } from "@/components/ui/page-header";
import { Activity } from "lucide-react";

export const metadata: Metadata = {
  title: "Scans History | BreachRadar",
  description: "View past scans and trigger new ones",
};

export default async function ScansPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await searchParams;
  const page = typeof resolvedParams.page === "string" ? parseInt(resolvedParams.page, 10) : 1;
  const limit = 25;
  const offset = (page - 1) * limit;

  // Fetch initial data for SSR
  const initialData = await fetchJSON<PaginatedResponse<Scan>>(`/api/v1/scans?limit=${limit}&offset=${offset}`);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scans History"
        description="View past scans and trigger new ones."
        icon={Activity}
        breadcrumb={[
          { label: "Dashboard", href: "/" },
          { label: "Scans", active: true },
        ]}
      />

      <ScansClient initialData={initialData} initialPage={page} />
    </div>
  );
}
