/**
 * lib/fetch.ts — Utilitaire fetch pour les Server Components Next.js
 *
 * `fetchJSON` est utilisé dans les pages serveur pour appeler le backend
 * via les rewrites Next.js (/api/* → FastAPI).
 *
 * Différence avec apiFetch (api.ts) :
 *   - apiFetch : client-side, gère les cookies HttpOnly, les redirections 401/403
 *   - fetchJSON : server-side, pas de window, retourne null en cas d'erreur
 *     plutôt que de throw (pour ne pas bloquer le rendu SSR)
 */

import { headers } from "next/headers";

const API_BASE = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://breachradar-api:8000";

/**
 * Fetch JSON côté serveur (Server Components).
 * Préfixe automatiquement les chemins relatifs avec API_BASE.
 *
 * @param path  - Chemin absolu ou URL complète, ex: "/api/v1/ransomlook/alerts?limit=25"
 * @param init  - Options fetch standard (method, headers, cache, next, ...)
 * @returns     - La réponse désérialisée, ou null en cas d'erreur réseau / HTTP
 */
export async function fetchJSON<T = unknown>(
  path: string,
  init?: RequestInit
): Promise<T | null> {
  const headersList = await headers();
  const cookie = headersList.get("cookie");

  // Construire l'URL complète si le chemin est relatif
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;

  try {
    const res = await fetch(url, {
      // Pas de cache par défaut en SSR pour des données temps réel
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(cookie ? { cookie } : {}),
        ...init?.headers,
      },
    });

    if (!res.ok) {
      console.error(`[fetchJSON] HTTP ${res.status} — ${url}`);
      return null;
    }

    if (res.status === 204) {
      return null;
    }

    return (await res.json()) as T;
  } catch (err) {
    console.error(`[fetchJSON] Network error — ${url}`, err);
    return null;
  }
}
