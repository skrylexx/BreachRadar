/**
 * /admin/settings — Paramètres de l'instance BreachRadar (Admin only)
 * Server component.
 */

import { Metadata } from "next";
import { SettingsClient } from "./client";

export const metadata: Metadata = {
  title: "Paramètres — Admin | BreachRadar",
  description: "Configuration globale de l'instance BreachRadar.",
};

export default function AdminSettingsPage() {
  return <SettingsClient />;
}
