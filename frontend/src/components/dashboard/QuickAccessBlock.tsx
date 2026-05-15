"use client";

import { Box, FileText, Github, Globe, Key, Link as LinkIcon, Lock, Search } from "lucide-react";
import Link from "next/link";

const QUICK_LINKS = [
  { href: "/reports", label: "Reports", icon: FileText, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" },
  { href: "/tools/hibp", label: "HIBP", icon: Key, color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" },
  { href: "/tools/github", label: "GitHub", icon: Github, color: "text-slate-300", bg: "bg-slate-500/10 border-slate-500/20" },
  { href: "/tools/ransomlook", label: "RansomLook", icon: Lock, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20" },
  { href: "/tools/urlscan", label: "URLScan", icon: Globe, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" },
  { href: "/tools/otx", label: "OTX", icon: Search, color: "text-orange-400", bg: "bg-orange-500/10 border-orange-500/20" },
];

export function QuickAccessBlock() {
  return (
    <div className="card-soc flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
        <Box className="w-4 h-4 text-radar" strokeWidth={1.5} />
        <h3 className="text-sm font-semibold text-foreground">Quick Access</h3>
      </div>
      
      <div className="p-4 grid grid-cols-2 gap-2 flex-grow content-start">
        {QUICK_LINKS.map((link) => {
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-2.5 p-2 rounded-md border transition-colors hover:brightness-125 ${link.bg}`}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${link.color}`} strokeWidth={1.5} />
              <span className="text-xs font-medium text-foreground truncate">{link.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
