"use client";
import { useState } from "react";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

const COLORS = ["bg-violet-100 text-violet-700","bg-blue-100 text-blue-700","bg-green-100 text-green-700","bg-amber-100 text-amber-700","bg-rose-100 text-rose-700","bg-cyan-100 text-cyan-700"];

export default function ClusteringPage() {
  const [terms, setTerms] = useState("musica,funk,sertanejo,rap,forró,baile,show");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setResult(null);
    try {
      const termList = terms.split(",").map((t) => t.trim()).filter(Boolean);
      const r = await fetch(`${API}/api/v8/clusters/label`, {
        method: "POST",
        headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ terms: termList, n_clusters: 3 }),
      });
      if (!r.ok) throw new Error("API Offline");
      const d = await r.json();
      setResult(d?.data ?? d);
    } catch (e) {
      setResult({ clusters: [] });
    }
    setLoading(false);
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">Territorios</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Clustering</h1>
        <p className="text-sm text-gray-500 mt-1">Agrupamento semantico de sinais culturais</p>
      </div>

      <div className="flex gap-3 mb-6">
        <input
          className="flex-1 h-10 px-4 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
          placeholder="Termos separados por virgula"
          value={terms}
          onChange={(e) => setTerms(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <button
          onClick={run}
          disabled={loading}
          className="px-5 h-10 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl transition"
        >
          {loading ? "Agrupando..." : "Agrupar"}
        </button>
      </div>

      {result && (
        <div className="space-y-3">
          {(result.clusters ?? result.labels ?? []).map((cluster: any, i: number) => (
            <div key={i} className="rounded-2xl bg-white border border-gray-200 shadow-sm p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className={"text-xs font-semibold px-2 py-0.5 rounded-full " + (COLORS[i % COLORS.length])}>
                  Cluster {i + 1}
                </span>
                {cluster.label && <span className="text-sm font-semibold text-gray-800">{cluster.label}</span>}
              </div>
              {cluster.terms && (
                <div className="flex flex-wrap gap-1.5">
                  {cluster.terms.map((t: string) => (
                    <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{t}</span>
                  ))}
                </div>
              )}
              {cluster.coherence !== undefined && (
                <p className="text-[10px] text-gray-400 mt-2">Coerencia: {(cluster.coherence * 100).toFixed(0)}%</p>
              )}
            </div>
          ))}

          {/* Fallback: raw response */}
          {!(result.clusters ?? result.labels) && (
            <div className="rounded-2xl bg-white border border-gray-200 p-5">
              <pre className="text-xs text-gray-600 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
