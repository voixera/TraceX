"use client";

import { useState } from "react";
import { Search, Globe, Github, User, Link as LinkIcon, Play } from "lucide-react";

const targetTypes = [
  { id: "domain", label: "Domain", icon: Globe, color: "text-cyan-400" },
  { id: "url", label: "URL", icon: LinkIcon, color: "text-blue-400" },
  { id: "github", label: "GitHub", icon: Github, color: "text-white" },
  { id: "username", label: "Username", icon: User, color: "text-purple-400" },
];

export default function InvestigationPage() {
  const [selectedType, setSelectedType] = useState("domain");
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);

  const handleInvestigate = () => {
    if (!target) return;
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Investigation</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Start a new OSINT investigation
        </p>
      </div>

      <div className="max-w-2xl">
        <div className="border border-border rounded-lg bg-card p-6 space-y-6">
          <div>
            <label className="text-sm font-medium block mb-3">Target Type</label>
            <div className="grid grid-cols-4 gap-3">
              {targetTypes.map((t) => {
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    onClick={() => setSelectedType(t.id)}
                    className={`flex flex-col items-center gap-2 p-4 rounded border transition-all ${
                      selectedType === t.id
                        ? "border-cyan-400 bg-cyan-400/10"
                        : "border-border hover:border-cyan-400/50"
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${t.color}`} />
                    <span className="text-xs">{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium block mb-2">
              Target {selectedType === "domain" ? "Domain" : selectedType === "url" ? "URL" : "Value"}
            </label>
            <div className="relative">
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder={
                  selectedType === "domain"
                    ? "example.com"
                    : selectedType === "url"
                    ? "https://example.com"
                    : selectedType === "github"
                    ? "owner/repository"
                    : "username"
                }
                className="w-full h-11 px-4 bg-secondary border border-border rounded font-mono text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
              />
              <Search className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Enter a {selectedType} to investigate
            </p>
          </div>

          <button
            onClick={handleInvestigate}
            disabled={!target || loading}
            className="w-full h-11 flex items-center justify-center gap-2 bg-cyan-400 text-background rounded font-medium text-sm hover:bg-cyan-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
                Investigating...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start Investigation
              </>
            )}
          </button>
        </div>

        <div className="mt-6 border border-border rounded-lg bg-card p-6">
          <h3 className="text-sm font-medium mb-3">Available Collectors</h3>
          <div className="grid grid-cols-2 gap-2">
            {["DNS Records", "TLS Certificate", "HTTP Analysis", "GitHub API", "WHOIS", "Technology Detection"].map((c) => (
              <div
                key={c}
                className="flex items-center gap-2 p-2 bg-secondary rounded text-sm"
              >
                <div className="w-2 h-2 rounded-full bg-green-400" />
                {c}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}