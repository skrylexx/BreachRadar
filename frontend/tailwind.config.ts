import type { Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      // ─── Couleurs BreachRadar ─────────────────────────────────────────────
      colors: {
        // Fond principal — gris-noir profond (Shadcn/UI style)
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",

        // Surfaces (cards, modals)
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        // Accent BreachRadar — Bleu Cyan/Indigo
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },

        // Status colors — code couleur cyber standard
        severity: {
          critical: "#ef4444", // Rouge
          high:     "#f97316", // Orange
          medium:   "#eab308", // Jaune
          low:      "#64748b", // Bleu-gris
          none:     "#22c55e", // Vert
        },

        // Radar accent
        radar: {
          DEFAULT: "#38bdf8",  // Cyan-indigo — identité visuelle
          dim:     "#0284c7",
          glow:    "#7dd3fc",
        },

        border:  "hsl(var(--border))",
        input:   "hsl(var(--input))",
        ring:    "hsl(var(--ring))",
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
      },

      // ─── Typographie ─────────────────────────────────────────────────────
      fontFamily: {
        // UI : Inter
        sans: ["Inter", "Inter Fallback", ...fontFamily.sans],
        // Données techniques : JetBrains Mono
        mono: ["JetBrains Mono", "JetBrains Mono Fallback", ...fontFamily.mono],
      },

      // ─── Border radius (style Shadcn/UI) ─────────────────────────────────
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },

      // ─── Animations ───────────────────────────────────────────────────────
      keyframes: {
        // Animation radar (rotation du sweep)
        "radar-sweep": {
          "0%":   { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
        // Pulsation du point de scan
        "radar-ping": {
          "0%":   { transform: "scale(1)", opacity: "1" },
          "75%, 100%": { transform: "scale(3)", opacity: "0" },
        },
        // Apparition slide-in (sidebar)
        "slide-in-left": {
          "0%":   { transform: "translateX(-100%)", opacity: "0" },
          "100%": { transform: "translateX(0)",     opacity: "1" },
        },
        // Fade in générique
        "fade-in": {
          "0%":   { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        // Glow pulsant pour l'accent radar
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 8px 2px rgba(56, 189, 248, 0.15)" },
          "50%":      { boxShadow: "0 0 20px 6px rgba(56, 189, 248, 0.35)" },
        },
        "accordion-down": {
          from: { height: "0" },
          to:   { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to:   { height: "0" },
        },
      },
      animation: {
        "radar-sweep": "radar-sweep 4s linear infinite",
        "radar-ping":  "radar-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite",
        "slide-in":    "slide-in-left 0.3s ease-out",
        "fade-in":     "fade-in 0.4s ease-out",
        "glow-pulse":  "glow-pulse 3s ease-in-out infinite",
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up":   "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
