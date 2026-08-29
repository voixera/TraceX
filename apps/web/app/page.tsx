"use client";

import { Activity, Archive, Box, Network, Target, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Open-Source Intelligence Platform Overview
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Cases"
          value="12"
          icon={Archive}
          trend="+3"
          trendUp
        />
        <StatCard
          title="Targets"
          value="47"
          icon={Target}
          trend="+12"
          trendUp
        />
        <StatCard
          title="Entities"
          value="156"
          icon={Box}
          trend="+28"
          trendUp
        />
        <StatCard
          title="Relationships"
          value="234"
          icon={Network}
          trend="+15"
          trendUp
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border border-border rounded-lg bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Investigations</h2>
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="space-y-3">
            <InvestigationItem
              target="example.com"
              type="domain"
              status="completed"
              sources={8}
            />
            <InvestigationItem
              target="octocat/linux-config"
              type="github"
              status="running"
              sources={4}
            />
            <InvestigationItem
              target="techblog"
              type="username"
              status="completed"
              sources={12}
            />
          </div>
        </div>

        <div className="border border-border rounded-lg bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Quick Actions</h2>
            <TrendingUp className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <QuickAction
              title="New Investigation"
              description="Start a new OSINT investigation"
              href="/investigation"
            />
            <QuickAction
              title="View Cases"
              description="Browse existing cases"
              href="/cases"
            />
            <QuickAction
              title="Relationship Graph"
              description="Visualize entity connections"
              href="/graph"
            />
            <QuickAction
              title="Generate Report"
              description="Export investigation data"
              href="/reports"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
}: {
  title: string;
  value: string;
  icon: any;
  trend: string;
  trendUp: boolean;
}) {
  return (
    <div className="border border-border rounded-lg bg-card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="p-2 bg-cyan-400/10 rounded">
          <Icon className="w-5 h-5 text-cyan-400" />
        </div>
      </div>
      <div className="flex items-center gap-1 mt-2">
        <span className={`text-xs ${trendUp ? "text-green-400" : "text-red-400"}`}>
          {trendUp ? "↑" : "↓"} {trend}
        </span>
        <span className="text-xs text-muted-foreground">from last week</span>
      </div>
    </div>
  );
}

function InvestigationItem({
  target,
  type,
  status,
  sources,
}: {
  target: string;
  type: string;
  status: string;
  sources: number;
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-secondary rounded">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-cyan-400" />
        <div>
          <p className="text-sm font-medium">{target}</p>
          <p className="text-xs text-muted-foreground capitalize">{type}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-xs text-muted-foreground">{sources} sources</span>
        <span
          className={`text-xs px-2 py-0.5 rounded ${
            status === "completed"
              ? "bg-green-400/10 text-green-400"
              : "bg-yellow-400/10 text-yellow-400"
          }`}
        >
          {status}
        </span>
      </div>
    </div>
  );
}

function QuickAction({
  title,
  description,
  href,
}: {
  title: string;
  description: string;
  href: string;
}) {
  return (
    <a
      href={href}
      className="block p-3 border border-border rounded hover:border-cyan-400/50 hover:bg-secondary/50 transition-all"
    >
      <p className="text-sm font-medium">{title}</p>
      <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
    </a>
  );
}