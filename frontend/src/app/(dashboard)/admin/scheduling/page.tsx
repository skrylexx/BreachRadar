/**
 * /admin/scheduling — Configuration du scheduler de scans (Admin only)
 * Server component.
 */

import { Metadata } from "next";
import { SchedulingClient } from "./client";

export const metadata: Metadata = {
  title: "Planification — Admin | BreachRadar",
  description: "Configuration du scheduler automatique de scans BreachRadar.",
};

export default function AdminSchedulingPage() {
  return <SchedulingClient />;
}
