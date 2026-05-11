import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Geist } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});


// ─── Fonts ────────────────────────────────────────────────────────────────────────
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
  weight: ["400", "500", "600"],
});

// ─── SEO Metadata ────────────────────────────────────────────────────────────
const domain =
  process.env.TARGET_DOMAIN ||
  process.env.NEXT_PUBLIC_TARGET_DOMAIN ||
  "BreachRadar";

export const metadata: Metadata = {
  title: {
    default: `BreachRadar — ${domain}`,
    template: "%s | BreachRadar",
  },
  description:
    "BreachRadar — Defensive OSINT platform for data breach monitoring, ransomware early warning and SOC governance.",
  keywords: ["breach monitoring", "data leak", "OSINT", "SOC", "cybersecurity", "ransomware"],
  robots: {
    index: false,
    follow: false,
  },
  icons: {
    // ── Favicon ────────────────────────────────────────────────────────────
    // Le fichier doit être présent dans frontend/public/logo_only.png
    // (copié depuis images/logo_only.png à la racine du repo).
    // Next.js ne sert que les fichiers du dossier public/ de son propre contexte.
    icon: [
      { url: "/logo_only.png", type: "image/png", sizes: "any" },
    ],
    apple: [
      { url: "/logo_only.png", sizes: "180x180", type: "image/png" },
    ],
    shortcut: "/logo_only.png",
  },
};

// ─── Root Layout ────────────────────────────────────────────────────────────
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={cn("dark", "font-sans", geist.variable)}
      suppressHydrationWarning
    >
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
