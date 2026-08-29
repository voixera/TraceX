"use client";

import { Activity } from "lucide-react";

const mockActivity = [
  { time: "13:45:22", action: "Investigation started", user: "system", details: "example.com" },
  { time: "13:45:30", action: "DNS collector completed", user: "system", details: "4 records found" },
  { time: "13:45:35", action: "TLS collector completed", user: "system", details: "Valid certificate" },
  { time: "13:45:40", action: "Entity created", user: "system", details: "example.com" },
  { time: "13:45:42", action: "Relationship discovered", user: "system", details: "domain → ip" },
  { time: "13:46:00", action: "Investigation completed", user: "system", details: "5 collectors, 12 entities" },
];

export default function ActivityPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Activity</h1>
        <p className="text-muted-foreground text-sm mt-1">
          System activity and audit log
        </p>
      </div>

      <div className="border border-border rounded-lg bg-card overflow-hidden">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Activity className="w-4 h-4" />
            <span>Real-time activity feed</span>
          </div>
        </div>
        <div className="divide-y divide-border">
          {mockActivity.map((item, i) => (
            <div key={i} className="p-4 flex items-start gap-4 hover:bg-secondary/30 transition-colors">
              <div className="w-20 font-mono text-xs text-muted-foreground">
                {item.time}
              </div>
              <div className="flex-1">
                <p className="text-sm">{item.action}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{item.details}</p>
              </div>
              <div className="text-xs text-muted-foreground">{item.user}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}