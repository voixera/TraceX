"use client";

import { FileText, ExternalLink, Clock } from "lucide-react";

const mockEvidence = [
  {
    id: "001",
    source: "DNS",
    observation: "A record resolves to 93.184.216.34",
    collector: "domain",
    timestamp: "2026-08-29 13:42 UTC",
    confidence: 1.0,
  },
  {
    id: "002",
    source: "TLS Certificate",
    observation: "Valid certificate issued by Let's Encrypt",
    collector: "domain",
    timestamp: "2026-08-29 13:42 UTC",
    confidence: 1.0,
  },
  {
    id: "003",
    source: "GitHub API",
    observation: "Repository has 1,234 stars",
    collector: "github",
    timestamp: "2026-08-29 13:45 UTC",
    confidence: 0.95,
  },
];

export default function EvidencePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Evidence</h1>
        <p className="text-muted-foreground text-sm mt-1">
          All collected evidence and observations
        </p>
      </div>

      <div className="space-y-4">
        {mockEvidence.map((evidence) => (
          <div
            key={evidence.id}
            className="border border-border rounded-lg bg-card p-4"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-cyan-400" />
                <div>
                  <span className="font-mono text-cyan-400 text-sm">
                    #{evidence.id}
                  </span>
                  <span className="text-muted-foreground text-sm ml-2">
                    {evidence.source}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                {evidence.timestamp}
              </div>
            </div>
            <p className="text-sm mb-3">{evidence.observation}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                Collector: {evidence.collector}
              </span>
              <span className="text-xs px-2 py-0.5 bg-secondary rounded">
                Confidence: {(evidence.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}