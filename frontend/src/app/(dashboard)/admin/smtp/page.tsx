/**
 * /admin/smtp — Configuration SMTP (Admin only)
 * Server component.
 */

import { Metadata } from "next";
import { SmtpClient } from "./client";

export const metadata: Metadata = {
  title: "Configuration SMTP — Admin | BreachRadar",
  description: "Paramètres SMTP pour les notifications email BreachRadar.",
};

export default function AdminSmtpPage() {
  return <SmtpClient />;
}
