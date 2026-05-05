import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone pour Docker (optimise le bundle)
  output: "standalone",

  // ─── Variables d'environnement ─────────────────────────────────────────────
  // Force Next.js à exposer ces variables au bundle client, même si le .env
  // est lu depuis la racine du repo plutôt que depuis frontend/.
  // Cela résout le problème de NEXT_PUBLIC_TARGET_DOMAIN non trouvé quand
  // Next.js est lancé depuis D:\BreachRadar\frontend avec le .env parent.
  env: {
    NEXT_PUBLIC_TARGET_DOMAIN: process.env.NEXT_PUBLIC_TARGET_DOMAIN ?? "",
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
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
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

export default nextConfig;
