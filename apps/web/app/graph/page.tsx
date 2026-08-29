"use client";

import { useState } from "react";
import { ZoomIn, ZoomOut, Download, Maximize2 } from "lucide-react";

const mockNodes = [
  { id: "1", label: "example.com", type: "domain", x: 400, y: 100 },
  { id: "2", label: "github.com/user", type: "github", x: 200, y: 250 },
  { id: "3", label: "user123", type: "username", x: 600, y: 250 },
  { id: "4", label: "api.example.com", type: "subdomain", x: 300, y: 400 },
  { id: "5", label: "93.184.216.34", type: "ip", x: 500, y: 400 },
];

const mockEdges = [
  { source: "1", target: "2", label: "references" },
  { source: "1", target: "3", label: "mentions" },
  { source: "1", target: "4", label: "hosts" },
  { source: "1", target: "5", label: "resolves_to" },
];

const typeColors: Record<string, string> = {
  domain: "bg-cyan-400",
  github: "bg-white",
  username: "bg-purple-400",
  subdomain: "bg-blue-400",
  ip: "bg-green-400",
};

export default function GraphPage() {
  const [zoom, setZoom] = useState(1);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Relationship Graph</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Visualize entity connections
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))}
            className="p-2 border border-border rounded hover:bg-secondary"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm font-mono w-16 text-center">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(2, z + 0.1))}
            className="p-2 border border-border rounded hover:bg-secondary"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-border mx-2" />
          <button className="p-2 border border-border rounded hover:bg-secondary">
            <Download className="w-4 h-4" />
          </button>
          <button className="p-2 border border-border rounded hover:bg-secondary">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 border border-border rounded-lg bg-card overflow-hidden relative">
        <svg
          width="100%"
          height="100%"
          className="min-h-[500px]"
          style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="hsl(215, 20%, 65%)" />
            </marker>
          </defs>

          {mockEdges.map((edge, i) => {
            const source = mockNodes.find((n) => n.id === edge.source)!;
            const target = mockNodes.find((n) => n.id === edge.target)!;
            const midX = (source.x + target.x) / 2;
            const midY = (source.y + target.y) / 2;

            return (
              <g key={i}>
                <line
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke="hsl(215, 20%, 65%)"
                  strokeWidth="1.5"
                  markerEnd="url(#arrowhead)"
                />
                <text
                  x={midX}
                  y={midY - 5}
                  fill="hsl(215, 20%, 65%)"
                  fontSize="10"
                  textAnchor="middle"
                  className="font-mono"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {mockNodes.map((node) => (
            <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
              <rect
                x="-60"
                y="-20"
                width="120"
                height="40"
                rx="4"
                fill="hsl(222, 47%, 14%)"
                stroke="hsl(215, 20%, 25%)"
                strokeWidth="1"
                className="hover:stroke-cyan-400 cursor-pointer"
              />
              <circle
                cx="-45"
                cy="0"
                r="4"
                className={typeColors[node.type] || "bg-gray-400"}
              />
              <text
                x="-35"
                y="5"
                fill="hsl(210, 40%, 98%)"
                fontSize="11"
                className="font-mono"
              >
                {node.label.length > 12
                  ? node.label.slice(0, 12) + "..."
                  : node.label}
              </text>
            </g>
          ))}
        </svg>

        <div className="absolute bottom-4 left-4 p-3 bg-secondary/90 border border-border rounded text-xs space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-cyan-400" />
            <span>Domain</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-white" />
            <span>GitHub</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-400" />
            <span>Username</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-400" />
            <span>Subdomain</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-400" />
            <span>IP Address</span>
          </div>
        </div>
      </div>
    </div>
  );
}