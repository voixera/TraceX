"use client";

import { Save, Key, Shield, Bell, Database } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Configure TraceX platform settings
        </p>
      </div>

      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-semibold">General</h2>
        </div>
        <div className="space-y-4">
          <SettingRow label="Platform Name" value="TraceX" />
          <SettingRow label="Environment" value="production" />
          <SettingRow label="API URL" value="http://localhost:8000" />
        </div>
      </div>

      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <Key className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-semibold">API Keys</h2>
        </div>
        <div className="space-y-3">
          <ApiKeyRow name="GitHub Token" status="not configured" />
          <ApiKeyRow name="Telegram Bot" status="not configured" />
        </div>
      </div>

      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-semibold">Data Retention</h2>
        </div>
        <div className="space-y-4">
          <SettingRow label="Evidence Retention" value="90 days" />
          <SettingRow label="Investigation Logs" value="30 days" />
        </div>
      </div>

      <div className="flex justify-end">
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-background rounded font-medium text-sm hover:bg-cyan-500">
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>
    </div>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <code className="font-mono text-sm bg-secondary px-3 py-1 rounded">
        {value}
      </code>
    </div>
  );
}

function ApiKeyRow({ name, status }: { name: string; status: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-secondary rounded">
      <div>
        <p className="text-sm font-medium">{name}</p>
        <p className="text-xs text-muted-foreground">{status}</p>
      </div>
      <button className="text-xs px-3 py-1 border border-border rounded hover:bg-card">
        Configure
      </button>
    </div>
  );
}