"use client";

import { Activity, Archive, Box, FileText, GitBranch, Home, Network, Settings, Shield, Target } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "../lib/utils";

const routes = [
  { label: "Dashboard", icon: Home, href: "/" },
  { label: "Cases", icon: Archive, href: "/cases" },
  { label: "Investigation", icon: Target, href: "/investigation" },
  { label: "Entities", icon: Box, href: "/entities" },
  { label: "Graph", icon: Network, href: "/graph" },
  { label: "Evidence", icon: FileText, href: "/evidence" },
  { label: "Sources", icon: GitBranch, href: "/sources" },
  { label: "Activity", icon: Activity, href: "/activity" },
  { label: "Settings", icon: Settings, href: "/settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 border-r border-border bg-card flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-cyan-400" />
          <div>
            <h1 className="font-bold text-sm">TraceX</h1>
            <p className="text-[10px] text-muted-foreground font-mono">v0.1.0</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {routes.map((route) => {
          const Icon = route.icon;
          const isActive = pathname === route.href;

          return (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded text-sm transition-colors",
                isActive
                  ? "bg-cyan-400/10 text-cyan-400 border border-cyan-400/20"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="w-4 h-4" />
              <span>{route.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border">
        <div className="text-[10px] text-muted-foreground font-mono">
          <div className="flex justify-between">
            <span>API</span>
            <span className="text-green-400">● ONLINE</span>
          </div>
          <div className="flex justify-between mt-1">
            <span>DB</span>
            <span className="text-green-400">● ONLINE</span>
          </div>
        </div>
      </div>
    </aside>
  );
}