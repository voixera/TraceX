"use client";

import { Box, ExternalLink } from "lucide-react";

const mockEntities = [
  { id: "1", type: "domain", value: "example.com", confidence: 1.0, sources: 3 },
  { id: "2", type: "subdomain", value: "api.example.com", confidence: 0.95, sources: 2 },
  { id: "3", type: "github", value: "octocat/Hello-World", confidence: 1.0, sources: 1 },
  { id: "4", type: "ip", value: "93.184.216.34", confidence: 1.0, sources: 2 },
  { id: "5", type: "username", value: "octocat", confidence: 0.9, sources: 4 },
  { id: "6", type: "certificate", value: "SHA256:abc123...", confidence: 1.0, sources: 1 },
];

const typeColors: Record<string, string> = {
  domain: "bg-cyan-400/10 text-cyan-400 border-cyan-400/20",
  subdomain: "bg-blue-400/10 text-blue-400 border-blue-400/20",
  github: "bg-white/10 text-white border-white/20",
  ip: "bg-green-400/10 text-green-400 border-green-400/20",
  username: "bg-purple-400/10 text-purple-400 border-purple-400/20",
  certificate: "bg-yellow-400/10 text-yellow-400 border-yellow-400/20",
};

export default function EntitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Entities</h1>
        <p className="text-muted-foreground text-sm mt-1">
          All discovered entities across cases
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockEntities.map((entity) => (
          <div
            key={entity.id}
            className="border border-border rounded-lg bg-card p-4 hover:border-cyan-400/50 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between mb-3">
              <Box className="w-5 h-5 text-cyan-400" />
              <button className="p-1 hover:bg-secondary rounded">
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>
            <div className="space-y-2">
              <span
                className={`inline-block text-[10px] px-2 py-0.5 rounded border font-mono uppercase ${
                  typeColors[entity.type] || ""
                }`}
              >
                {entity.type}
              </span>
              <p className="font-mono text-sm break-all">{entity.value}</p>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Confidence: {(entity.confidence * 100).toFixed(0)}%</span>
                <span>{entity.sources} sources</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}