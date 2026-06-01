import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Output standalone pour Docker (optimise le bundle)
  output: "standalone",

  // ─── Variables d'environnement ─────────────────────────────────────────────
  // Next.js lit UNIQUEMENT le .env du répertoire de démarrage (frontend/).
  // TARGET_DOMAIN est défini dans le .env racine du repo et transmis au build
  // via docker-compose build args → Dockerfile ARG → ENV → ici.
  env: {
    // Variable sans préfixe — accessible UNIQUEMENT côté serveur
    TARGET_DOMAIN: process.env.TARGET_DOMAIN ?? "",
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },

  // Proxy API : toutes les requêtes /api/* sont redirigées vers FastAPI
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        }/:path*`,
      },
    ];
  },

  // Headers de sécurité
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self'",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob:",
              "connect-src 'self' http://localhost:8000",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
