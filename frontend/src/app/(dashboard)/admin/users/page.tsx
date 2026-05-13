/**
 * /admin/users — Gestion des utilisateurs (Admin only)
 * Server component : récupère la liste côté serveur et hydrate le client.
 */

import { Metadata } from "next";
import { UsersClient } from "./client";

export const metadata: Metadata = {
  title: "Utilisateurs — Admin | BreachRadar",
  description: "Gestion des utilisateurs de l'instance BreachRadar.",
};

export default function AdminUsersPage() {
  return <UsersClient />;
}
