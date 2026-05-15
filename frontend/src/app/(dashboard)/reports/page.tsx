import { Metadata } from "next";
import { ReportsClient } from "./client";
import { fetchJSON } from "@/lib/fetch";
import { PaginatedResponse, Report } from "@/lib/api";

export const metadata: Metadata = {
  title: "Reports | BreachRadar",
  description: "View and generate security audit reports.",
};

export default async function ReportsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await searchParams;
  const page = typeof resolvedParams.page === "string" ? parseInt(resolvedParams.page, 10) : 1;
  const period = typeof resolvedParams.period === "string" ? resolvedParams.period : "30d";
  const limit = 25;
  const offset = (page - 1) * limit;

  // Fetch reports data
  const reportsData = await fetchJSON<PaginatedResponse<Report>>(
    `/api/v1/reports?limit=${limit}&offset=${offset}&period=${period}`
  );

  return (
    <ReportsClient
      initialData={reportsData}
      initialPage={page}
      period={period}
    />
  );
}
