"use client";

/**
 * Page de connexion — BreachRadar WebUI
 * Design : dark mode, animation radar en fond, formulaire glassmorphism
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2, Shield } from "lucide-react";
import { useTranslations } from "next-intl";

// ─── Composant ────────────────────────────────────────────────────────────────
export default function LoginPage() {
  const router = useRouter();
  const t = useTranslations("Auth");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ─── Schéma de validation ─────────────────────────────────────────────────────
  const loginSchema = z.object({
    email: z.string().email(t("email_invalid")),
    password: z.string().min(1, t("password_required")),
  });

  type LoginFormData = z.infer<typeof loginSchema>;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: LoginFormData) => {
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(data),
      });

      const json = await res.json();

      if (!res.ok) {
        setError(json.detail || t("error_failed"));
        return;
      }

      // Récupérer le paramètre return_to
      const searchParams = new URLSearchParams(window.location.search);
      const returnTo = searchParams.get("return_to") || "/";

      // MFA requis → rediriger vers la page MFA en passant le return_to
      if (json.requires_mfa) {
        sessionStorage.setItem("mfa_challenge", json.mfa_challenge_token);
        router.push(`/mfa?return_to=${encodeURIComponent(returnTo)}`);
        return;
      }

      // Connexion directe → rediriger vers return_to ou dashboard
      router.push(returnTo);
    } catch {
      setError(t("error_network"));
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden">

      {/* ─── Fond radar animé ─────────────────────────────────────────── */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.04]">
        <RadarBackground />
      </div>

      {/* ─── Card de connexion ────────────────────────────────────────── */}
      <div className="relative z-10 w-full max-w-md px-4 animate-fade-in">
        {/* Logo / Titre */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Shield className="w-8 h-8 text-radar animate-glow-pulse" />
            <span className="text-2xl font-bold tracking-tight">
              Breach<span className="text-radar">Radar</span>
            </span>
          </div>
          <p className="text-muted-foreground text-sm">
            {t("login_subtitle")}
          </p>
        </div>

        {/* Formulaire */}
        <div className="card-soc p-6 space-y-5">
          <h1 className="text-lg font-semibold text-foreground">{t("login_title")}</h1>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email */}
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium text-muted-foreground">
                {t("email_label")}
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="w-full px-3 py-2 bg-secondary border border-border rounded-md
                           text-sm font-data text-foreground placeholder:text-muted-foreground
                           focus:outline-none focus:ring-2 focus:ring-radar/50 focus:border-radar
                           transition-all duration-150"
                placeholder={t("email_placeholder")}
                {...register("email")}
              />
              {errors.email && (
                <p className="text-xs text-red-400">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium text-muted-foreground">
                {t("password_label")}
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  className="w-full px-3 py-2 pr-10 bg-secondary border border-border rounded-md
                             text-sm font-data text-foreground placeholder:text-muted-foreground
                             focus:outline-none focus:ring-2 focus:ring-radar/50 focus:border-radar
                             transition-all duration-150"
                  placeholder={t("password_placeholder")}
                  {...register("password")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground
                             hover:text-foreground transition-colors"
                  aria-label={showPassword ? t("hide_password") : t("show_password")}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-400">{errors.password.message}</p>
              )}
            </div>

            {/* Erreur API */}
            {error && (
              <div className="p-3 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              id="login-submit"
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2
                         bg-radar text-background font-semibold
                         py-2.5 px-4 rounded-md
                         hover:bg-radar-glow active:scale-[0.98]
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-150"
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> {t("btn_authenticating")}</>
              ) : (
                t("btn_signin")
              )}
            </button>
          </form>

          {/* Lien reset password */}
          <div className="text-center">
            <a
              href="/reset-password"
              className="text-xs text-muted-foreground hover:text-radar transition-colors"
            >
              {t("forgot_password")}
            </a>
          </div>
        </div>

        {/* Footer légal */}
        <p className="text-center text-xs text-muted-foreground/50 mt-4">
          {t("footer_legal")}
        </p>
      </div>
    </div>
  );
}

// ─── Fond radar SVG animé ─────────────────────────────────────────────────────
function RadarBackground() {
  return (
    <svg
      width="600"
      height="600"
      viewBox="0 0 600 600"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Cercles concentriques */}
      {[60, 120, 180, 240, 300].map((r) => (
        <circle
          key={r}
          cx="300" cy="300" r={r}
          stroke="#38bdf8"
          strokeWidth="1"
          strokeDasharray="4 8"
        />
      ))}
      {/* Lignes de grille */}
      <line x1="300" y1="0" x2="300" y2="600" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="0" y1="300" x2="600" y2="300" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="87" y1="87" x2="513" y2="513" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="513" y1="87" x2="87" y2="513" stroke="#38bdf8" strokeWidth="0.5" />

      {/* Sweep rotatif */}
      <g
        style={{
          transformOrigin: "300px 300px",
          animation: "radar-sweep 4s linear infinite",
        }}
      >
        <defs>
          <radialGradient id="sweep-grad" cx="0" cy="0" r="1">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0" />
            <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.8" />
          </radialGradient>
        </defs>
        <path
          d="M300 300 L600 300 A300 300 0 0 0 300 0 Z"
          fill="url(#sweep-grad)"
          opacity="0.4"
        />
      </g>

      {/* Point centre */}
      <circle cx="300" cy="300" r="4" fill="#38bdf8" />
    </svg>
  );
}
