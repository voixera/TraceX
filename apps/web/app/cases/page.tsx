"use client";

import { Plus, Search, Filter } from "lucide-react";

const mockCases = [
  {
    id: "TRX-2026-001",
    name: "Example Domain Investigation",
    targets: 7,
    evidence: 17,
    sources: 8,
    status: "active",
    created: "2026-08-29",
  },
  {
    id: "TRX-2026-002",
    name: "GitHub Repository Analysis",
    targets: 3,
    evidence: 12,
    sources: 5,
    status: "active",
    created: "2026-08-28",
  },
  {
    id: "TRX-2026-003",
    name: "Username Correlation Study",
    targets: 5,
    evidence: 8,
    sources: 3,
    status: "archived",
    created: "2026-08-25",
  },
];

export default function CasesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Cases</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your investigation cases
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-background rounded font-medium text-sm hover:bg-cyan-500 transition-colors">
          <Plus className="w-4 h-4" />
          New Case
        </button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search cases..."
            className="w-full h-9 pl-10 pr-4 bg-card border border-border rounded text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
          />
        </div>
        <button className="flex items-center gap-2 px-3 py-2 border border-border rounded text-sm hover:bg-secondary">
          <Filter className="w-4 h-4" />
          Filter
        </button>
      </div>

      <div className="border border-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-card">
            <tr className="text-left text-sm text-muted-foreground">
              <th className="px-4 py-3 font-medium">Case ID</th>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Targets</th>
              <th className="px-4 py-3 font-medium">Evidence</th>
              <th className="px-4 py-3 font-medium">Sources</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {mockCases.map((c) => (
              <tr key={c.id} className="hover:bg-secondary/50 transition-colors cursor-pointer">
                <td className="px-4 py-3 font-mono text-sm text-cyan-400">{c.id}</td>
                <td className="px-4 py-3 text-sm">{c.name}</td>
                <td className="px-4 py-3 text-sm text-center">{c.targets}</td>
                <td className="px-4 py-3 text-sm text-center">{c.evidence}</td>
                <td className="px-4 py-3 text-sm text-center">{c.sources}</td>
                <td className="px-4 py-3">
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      c.status === "active"
                        ? "bg-green-400/10 text-green-400"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {c.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{c.created}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}