/**
 * TimeFilter — Sélecteur de plage temporelle standard
 * Utilisé sur toutes les pages outil et le dashboard.
 *
 * Options : 7j | 1 mois | 6 mois | 12 mois | Tout
 */

"use client";

import { cn } from "@/lib/utils";

export type TimePeriod = "7d" | "30d" | "6m" | "12m" | "all";

interface TimeFilterOption {
  value: TimePeriod;
  label: string;
}

const TIME_OPTIONS: TimeFilterOption[] = [
  { value: "7d",  label: "7j" },
  { value: "30d", label: "1 mois" },
  { value: "6m",  label: "6 mois" },
  { value: "12m", label: "12 mois" },
  { value: "all", label: "Tout" },
];

interface TimeFilterProps {
  value: TimePeriod;
  onChange: (value: TimePeriod) => void;
  className?: string;
}

export function TimeFilter({ value, onChange, className }: TimeFilterProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-1 p-0.5 bg-card rounded-lg border border-border/50",
        className
      )}
      role="group"
      aria-label="Filtre temporel"
    >
      {TIME_OPTIONS.map((option) => (
        <button
          key={option.value}
          id={`time-filter-${option.value}`}
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
          className={cn(
            "px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150",
            value === option.value
              ? "bg-radar/15 text-radar border border-radar/30"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
