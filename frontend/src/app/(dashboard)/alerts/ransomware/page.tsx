import { Metadata } from "next";
import { RansomwareAlertsClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, RansomwareAlert } from "@/lib/api";

export const metadata: Metadata = {
  title: "Ransomware Alerts | BreachRadar",
  description: "Monitor detailed ransomware group activities and victims.",
};

export default async function RansomwareAlertsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await searchParams;
  const page = typeof resolvedParams.page === "string" ? parseInt(resolvedParams.page, 10) : 1;
  const period = typeof resolvedParams.period === "string" ? resolvedParams.period : "30d";
  
  // Extract filters
  const group = typeof resolvedParams.group === "string" ? resolvedParams.group : undefined;
  const status = typeof resolvedParams.status === "string" ? resolvedParams.status : undefined;
  
  const limit = 25;
  const offset = (page - 1) * limit;

  // Build query string for alerts
  const qs = new URLSearchParams();
  qs.set("limit", limit.toString());
  qs.set("offset", offset.toString());
  qs.set("period", period);
  if (group) qs.set("group", group);
  if (status) qs.set("status", status);

  // Appels parallèles
  const [alertsData, statusData] = await Promise.all([
    fetchJSON<PaginatedResponse<RansomwareAlert>>(`/api/v1/ransomlook/alerts?${qs.toString()}`),
    fetchJSON<Record<string, any>>("/api/v1/ransomlook/status"),
  ]);

  return (
    <RansomwareAlertsClient
      initialData={alertsData}
      statusData={statusData || {}}
      initialPage={page}
      period={period}
      currentFilters={{ group, status }}
    />
  );
}
