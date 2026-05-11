import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";
import "./globals.css";

// ─── Fonts ─────────────────────────────────────────────────────────────────────
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

// ─── SEO Metadata ──────────────────────────────────────────────────────────────
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
    // Logos dans public/images/ — Next.js sert tout le contenu de public/ statiquement
    icon: [
      { url: "/images/logo_only.png", type: "image/png", sizes: "any" },
    ],
    apple: [
      { url: "/images/logo_only.png", sizes: "180x180", type: "image/png" },
    ],
    shortcut: "/images/logo_only.png",
  },
};

// ─── Root Layout ───────────────────────────────────────────────────────────────
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      className="dark"
      suppressHydrationWarning
    >
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        <NextIntlClientProvider messages={messages} locale={locale}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
