import { Metadata } from "next";
import { LeakCheckClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, Finding } from "@/lib/api";

export const metadata: Metadata = {
  title: "LeakCheck | BreachRadar",
  description: "Monitor credential leaks and compromised accounts.",
};

export default async function LeakCheckPage({
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
  const [findingsData, chartData] = await Promise.all([
    fetchJSON<PaginatedResponse<Finding>>(`/api/v1/findings?source=leakcheck&limit=${limit}&offset=${offset}&period=${period}`),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?source=leakcheck&period=${period}`),
  ]);

  return (
    <LeakCheckClient
      initialData={findingsData}
      chartData={chartData || []}
      initialPage={page}
      period={period}
    />
  );
}
