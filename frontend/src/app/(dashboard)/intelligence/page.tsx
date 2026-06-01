"use client";

import { useEffect, useState, useCallback } from "react";
import { 
  ScrollText, 
  Search, 
  Filter, 
  ExternalLink, 
  Clock, 
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  Bell
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { apiFetch } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";
import { fr, enGB } from "date-fns/locale";
import { useTranslations, useLocale } from "next-intl";

interface CyberFinding {
  id: string;
  source: string;
  finding_type: string;
  title: string;
  description?: string;
  url?: string;
  severity: string;
  extra_metadata?: any;
  is_read: boolean;
  discovered_at: string;
  published_at?: string;
}

export default function IntelligenceFeedPage() {
  const t = useTranslations("Intelligence");
  const tc = useTranslations("Common");
  const locale = useLocale();
  const [findings, setFindings] = useState<CyberFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [readFilter, setReadFilter] = useState<string>("unread");

  const fetchFindings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch<{ items: CyberFinding[] }>("/api/v1/intelligence?page_size=50");
      setFindings(data.items);
    } catch (error) {
      console.error("Error fetching intelligence:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFindings();
  }, [fetchFindings]);

  const markAsRead = async (id: string) => {
    try {
      await apiFetch(`/api/v1/intelligence/${id}/read`, { method: "POST" });
      setFindings(prev => prev.map(f => f.id === id ? { ...f, is_read: true } : f));
    } catch (error) {
      console.error("Error marking as read:", error);
    }
  };

  const filteredFindings = findings.filter(f => {
    const matchesSearch = f.title.toLowerCase().includes(search.toLowerCase()) || 
                         f.source.toLowerCase().includes(search.toLowerCase());
    
    const matchesSeverity = severityFilter === "all" || f.severity === severityFilter;
    
    let matchesRead = true;
    if (readFilter === "unread") matchesRead = !f.is_read;
    if (readFilter === "read") matchesRead = f.is_read;

    return matchesSearch && matchesSeverity && matchesRead;
  });

  return (
    <div className="space-y-6">
      <PageHeader 
        title={t("title")} 
        description={t("description")}
        icon={ScrollText}
      />

      {/* Barre d'outils / Filtres */}
      <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
        <div className="relative w-full lg:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder={t("search_placeholder")} 
            className="pl-10 bg-secondary/30 border-border/50"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
          {/* Filtre Statut de lecture */}
          <select 
            value={readFilter}
            onChange={(e) => setReadFilter(e.target.value)}
            className="bg-secondary/30 border border-border/50 rounded-md px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-radar"
          >
            <option value="all">{t("filter_all")}</option>
            <option value="unread">{t("filter_unread")}</option>
            <option value="read">{t("filter_read")}</option>
          </select>

          {/* Filtre Sévérité */}
          <select 
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-secondary/30 border border-border/50 rounded-md px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-radar"
          >
            <option value="all">{t("filter_severity_all")}</option>
            <option value="CRITICAL">{tc("severity")} - Critique</option>
            <option value="HIGH">{tc("severity")} - Élevée</option>
            <option value="MEDIUM">{tc("severity")} - Moyenne</option>
            <option value="LOW">{tc("severity")} - Faible</option>
          </select>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchFindings}
            disabled={loading}
            className="bg-secondary/30 border-border/50 ml-auto lg:ml-0"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            {t("btn_refresh")}
          </Button>
        </div>
      </div>

      {/* Liste des findings */}
      <div className="grid gap-4">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="p-4 border-border/20 bg-card/30">
              <div className="flex gap-4">
                <Skeleton className="w-12 h-12 rounded-md" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-3 w-full" />
                </div>
              </div>
            </Card>
          ))
        ) : filteredFindings.length > 0 ? (
          filteredFindings.map((finding) => (
            <Card 
              key={finding.id} 
              className={`p-5 border-border/20 bg-card/30 hover:border-radar/30 transition-all duration-200
                         ${finding.is_read ? "opacity-60" : "border-l-4 border-l-radar"}`}
            >
              <div className="flex flex-col sm:flex-row gap-4">
                {/* Icône & Source */}
                <div className="flex flex-row sm:flex-col items-center sm:items-start gap-3 sm:w-32 flex-shrink-0">
                  <div className="w-10 h-10 rounded-lg bg-radar/10 flex items-center justify-center border border-radar/20">
                    {finding.finding_type === "rss" ? <ScrollText className="w-5 h-5 text-radar" /> : 
                     finding.finding_type === "github" ? <Search className="w-5 h-5 text-radar" /> :
                     <Bell className="w-5 h-5 text-radar" />}
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 leading-none mb-1">
                      {finding.source}
                    </p>
                    <SeverityBadge level={finding.severity as any} />
                  </div>
                </div>

                {/* Contenu principal */}
                <div className="flex-1 min-w-0 space-y-2">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="text-sm font-semibold text-foreground line-clamp-1">
                      {finding.title}
                    </h3>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {!finding.is_read && (
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-8 w-8 text-muted-foreground hover:text-radar"
                          onClick={() => markAsRead(finding.id)}
                          title={t("mark_read")}
                        >
                          <CheckCircle2 className="w-4 h-4" />
                        </Button>
                      )}
                      {finding.url && (
                        <a 
                          href={finding.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="p-2 rounded-md hover:bg-radar/10 text-muted-foreground hover:text-radar transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                    {finding.description}
                  </p>

                  <div className="flex items-center gap-4 pt-1">
                    <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-medium">
                      <Clock className="w-3 h-3" />
                      {finding.published_at 
                        ? formatDistanceToNow(new Date(finding.published_at), { addSuffix: true, locale: locale === 'fr' ? fr : enGB })
                        : formatDistanceToNow(new Date(finding.discovered_at), { addSuffix: true, locale: locale === 'fr' ? fr : enGB })}
                    </div>
                    {finding.extra_metadata?.category && (
                      <div className="px-1.5 py-0.5 rounded bg-secondary/50 text-[10px] text-muted-foreground border border-border/50">
                        {finding.extra_metadata.category}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="py-20 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-secondary/30 flex items-center justify-center mx-auto border border-border/50">
              <Search className="w-8 h-8 text-muted-foreground/40" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">{t("empty_title")}</p>
              <p className="text-xs text-muted-foreground">{t("empty_desc")}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
