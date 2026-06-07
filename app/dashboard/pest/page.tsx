"use client";
import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend,
} from "recharts";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

const PEST_COLORS: Record<string, string> = { P: "#ef4444", E: "#3b82f6", S: "#22c55e", T: "#8b5cf6" };
const PEST_LABELS: Record<string, string> = { P: "Político", E: "Econômico", S: "Social", T: "Tecnológico" };
const PEST_BADGE: Record<string, string> = {
  P: "bg-red-100 text-red-700",
  E: "bg-blue-100 text-blue-700",
  S: "bg-green-100 text-green-700",
  T: "bg-violet-100 text-violet-700",
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg px-3 py-2 text-xs">
      <p className="font-semibold">{payload[0].payload.fullName}</p>
      <p className="text-gray-500">{payload[0].value} sinais</p>
    </div>
  );
};

export default function PestPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v8/pest/stats`, {
      headers: getClientDashboardHeaders(),
    })
      .then((r) => r.json())
      .then((d) => setStats(d?.data ?? d))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const dist = stats?.distribution ?? stats?.category_distribution ?? {};
  const total = stats?.total ?? (Object.values(dist) as number[]).reduce((a, b) => a + b, 0);

  const chartData = ["P", "E", "S", "T"].map((cat) => ({
    cat,
    fullName: PEST_LABELS[cat],
    count: dist[cat] ?? dist[PEST_LABELS[cat]] ?? 0,
    pct: total > 0 ? Math.round(((dist[cat] ?? dist[PEST_LABELS[cat]] ?? 0) / (total as number)) * 100) : 0,
  }));

  const pieData = chartData.filter((d) => d.count > 0).map((d) => ({
    name: d.fullName,
    value: d.count,
    fill: PEST_COLORS[d.cat],
  }));

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Enterprise</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Análise PEST</h1>
        <p className="text-sm text-gray-500 mt-1">Forças Políticas, Econômicas, Sociais e Tecnológicas no contexto cultural brasileiro</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          Carregando análise PEST...
        </div>
      )}

      {!loading && stats && (
        <div className="space-y-5">
          {/* KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {chartData.map(({ cat, fullName, count, pct }) => (
              <div key={cat} className="rounded-2xl bg-white border border-gray-200 shadow-sm p-5 text-center">
                <span className={"inline-flex items-center justify-center text-lg font-extrabold w-10 h-10 rounded-full mx-auto mb-2 " + PEST_BADGE[cat]}>
                  {cat}
                </span>
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-[10px] text-gray-500 mt-0.5">{fullName} · {pct}%</p>
              </div>
            ))}
          </div>

          {/* Bar + Pie side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Distribuição — {total} sinais</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData} margin={{ bottom: 4 }}>
                  <XAxis dataKey="cat" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {chartData.map((d) => (
                      <Cell key={d.cat} fill={PEST_COLORS[d.cat]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {pieData.length > 0 && (
              <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">Proporção por categoria</h2>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v: any) => [`${v} sinais`]} contentStyle={{ fontSize: 12 }} />
                    <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
