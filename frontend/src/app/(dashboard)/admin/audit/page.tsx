/**
 * /admin/audit — Audit trail (Admin only)
 * Server component.
 */

import { Metadata } from "next";
import { AuditClient } from "./client";

export const metadata: Metadata = {
  title: "Audit Trail — Admin | BreachRadar",
  description: "Journal d'audit des actions utilisateurs sur l'instance BreachRadar.",
};

export default function AdminAuditPage() {
  return <AuditClient />;
}
