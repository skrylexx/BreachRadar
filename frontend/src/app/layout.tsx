import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// ─── Fonts ─────────────────────────────────────────────────────────────────
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
export const metadata: Metadata = {
  title: {
    default: "BreachRadar — SOC Governance Dashboard",
    template: "%s | BreachRadar",
  },
  description:
    "BreachRadar — Defensive OSINT platform for data breach monitoring, ransomware early warning and SOC governance.",
  keywords: ["breach monitoring", "data leak", "OSINT", "SOC", "cybersecurity", "ransomware"],
  robots: {
    index: false, // Outil interne — ne pas indexer
    follow: false,
  },
  icons: {
    icon: "/favicon.ico",
  },
};

// ─── Root Layout ─────────────────────────────────────────────────────────────
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className="dark"
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
