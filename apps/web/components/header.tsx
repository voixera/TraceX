"use client";

import { Bell, Search, Terminal } from "lucide-react";

export function Header() {
  return (
    <header className="h-14 border-b border-border bg-card px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search cases, targets, entities..."
            className="w-80 h-9 pl-10 pr-4 bg-secondary border border-border rounded text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground bg-background px-1.5 py-0.5 rounded border border-border">
            ⌘K
          </kbd>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="p-2 hover:bg-secondary rounded transition-colors">
          <Terminal className="w-4 h-4 text-muted-foreground" />
        </button>
        <button className="p-2 hover:bg-secondary rounded transition-colors relative">
          <Bell className="w-4 h-4 text-muted-foreground" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-cyan-400 rounded-full" />
        </button>
      </div>
    </header>
  );
}