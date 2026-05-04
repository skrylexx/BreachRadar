"use client";

/**
 * FindingsTable — Tableau des dernières trouvailles
 * Design Stripe-style : aéré, badges de sévérité colorés, JetBrains Mono pour les données.
 */

import { ExternalLink, Shield } from "lucide-react";

type Severity = "critical" | "high" | "medium" | "low" | "none";

interface Finding {
  id: string;
  source: string;
  domain: string;
  severity: Severity;
  type: string;       // "breach" | "ransomware" | "paste" | "github"
  count: number;
  discovered_at: string;
}

// Données de démonstration
const DEMO_FINDINGS: Finding[] = [
  {
    id: "1",
    source: "RansomLook",
    domain: "example.com",
    severity: "critical",
    type: "ransomware",
    count: 1,
    discovered_at: "2026-05-04T09:00:00Z",
  },
  {
    id: "2",
    source: "HIBP",
    domain: "example.com",
    severity: "high",
    type: "breach",
    count: 3,
    discovered_at: "2026-05-03T14:22:00Z",
  },
  {
    id: "3",
    source: "LeakCheck",
    domain: "example.com",
    severity: "medium",
    type: "breach",
    count: 12,
    discovered_at: "2026-05-02T08:45:00Z",
  },
  {
    id: "4",
    source: "GitHub",
    domain: "example.com",
    severity: "low",
    type: "github",
    count: 2,
    discovered_at: "2026-05-01T16:30:00Z",
  },
];

// ─── Badge de sévérité ────────────────────────────────────────────────────────
function SeverityBadge({ severity }: { severity: Severity }) {
  const classes: Record<Severity, string> = {
    critical: "badge-critical",
    high:     "badge-high",
    medium:   "badge-medium",
    low:      "badge-low",
    none:     "badge-none",
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold
                      font-data uppercase tracking-wide ${classes[severity]}`}>
      {severity}
    </span>
  );
}

// ─── Badge source ─────────────────────────────────────────────────────────────
function SourceBadge({ source }: { source: string }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs
                     bg-secondary border border-border/50 text-muted-foreground font-data">
      {source}
    </span>
  );
}

// ─── Composant ────────────────────────────────────────────────────────────────
export function FindingsTable({ findings = DEMO_FINDINGS }: { findings?: Finding[] }) {
  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  };

  return (
    <div className="card-soc">
      {/* En-tête */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-radar" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold text-foreground">Latest Findings</h3>
        </div>
        <span className="text-xs text-muted-foreground">
          {findings.length} result{findings.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Tableau */}
      <div className="overflow-x-auto">
        <table className="w-full" aria-label="Findings table">
          <thead>
            <tr className="border-b border-border/30">
              {["Severity", "Source", "Domain", "Type", "Count", "Discovered"].map((col) => (
                <th
                  key={col}
                  scope="col"
                  className="px-4 py-2.5 text-left text-xs font-medium
                             text-muted-foreground uppercase tracking-wider"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {findings.map((finding, idx) => (
              <tr
                key={finding.id}
                className={`border-b border-border/20 last:border-0
                            hover:bg-accent/30 transition-colors duration-100
                            ${idx % 2 === 0 ? "" : "bg-secondary/20"}`}
              >
                <td className="px-4 py-3">
                  <SeverityBadge severity={finding.severity} />
                </td>
                <td className="px-4 py-3">
                  <SourceBadge source={finding.source} />
                </td>
                <td className="px-4 py-3 font-data text-xs text-foreground">
                  {finding.domain}
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground capitalize">
                  {finding.type}
                </td>
                <td className="px-4 py-3 font-data text-xs text-foreground font-semibold">
                  {finding.count}
                </td>
                <td className="px-4 py-3 font-data text-xs text-muted-foreground whitespace-nowrap">
                  {formatDate(finding.discovered_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
