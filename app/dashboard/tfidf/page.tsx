"use client";
import { useState } from "react";
import { useKeywords } from "@/contexts/KeywordContext";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

const COLORS = ["#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe"];

export default function TfidfPage() {
  const { keywords: ctxKeywords, periodDays } = useKeywords();
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [ranOnce, setRanOnce] = useState(false);

  // Use context keywords if user hasn't typed anything
  const activeKeywords = inputText
    ? inputText.split(",").map((k) => k.trim()).filter(Boolean)
    : ctxKeywords;

  async function run() {
    if (activeKeywords.length === 0) return;
    setLoading(true);
    setResult(null);
    setRanOnce(true);
    const r = await fetch(`${API}/api/v8/explore/themes`, {
      method: "POST",
      headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ keywords: activeKeywords, period_days: periodDays }),
    });
    const d = await r.json();
    setResult(d?.data ?? null);
    setLoading(false);
  }

  const terms: string[] = result?.top_terms ?? [];
  const weights: number[] = result?.term_weights ?? [];

  const chartData = terms.map((term, i) => ({
    term: term.length > 16 ? term.slice(0, 14) + "…" : term,
    fullTerm: term,
    weight: parseFloat((weights[i] ?? 0).toFixed(3)),
  }));

  const circleData = result?.circle_distribution
    ? Object.entries(result.circle_distribution)
        .sort((a: any, b: any) => b[1] - a[1])
        .map(([name, val]: [string, any]) => ({ name, value: Math.round(val) }))
    : [];

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">Territorios</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">TF-IDF</h1>
        <p className="text-sm text-gray-500 mt-1">Relevância estatística de termos nos sinais culturais</p>
      </div>

      {/* Input */}
      <div className="flex gap-3 mb-2">
        <input
          className="flex-1 h-10 px-4 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
          placeholder={ctxKeywords.length > 0 ? ctxKeywords.join(", ") : "Ex: musica, funk, sertanejo"}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <button
          onClick={run}
          disabled={loading || activeKeywords.length === 0}
          className="px-5 h-10 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl transition"
        >
          {loading ? "Analisando..." : "Analisar"}
        </button>
      </div>
      {ctxKeywords.length > 0 && !inputText && (
        <p className="text-xs text-violet-500 mb-6">Usando keywords do seu projeto: <strong>{ctxKeywords.join(", ")}</strong></p>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-5 mt-6">
          {/* Bar chart */}
          <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-5">
              Relevância dos Termos — {result.total_signals ?? 0} sinais analisados
            </h2>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 32 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => v.toFixed(2)} />
                <YAxis type="category" dataKey="term" width={130} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [val.toFixed(3), "TF-IDF"]}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.fullTerm ?? ""}
                  contentStyle={{ fontSize: 12 }}
                />
                <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Circle distribution */}
          {circleData.length > 0 && (
            <div className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">Distribuição por Círculo Cultural</h2>
              <div className="flex flex-wrap gap-2">
                {circleData.map(({ name, value }) => (
                  <span key={name} className="text-xs px-3 py-1 rounded-full bg-violet-50 text-violet-700 border border-violet-100">
                    {name} · {value}%
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!ranOnce && ctxKeywords.length > 0 && (
        <div className="mt-6 rounded-2xl bg-violet-50 border border-violet-100 p-6 text-center">
          <p className="text-sm text-violet-600 font-medium mb-3">Pronto para analisar <strong>{ctxKeywords.join(", ")}</strong></p>
          <button onClick={run} className="px-6 py-2 bg-violet-600 text-white rounded-xl text-sm font-medium hover:bg-violet-500 transition">
            Rodar análise TF-IDF →
          </button>
        </div>
      )}
    </div>
  );
}
