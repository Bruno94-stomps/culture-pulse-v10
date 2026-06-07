"use client";
import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

const RISK_COLORS: Record<string, string> = {
  critical: "#dc2626",
  high:     "#f97316",
  medium:   "#eab308",
  low:      "#22c55e",
};

const RISK_BADGE: Record<string, string> = {
  critical: "text-red-800 bg-red-100 border-red-300",
  high:     "text-orange-700 bg-orange-50 border-orange-200",
  medium:   "text-amber-700 bg-amber-50 border-amber-200",
  low:      "text-green-700 bg-green-50 border-green-200",
};

export default function RiskPage() {
  const [matrix, setMatrix] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v8/stability-risk/matrix`, {
      headers: getClientDashboardHeaders(),
    })
      .then((r) => r.json())
      .then((d) => setMatrix(d?.data ?? d))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const items: any[] = matrix?.signals ?? matrix?.items ?? matrix?.risks ?? (Array.isArray(matrix) ? matrix : []);

  // Build chart data from risk level counts
  const riskCounts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  items.forEach((item) => {
    const lvl = (item.risk_level ?? item.risk ?? "low").toLowerCase();
    if (lvl in riskCounts) riskCounts[lvl]++;
    else riskCounts.low++;
  });
  const chartData = Object.entries(riskCounts)
    .filter(([, v]) => v > 0)
    .map(([level, count]) => ({ level, label: level.charAt(0).toUpperCase() + level.slice(1), count }));

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Enterprise</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Risco & Vulnerabilidade</h1>
        <p className="text-sm text-gray-500 mt-1">Mapeamento de riscos culturais e vulnerabilidades de marcas</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          Carregando matriz de risco...
        </div>
      )}

      {!loading && (
        <div className="space-y-5">
          {/* KPI cards */}
          {matrix && !Array.isArray(matrix) && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {(["critical", "high", "medium", "low"] as const).map((k) => {
                const val = matrix[k + "_risk"] ?? matrix[k] ?? riskCounts[k];
                if (val === undefined) return null;
                return (
                  <div key={k} className="rounded-xl bg-white border border-gray-200 p-4 text-center shadow-sm">
                    <p className="text-2xl font-bold text-gray-900">{val}</p>
                    <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-wide">{k}</p>
                  </div>
                );
              })}
              {matrix.total !== undefined && (
                <div className="rounded-xl bg-white border border-gray-200 p-4 text-center shadow-sm">
                  <p className="text-2xl font-bold text-gray-900">{matrix.total}</p>
                  <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-wide">total</p>
                </div>
              )}
            </div>
          )}

          {/* Bar chart */}
          {chartData.length > 0 && (
            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-5">Sinais por nível de risco</h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{ bottom: 4 }}>
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip
                    formatter={(v: any) => [`${v} sinais`, "Quantidade"]}
                    contentStyle={{ fontSize: 12 }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {chartData.map((d) => (
                      <Cell key={d.level} fill={RISK_COLORS[d.level] ?? "#94a3b8"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Signal list */}
          {items.length > 0 && (
            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Detalhamento de sinais</h2>
              <div className="space-y-2">
                {items.slice(0, 20).map((item: any, i: number) => {
                  const risk = (item.risk_level ?? item.risk ?? "low").toLowerCase();
                  return (
                    <div key={i} className={"rounded-xl border p-3 flex items-center gap-3 " + (RISK_BADGE[risk] ?? "bg-gray-50 border-gray-200")}>
                      <span className="text-[10px] font-bold uppercase w-16 shrink-0">{risk}</span>
                      <span className="text-xs font-medium flex-1 truncate">{item.termo ?? item.name ?? item.circle ?? `Item ${i + 1}`}</span>
                      {item.score !== undefined && (
                        <span className="text-xs font-bold shrink-0">{Number(item.score).toFixed(2)}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {items.length === 0 && (
            <div className="rounded-2xl bg-white border border-gray-200 p-8 text-center">
              <p className="text-sm text-gray-500">Nenhum dado de risco disponível ainda.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
