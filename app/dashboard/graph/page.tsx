"use client";
import { useEffect, useState } from "react";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

type Node = { id: string; label?: string; size?: number; weight?: number };
type Edge = { source: string; target: string; weight?: number; strength?: number };

export default function GraphPage() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/v8/graph/circles-network`, {
      headers: getClientDashboardHeaders(),
    })
      .then((r) => r.json())
      .then((d) => {
        const data = d?.data ?? d;
        setNodes(data?.nodes ?? []);
        setEdges(data?.edges ?? data?.links ?? []);
        if (!data?.nodes || data.nodes.length === 0) throw new Error("Vazio");
      })
      .catch(() => {
        setError("Falha ao carregar o grafo. Tente novamente mais tarde.");
        setNodes([]);
        setEdges([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">Territorios</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Grafo Cultural</h1>
        <p className="text-sm text-gray-500 mt-1">Conexoes e tensoes entre os 16 circulos culturais brasileiros</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          Carregando grafo...
        </div>
      )}

      {error && <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">{error}</div>}

      {!loading && !error && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Nodes */}
          <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Circulos ({nodes.length})</h2>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {nodes.map((n) => {
                const strength = n.weight ?? n.size ?? 0;
                const pct = Math.min(100, Math.round(strength * 100));
                return (
                  <div key={n.id} className="flex items-center gap-3">
                    <span className="w-32 text-xs text-gray-600 truncate shrink-0">{n.label ?? n.id}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                      <div className="bg-violet-400 h-1.5 rounded-full" style={{ width: pct + "%" }} />
                    </div>
                    <span className="w-8 text-right text-[10px] text-gray-400">{strength.toFixed ? strength.toFixed(2) : strength}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Edges */}
          <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Conexoes mais fortes ({edges.length})</h2>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {[...edges]
                .sort((a, b) => (b.weight ?? b.strength ?? 0) - (a.weight ?? a.strength ?? 0))
                .slice(0, 20)
                .map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
                    <span className="px-2 py-0.5 bg-violet-50 rounded text-violet-700 truncate max-w-24">{e.source}</span>
                    <span className="text-gray-400">↔</span>
                    <span className="px-2 py-0.5 bg-blue-50 rounded text-blue-700 truncate max-w-24">{e.target}</span>
                    <span className="ml-auto text-gray-400 shrink-0">{((e.weight ?? e.strength ?? 0) as number).toFixed(2)}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
