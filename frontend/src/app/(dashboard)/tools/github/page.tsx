import { Metadata } from "next";
import { GitHubClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, Finding, ConnectorStatus } from "@/lib/api";

export const metadata: Metadata = {
  title: "GitHub & GitLab | BreachRadar",
  description: "Monitor exposed secrets and credentials in public repositories.",
};

export default async function GitHubPage({
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
    fetchJSON<PaginatedResponse<Finding>>(`/api/v1/findings?source=github&limit=${limit}&offset=${offset}&period=${period}`),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?source=github&period=${period}`),
    fetchJSON<ConnectorStatus[]>("/api/v1/connectors/status"),
  ]);

  const isMock = Array.isArray(connectors) && connectors.find(c => c.name.toLowerCase() === "github")?.is_mock;

  return (
    <GitHubClient
      initialData={findingsData}
      chartData={chartData || []}
      initialPage={page}
      period={period}
      isMock={isMock}
    />
  );
}
