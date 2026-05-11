"use client";

import { AlertTriangle, ChevronRight, ShieldAlert } from "lucide-react";
import Link from "next/link";
import type { RansomwareAlert } from "@/lib/api";

export function RansomwareAlertBlock({ alerts = [] }: { alerts?: RansomwareAlert[] }) {
  if (!alerts || alerts.length === 0) return null;

  const alert = alerts[0]; // Display the most recent

  return (
    <div className="card-soc border-red-500/30 bg-red-500/5 relative overflow-hidden group">
      {/* Halo effect */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 rounded-full bg-red-500/10 blur-3xl" />
      
      <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-md bg-red-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5 text-red-500" strokeWidth={1.5} />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-sm font-bold text-red-400 uppercase tracking-wide">
                Ransomware Alert: {alert.group}
              </h3>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 font-data">
                CRITICAL
              </span>
            </div>
            <p className="text-xs text-foreground font-medium mb-1">
              Victim: <span className="font-data text-muted-foreground">{alert.victim}</span>
            </p>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] text-muted-foreground font-data">
              {alert.sector && <span>Sector: {alert.sector}</span>}
              {alert.country && <span>Country: {alert.country}</span>}
              {alert.claim_size && <span>Size: {alert.claim_size}</span>}
              <span>Status: {alert.status}</span>
            </div>
          </div>
        </div>

        <Link
          href="/alerts/ransomware"
          className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-md
                     bg-red-500/10 text-red-400 text-xs font-semibold border border-red-500/20
                     hover:bg-red-500/20 transition-colors whitespace-nowrap self-start md:self-auto"
        >
          View Details
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
