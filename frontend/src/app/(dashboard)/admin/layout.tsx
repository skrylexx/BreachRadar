"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Users, Key, Mail, Clock, ShieldCheck, Settings } from "lucide-react";

const ADMIN_NAV = [
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/api-keys", label: "API Keys", icon: Key },
  { href: "/admin/smtp", label: "SMTP", icon: Mail },
  { href: "/admin/scheduling", label: "Scheduling", icon: Clock },
  { href: "/admin/audit", label: "Audit Trail", icon: ShieldCheck },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="space-y-6">
      {/* ─── Admin Sub-Navigation ────────────────────────────────────────────── */}
      <div className="card-soc p-2 overflow-x-auto custom-scrollbar">
        <nav className="flex items-center gap-1 min-w-max">
          {ADMIN_NAV.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors
                  ${isActive 
                    ? "bg-radar/10 text-radar border border-radar/20" 
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground border border-transparent"}
                `}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* ─── Admin Page Content ──────────────────────────────────────────────── */}
      <div className="admin-content-guard">
        {children}
      </div>
    </div>
  );
}
