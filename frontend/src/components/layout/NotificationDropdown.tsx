"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell, CheckCircle2, Clock, ExternalLink, Inbox } from "lucide-react";
import { intelligenceApi } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function NotificationDropdown() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await intelligenceApi.list({ page_size: 5, is_read: false });
      setNotifications(res.items);
      setUnreadCount(res.total);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    // Poll every 60 seconds
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await intelligenceApi.markAsRead(id);
      setNotifications(prev => prev.filter(n => n.id !== id));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await intelligenceApi.markAllAsRead();
      setNotifications([]);
      setUnreadCount(0);
      setIsOpen(false);
    } catch (error) {
      console.error("Failed to mark all as read:", error);
    }
  };

  return (
    <div className="relative">
      <button
        id="header-notifications"
        className="sidebar-icon relative"
        title="Notifications"
        aria-label="Notifications"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Bell className="w-4 h-4" strokeWidth={1.5} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-[10px] text-white flex items-center justify-center rounded-full font-bold animate-pulse">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          {/* Overlay pour fermer */}
          <div 
            className="fixed inset-0 z-[60]" 
            onClick={() => setIsOpen(false)}
          />
          
          <div className="absolute right-0 top-full mt-2 w-80 bg-popover border border-border rounded-lg shadow-2xl z-[70] animate-in fade-in slide-in-from-top-2">
            <div className="flex items-center justify-between p-4 border-b border-border/50">
              <h3 className="text-sm font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <button 
                  onClick={markAllAsRead}
                  className="text-[10px] text-radar hover:text-radar-glow font-bold uppercase tracking-wider"
                >
                  Tout marquer comme lu
                </button>
              )}
            </div>

            <div className="max-h-[400px] overflow-y-auto">
              {loading && notifications.length === 0 ? (
                <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
                  Chargement...
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-12 text-center space-y-3 opacity-40">
                  <Inbox className="w-8 h-8 mx-auto stroke-1" />
                  <p className="text-xs">Aucune nouvelle notification</p>
                </div>
              ) : (
                <div className="divide-y divide-border/30">
                  {notifications.map((n) => (
                    <div 
                      key={n.id} 
                      className="p-4 hover:bg-accent/30 transition-colors group relative"
                    >
                      <div className="flex gap-3">
                        <div className="flex-1 space-y-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase truncate">
                              {n.source}
                            </span>
                            <SeverityBadge level={n.severity} className="scale-75 origin-right" />
                          </div>
                          <p className="text-xs font-medium text-foreground line-clamp-2 leading-relaxed">
                            {n.title}
                          </p>
                          <div className="flex items-center gap-2 pt-1">
                            <Clock className="w-3 h-3 text-muted-foreground/50" />
                            <span className="text-[10px] text-muted-foreground/50">
                              {formatDistanceToNow(new Date(n.published_at || n.discovered_at), { addSuffix: true, locale: fr })}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={(e) => markAsRead(n.id, e)}
                          className="h-6 w-6 rounded-full flex items-center justify-center bg-background border border-border text-muted-foreground hover:text-radar hover:border-radar transition-all opacity-0 group-hover:opacity-100"
                          title="Marquer comme lu"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      {n.url && (
                        <a 
                          href={n.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="absolute inset-0 z-0"
                          onClick={() => setIsOpen(false)}
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-3 border-t border-border/50 bg-secondary/10">
              <Link 
                href="/intelligence"
                onClick={() => setIsOpen(false)}
                className="block text-center text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Voir tout le flux de veille
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
