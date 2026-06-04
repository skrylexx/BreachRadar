/**
 * lib/fetch.ts — fetch utility for Next.js Server Components
 *
 * `fetchJSON` is used in server pages to call the backend
 * via Next.js rewrites (/api/* → FastAPI).
 *
 * Difference with apiFetch (api.ts):
 *   - apiFetch: client-side, manages HttpOnly cookies, 401/403 redirects
 *   - fetchJSON: server-side, no window, returns null on error
 *     rather than throwing (to avoid blocking SSR rendering)
 */

import { headers } from "next/headers";

const API_BASE = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://breachradar-api:8000";

/**
 * Server-side JSON fetch (Server Components).
 * Automatically prefixes relative paths with API_BASE.
 *
 * @param path  - Absolute path or full URL, e.g.: "/api/v1/ransomlook/alerts?limit=25"
 * @param init  - Standard fetch options (method, headers, cache, next, ...)
 * @returns     - The deserialized response, or null in case of network / HTTP error
 */
export async function fetchJSON<T = unknown>(
  path: string,
  init?: RequestInit
): Promise<T | null> {
  const headersList = await headers();
  const cookie = headersList.get("cookie");

  // Construct full URL if path is relative
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;

  try {
    const res = await fetch(url, {
      // No cache by default in SSR for real-time data
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
