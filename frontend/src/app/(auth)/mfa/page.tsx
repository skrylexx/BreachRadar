"use client";

/**
 * MFA verification page — BreachRadar WebUI
 * Design: Same as login page (radar, glassmorphism)
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Shield, ArrowLeft } from "lucide-react";
import { authApi } from "@/lib/api";
import { useTranslations } from "next-intl";

// ─── Component ────────────────────────────────────────────────────────────────
export default function MFAPage() {
  const router = useRouter();
  const t = useTranslations("MFA");
  const [error, setError] = useState<string | null>(null);
  const [challengeToken, setChallengeToken] = useState<string | null>(null);
  const [isRecovery, setIsRecovery] = useState(false);

  // Check for challenge token presence on mount
  useEffect(() => {
    const token = sessionStorage.getItem("mfa_challenge");
    if (!token) {
      router.push("/login");
      return;
    }
    setChallengeToken(token);
  }, [router]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<any>({ 
    resolver: zodResolver(
      z.object({
        totp_code: isRecovery 
          ? z.string().length(12, t("error_recovery_length"))
          : z.string().length(6, t("error_length")).regex(/^\d+$/, t("error_digits")),
      })
    ) 
  });

  const onSubmit = async (data: any) => {
    if (!challengeToken) return;
    setError(null);

    try {
      await authApi.mfaVerify(challengeToken, data.totp_code);
      
      // Success: Clear challenge and redirect
      sessionStorage.removeItem("mfa_challenge");
      
      // Get the return_to parameter
      const searchParams = new URLSearchParams(window.location.search);
      const returnTo = searchParams.get("return_to") || "/";
      
      router.push(returnTo);
    } catch (err: any) {
      setError(err.message || t("error_invalid"));
    }
  };

  const toggleMode = () => {
    setIsRecovery(!isRecovery);
    setError(null);
    reset();
  };

  // Show nothing if redirection is in progress
  if (!challengeToken) return null;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden">
      
      {/* ─── Animated radar background ─────────────────────────────────────────── */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.04]">
        <RadarBackground />
      </div>

      {/* ─── MFA Card ─────────────────────────────────────────────────── */}
      <div className="relative z-10 w-full max-w-md px-4 animate-fade-in">
        {/* Logo / Title */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Shield className="w-8 h-8 text-radar animate-glow-pulse" />
            <span className="text-2xl font-bold tracking-tight">
              Breach<span className="text-radar">Radar</span>
            </span>
          </div>
          <p className="text-muted-foreground text-sm font-medium tracking-wide">
            {t("title_required")}
          </p>
        </div>

        {/* Form */}
        <div className="card-soc p-6 space-y-6">
          <div className="space-y-1">
            <h1 className="text-lg font-semibold text-foreground">
              {isRecovery ? t("recovery_title") : t("card_title")}
            </h1>
            <p className="text-sm text-muted-foreground">
              {isRecovery 
                ? t("recovery_desc")
                : t("card_desc")}
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* TOTP / Recovery code */}
            <div className="space-y-2">
              <label htmlFor="totp_code" className="text-xs font-bold uppercase tracking-widest text-muted-foreground/70">
                {isRecovery ? t("input_label_recovery") : t("input_label")}
              </label>
              <input
                id="totp_code"
                type="text"
                inputMode={isRecovery ? "text" : "numeric"}
                autoComplete="one-time-code"
                autoFocus
                key={isRecovery ? "recovery" : "totp"}
                className={`w-full px-3 py-4 bg-secondary/50 border border-border rounded-md
                           text-center font-mono text-foreground 
                           placeholder:text-muted-foreground/20
                           focus:outline-none focus:ring-2 focus:ring-radar/50 focus:border-radar
                           transition-all duration-150 ${isRecovery ? "text-xl tracking-wider" : "text-3xl tracking-[0.5em]"}`}
                placeholder={isRecovery ? t("input_placeholder_recovery") : t("input_placeholder")}
                maxLength={isRecovery ? 12 : 6}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleSubmit(onSubmit)();
                  }
                }}
                {...register("totp_code")}
              />
              {errors.totp_code && (
                <p className="text-xs text-red-400 font-medium">{errors.totp_code.message as string}</p>
              )}
            </div>

            {/* API Error */}
            {error && (
              <div className="p-3 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm animate-shake">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2
                         bg-radar text-background font-bold uppercase tracking-wider
                         py-3 px-4 rounded-md
                         hover:bg-radar-glow active:scale-[0.98]
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-150 shadow-lg shadow-radar/20"
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> {t("btn_verifying")}</>
              ) : (
                isRecovery ? t("btn_recover") : t("btn_verify")
              )}
            </button>
          </form>

          {/* Recovery mode / Back link */}
          <div className="flex flex-col gap-3 text-center">
            <button
              onClick={toggleMode}
              className="text-xs text-radar/80 hover:text-radar transition-colors font-medium"
            >
              {isRecovery ? t("link_use_app") : t("link_use_recovery")}
            </button>

            <button
              onClick={() => router.push("/login")}
              className="text-xs text-muted-foreground hover:text-radar transition-colors 
                         flex items-center justify-center gap-1.5 mx-auto font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> 
              {t("link_back_login")}
            </button>
          </div>
        </div>

        {/* Legal footer */}
        <p className="text-center text-xs text-muted-foreground/40 mt-6 tracking-tight">
          {t("footer_legal")}
        </p>
      </div>
    </div>
  );
}

// ─── Animated SVG radar background (same as login) ────────────────────────────────
function RadarBackground() {
  return (
    <svg
      width="600"
      height="600"
      viewBox="0 0 600 600"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Concentric circles */}
      {[60, 120, 180, 240, 300].map((r) => (
        <circle
          key={r}
          cx="300" cy="300" r={r}
          stroke="#38bdf8"
          strokeWidth="1"
          strokeDasharray="4 8"
        />
      ))}
      {/* Grid lines */}
      <line x1="300" y1="0" x2="300" y2="600" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="0" y1="300" x2="600" y2="300" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="87" y1="87" x2="513" y2="513" stroke="#38bdf8" strokeWidth="0.5" />
      <line x1="513" y1="87" x2="87" y2="513" stroke="#38bdf8" strokeWidth="0.5" />

      {/* Rotating sweep */}
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

      {/* Center point */}
      <circle cx="300" cy="300" r="4" fill="#38bdf8" />
    </svg>
  );
}
