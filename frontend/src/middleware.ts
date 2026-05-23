/**
 * middleware.ts — Authentification + RBAC Next.js
 *
 * Protège :
 *   - Toutes les routes du groupe (dashboard) → vérification JWT cookie
 *   - Les routes /admin/* → vérification rôle admin en plus
 *
 * Stratégie :
 *   - Lecture du cookie `access_token` (HttpOnly, posé par le backend)
 *   - Décode le JWT côté Edge (sans clé secrète côté client → vérification signature côté backend)
 *   - Si absent ou expiré → redirect /login
 *   - Si rôle non-admin sur /admin/* → redirect /403
 *
 * NOTE : La vérification de signature complète est effectuée par le backend FastAPI.
 *        Ici on ne fait qu'un decode basique (sans vérification crypto) pour lire
 *        la date d'expiration et le rôle — suffisant pour un UX guard.
 *        La protection réelle est assurée par le backend.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes publiques (pas de JWT requis)
const PUBLIC_PATHS = ["/login", "/mfa", "/403", "/404"];

// Routes admin uniquement
const ADMIN_PATHS = ["/admin"];

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    // Base64url → Base64 → JSON
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(payload);
    return JSON.parse(decoded) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function isTokenExpired(payload: Record<string, unknown>): boolean {
  const exp = payload.exp as number | undefined;
  if (!exp) return true;
  return Date.now() >= exp * 1000;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Laisser passer les assets et l'API
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api/") ||
    pathname.includes(".")  // fichiers statiques (.ico, .png, etc.)
  ) {
    return NextResponse.next();
  }

  // 2. Lire le cookie JWT
  const token = request.cookies.get("access_token")?.value;
  const payload = token ? decodeJwtPayload(token) : null;
  const isAuth = payload && !isTokenExpired(payload);

  // 3. Gestion des routes publiques
  const isPublicPath = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  // Si on est sur /login (ou autre public) mais déjà authentifié → dashboard
  if (isPublicPath && isAuth && pathname === "/login") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  if (isPublicPath) {
    return NextResponse.next();
  }

  // 4. Protection des routes privées
  if (!isAuth) {
    // Pas de token ou expiré → redirect login avec return_to
    const loginUrl = new URL("/login", request.url);
    // Éviter de mettre /login ou /mfa en return_to
    if (!isPublicPath) {
      loginUrl.searchParams.set("return_to", pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  // 5. Guard admin : routes /admin/*
  const isAdminRoute = ADMIN_PATHS.some((p) => pathname.startsWith(p));
  if (isAdminRoute) {
    const role = payload?.role as string | undefined;
    if (role !== "admin") {
      return NextResponse.redirect(new URL("/403", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  // Appliquer le middleware à toutes les routes sauf les exceptions ci-dessus
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
