"use client";

import { useEffect, useState } from "react";
import { ScrollText, ChevronRight, Clock, ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { apiFetch } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";
import Link from "next/link";

interface CyberFinding {
  id: string;
  source: string;
  title: string;
  severity: string;
  discovered_at: string;
  url?: string;
}

export function IntelligenceWidget() {
  const [findings, setFindings] = useState<CyberFinding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const data = await apiFetch<{ items: CyberFinding[] }>("/api/v1/intelligence?page_size=5");
        setFindings(data.items);
      } catch (error) {
        console.error("Error fetching dashboard intelligence:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLatest();
  }, []);

  return (
    <Card className="flex flex-col h-full border-border/20 bg-card/30 overflow-hidden">
      <div className="p-4 border-b border-border/10 flex items-center justify-between bg-radar/5">
        <div className="flex items-center gap-2">
          <ScrollText className="w-4 h-4 text-radar" />
          <h2 className="text-xs font-bold uppercase tracking-widest text-foreground">
            Dernières Veilles
          </h2>
        </div>
        <Link href="/intelligence">
          <Button variant="ghost" size="sm" className="h-7 text-[10px] text-muted-foreground hover:text-radar gap-1">
            Voir tout <ChevronRight className="w-3 h-3" />
          </Button>
        </Link>
      </div>

      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="p-4 space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="w-8 h-8 rounded" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-3 w-1/2" />
                  <Skeleton className="h-2 w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : findings.length > 0 ? (
          <div className="divide-y divide-border/10">
            {findings.map((f) => (
              <div key={f.id} className="p-4 hover:bg-secondary/20 transition-colors group">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-muted-foreground/60 uppercase truncate max-w-[80px]">
                        {f.source}
                      </span>
                      <div className="flex items-center gap-1 text-[9px] text-muted-foreground">
                        <Clock className="w-2.5 h-2.5" />
                        {formatDistanceToNow(new Date(f.discovered_at), { locale: fr })}
                      </div>
                    </div>
                    <h3 className="text-xs font-medium text-foreground line-clamp-1 group-hover:text-radar transition-colors">
                      {f.title}
                    </h3>
                  </div>
                  <SeverityBadge level={f.severity as any} className="scale-75 origin-right" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center space-y-2">
            <ScrollText className="w-8 h-8 text-muted-foreground/20" />
            <p className="text-[10px] text-muted-foreground">Aucune donnée de veille récente.</p>
          </div>
        )}
      </div>
    </Card>
  );
}
