"use client";
import { useEffect, useState } from "react";
import { useKeywords } from "@/contexts/KeywordContext";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

type Scenario = {
  scenario_type?: string;
  probability?: number;
  horizon_weeks?: number;
  narrative?: string;
  impact_level?: string;
};

const TYPE_COLOR: Record<string, string> = {
  optimistic:    "bg-green-100 text-green-700",
  pessimistic:   "bg-red-100 text-red-700",
  base:          "bg-blue-100 text-blue-700",
  transformative:"bg-violet-100 text-violet-700",
};

export default function ScenariosPage() {
  const { signals, hasKeywords, keywords, signalsLoading, hydrated } = useKeywords();
  const [results, setResults] = useState<{ signal_termo: string; scenarios: Scenario[] }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!hydrated || signalsLoading || signals.length === 0) return;

    setLoading(true);
    fetch(`${API}/api/v8/intelligence/scenarios/batch`, {
      method: "POST",
      headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ signals }),
    })
      .then((r) => r.json())
      .then((d) => {
        const raw: any[] = d?.data?.results ?? [];
        setResults(raw.filter((r) => r?.signal_termo));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [signals]);

  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Enterprise</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Cenários Futuros</h1>
        <p className="text-sm text-gray-500 mt-1">Projeções culturais 6-12 semanas à frente por sinal</p>
      </div>

      {!hasKeywords && (
        <div className="rounded-2xl bg-violet-50 border border-violet-100 p-6 text-center">
          <p className="text-sm text-violet-700 font-medium">Nenhuma keyword ativa.</p>
          <a href="/onboarding" className="mt-2 inline-block text-xs text-violet-500 underline">Definir palavras-chave →</a>
        </div>
      )}

      {hasKeywords && (
        <div className="mb-4 flex flex-wrap gap-1.5">
          {keywords.map((kw) => (
            <span key={kw} className="text-xs bg-violet-50 text-violet-700 border border-violet-100 px-2 py-0.5 rounded-full">{kw}</span>
          ))}
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          Calculando cenários...
        </div>
      )}
      {signalsLoading && !loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
          Buscando sinais reais...
        </div>
      )}

      <div className="space-y-6">
        {results.map((group, gi) => (
          <div key={gi} className="rounded-2xl bg-white border border-gray-200 shadow-sm p-6">
            <h2 className="text-sm font-semibold text-gray-800 mb-4">
              Sinal: <span className="text-violet-700">{group.signal_termo}</span>
            </h2>
            <div className="grid md:grid-cols-2 gap-3">
              {(group.scenarios ?? []).map((s, si) => {
                const type = (s.scenario_type ?? "base").toLowerCase();
                return (
                  <div key={si} className="rounded-xl bg-gray-50 border border-gray-100 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className={"text-[10px] font-bold uppercase px-2 py-0.5 rounded-full " + (TYPE_COLOR[type] ?? "bg-gray-200 text-gray-700")}>
                        {type}
                      </span>
                      <div className="text-right">
                        <span className="text-sm font-bold text-gray-900">{Math.round((s.probability ?? 0) * 100)}%</span>
                        <span className="text-[10px] text-gray-400 ml-1">prob.</span>
                      </div>
                    </div>
                    {s.narrative && <p className="text-xs text-gray-600 leading-relaxed">{s.narrative}</p>}
                    <div className="flex items-center justify-between mt-2">
                      {s.horizon_weeks && <span className="text-[10px] text-gray-400">{s.horizon_weeks} semanas</span>}
                      {s.impact_level && <span className="text-[10px] font-medium text-gray-500">impacto: {s.impact_level}</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
