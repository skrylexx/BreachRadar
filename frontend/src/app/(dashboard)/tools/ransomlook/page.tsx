import { Metadata } from "next";
import { RansomLookClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, RansomwareAlert } from "@/lib/api";

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
  const limit = 25;
  const offset = (page - 1) * limit;

  // Appels parallèles
  const [alertsData, chartData] = await Promise.all([
    fetchJSON<PaginatedResponse<RansomwareAlert>>(`/api/v1/ransomlook/alerts?limit=${limit}&offset=${offset}&period=${period}`),
    fetchJSON<any[]>(`/api/v1/dashboard/chart?source=ransomlook&period=${period}`),
  ]);

  return (
    <RansomLookClient
      initialData={alertsData}
      chartData={chartData || []}
      initialPage={page}
      period={period}
    />
  );
}
