"use client";

import { GitBranch, Activity, AlertCircle } from "lucide-react";

const mockSources = [
  { name: "DNS", type: "dns", status: "active", rate: "5 req/s", lastCall: "2s ago" },
  { name: "GitHub API", type: "api", status: "active", rate: "30 req/min", lastCall: "10s ago" },
  { name: "HTTP", type: "http", status: "active", rate: "60 req/min", lastCall: "1m ago" },
  { name: "TLS", type: "certificate", status: "active", rate: "20 req/min", lastCall: "5m ago" },
];

export default function SourcesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Sources</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Available data sources and collectors
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockSources.map((source) => (
          <div
            key={source.name}
            className="border border-border rounded-lg bg-card p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <GitBranch className="w-5 h-5 text-cyan-400" />
                <div>
                  <p className="font-medium">{source.name}</p>
                  <p className="text-xs text-muted-foreground uppercase font-mono">
                    {source.type}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-xs text-green-400">{source.status}</span>
              </div>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rate Limit</span>
                <span className="font-mono">{source.rate}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Call</span>
                <span className="font-mono">{source.lastCall}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}