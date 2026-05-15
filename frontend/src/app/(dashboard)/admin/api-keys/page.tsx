/**
 * /admin/api-keys — Gestion des clés API connecteurs (Admin only)
 * Server component.
 */

import { Metadata } from "next";
import { ApiKeysClient } from "./client";

export const metadata: Metadata = {
  title: "Clés API — Admin | BreachRadar",
  description: "Gestion des clés API pour les connecteurs OSINT.",
};

export default function AdminApiKeysPage() {
  return <ApiKeysClient />;
}
