"use client";
import { useEffect, useState } from "react";
import { useKeywords } from "@/contexts/KeywordContext";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

type Opportunity = {
  opportunity_type?: string;
  confidence?: number;
  title?: string;
  description?: string;
  window_weeks?: number;
  potential?: string;
  actions?: string[];
};

const POTENTIAL_COLOR: Record<string, string> = {
  high:   "text-green-700 bg-green-50 border-green-200",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  low:    "text-gray-600 bg-gray-50 border-gray-200",
};

export default function OpportunitiesPage() {
  const { signals, hasKeywords, keywords, signalsLoading, hydrated } = useKeywords();
  const [items, setItems] = useState<{ termo: string; opps: Opportunity[] }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!hydrated || signalsLoading || signals.length === 0) return;

    setLoading(true);
    fetch(`${API}/api/v8/intelligence/opportunities/batch`, {
      method: "POST",
      headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ signals }),
    })
      .then((r) => r.json())
      .then((d) => {
        const raw: any[] = d?.data?.results ?? [];
        const grouped = signals.map((sig, i) => ({
          termo: sig.termo,
          opps: Array.isArray(raw[i]) ? raw[i] : [],
        })).filter((g) => g.opps.length > 0);
        setItems(grouped);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [signals]);

  const total = items.reduce((acc, g) => acc + g.opps.length, 0);

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Enterprise</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Oportunidades</h1>
        <p className="text-sm text-gray-500 mt-1">
          {total > 0 ? `${total} janelas de oportunidade identificadas` : "Janelas de oportunidade cultural identificadas automaticamente"}
        </p>
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
          Identificando oportunidades...
        </div>
      )}
      {signalsLoading && !loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
          Buscando sinais reais...
        </div>
      )}

      <div className="space-y-6">
        {items.map((group, gi) => (
          <div key={gi}>
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              {group.termo}
            </h2>
            <div className="space-y-3">
              {group.opps.map((opp, oi) => {
                const pot = (opp.potential ?? "medium").toLowerCase();
                return (
                  <div key={oi} className={"rounded-2xl border p-5 " + (POTENTIAL_COLOR[pot] ?? "bg-white border-gray-200")}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold">{opp.title}</span>
                        </div>
                        {opp.description && <p className="text-xs opacity-80">{opp.description}</p>}
                        {opp.actions && opp.actions.length > 0 && (
                          <ul className="mt-2 space-y-0.5">
                            {opp.actions.slice(0, 3).map((a, ai) => (
                              <li key={ai} className="text-xs opacity-70">→ {a}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                      <div className="shrink-0 text-right">
                        <p className="text-xl font-bold">{Math.round((opp.confidence ?? 0) * 100)}%</p>
                        <p className="text-[10px] opacity-60">conf.</p>
                        {opp.window_weeks && (
                          <p className="text-[10px] opacity-60 mt-1">{opp.window_weeks} sem.</p>
                        )}
                      </div>
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
