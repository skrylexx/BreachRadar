import { Metadata } from "next";
import { RansomLookClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, RansomwareAlert, ConnectorStatus } from "@/lib/api";

export const metadata: Metadata = {
  title: "RansomLook | BreachRadar",
  description: "Monitor ransomware group activities and victims.",
};

export default async function RansomLookPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await searchParams;
  const page = typeof resolvedParams.page === "string" ? parseInt(resolvedParams.page, 10) : 1;
  const period = typeof resolvedParams.period === "string" ? resolvedParams.period : "7d";
  const search = typeof resolvedParams.search === "string" ? resolvedParams.search : "";
  const limit = 25;
  const offset = (page - 1) * limit;

  const domain = search || process.env.TARGET_DOMAIN || "";

  // Appels parallèles
  const [alertsData, chartData, connectors] = await Promise.all([
    fetchJSON<PaginatedResponse<RansomwareAlert>>(`/api/v1/ransomlook/alerts?limit=${limit}&offset=${offset}&period=${period}${domain ? `&domain=${domain}` : ""}`),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?source=ransomlook&period=${period}`),
    fetchJSON<ConnectorStatus[]>("/api/v1/connectors/status"),
  ]);

  const connector = Array.isArray(connectors) ? connectors.find(c => c.name.toLowerCase() === "ransomlook") : undefined;
  const isMock = connector?.is_mock;
  const isConfigured = connector?.configured;

  return (
    <RansomLookClient
      initialData={alertsData}
      chartData={chartData || []}
      initialPage={page}
      period={period}
      search={search}
      isMock={isMock}
      isConfigured={isConfigured}
    />
  );
}
