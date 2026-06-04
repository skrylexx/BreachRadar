import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const backendUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  // Standalone output for Docker (optimizes the bundle)
  output: "standalone",

  // ─── Environment variables ────────────────────── ───────────────────────
  // Next.js ONLY reads the .env from the start directory (frontend/).
  // TARGET_DOMAIN is defined in the repo root .env and passed to the build
  // via docker-compose build args → Dockerfile ARG → ENV → here.
  env: {
    // Variable without prefix — accessible ONLY on the server side
    TARGET_DOMAIN: process.env.TARGET_DOMAIN ?? "",
    // We force the client to use relative paths to pass through the Next.js proxy (avoids CORS)
    NEXT_PUBLIC_API_URL: "",
  },

  // API Proxy: all /api/* requests are redirected to FastAPI
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob:",
              `connect-src 'self' ${backendUrl} http://localhost:8000 http://127.0.0.1:8000`,
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
