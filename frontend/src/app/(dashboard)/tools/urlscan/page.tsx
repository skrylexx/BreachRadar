import { Metadata } from "next";
import { URLScanClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, Finding, ConnectorStatus } from "@/lib/api";

export const metadata: Metadata = {
  title: "URLScan | BreachRadar",
  description: "Monitor scanned URLs and domain reputations.",
};

export default async function URLScanPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await searchParams;
  const page = typeof resolvedParams.page === "string" ? parseInt(resolvedParams.page, 10) : 1;
  const period = typeof resolvedParams.period === "string" ? resolvedParams.period : "7d";
  const limit = 25;
  const offset = (page - 1) * limit;

  // Appels parallèles
  const [findingsData, chartData, connectors] = await Promise.all([
    fetchJSON<PaginatedResponse<Finding>>(`/api/v1/findings?source=urlscan&limit=${limit}&offset=${offset}&period=${period}`),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?source=urlscan&period=${period}`),
    fetchJSON<ConnectorStatus[]>("/api/v1/connectors/status"),
  ]);

  const isMock = Array.isArray(connectors) && connectors.find(c => c.name.toLowerCase() === "urlscan")?.is_mock;

  return (
    <URLScanClient
      initialData={findingsData}
      chartData={chartData || []}
      initialPage={page}
      period={period}
      isMock={isMock}
    />
  );
}
