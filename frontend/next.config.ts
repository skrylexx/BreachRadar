import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone pour Docker (optimise le bundle)
  output: "standalone",

  // ─── Variables d'environnement ─────────────────────────────────────────────
  // Next.js lit UNIQUEMENT le .env du répertoire de démarrage (frontend/).
  // Pour que TARGET_DOMAIN (défini dans le .env racine du repo) soit accessible
  // au Server Component layout.tsx, on le propage ici explicitement depuis
  // le process.env du process Node (Docker les injecte, dotenv-cli les précharge).
  env: {
    // Variable sans préfixe — accessible UNIQUEMENT côté serveur
    TARGET_DOMAIN: process.env.TARGET_DOMAIN ?? "",
    // Variable NEXT_PUBLIC — accessible client ET serveur (build-time)
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
