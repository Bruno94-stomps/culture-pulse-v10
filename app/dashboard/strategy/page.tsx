"use client";
import { useEffect, useState } from "react";
import { useKeywords } from "@/contexts/KeywordContext";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

type Action = {
  action_type?: string;
  urgency?: number;
  title?: string;
  playbook?: string[];
  channels?: string[];
  kpis?: string[];
  impact_estimate?: string;
  rationale?: string;
};

const URGENCY_COLOR = (u: number) => {
  if (u >= 4) return "border-l-4 border-red-400";
  if (u >= 3) return "border-l-4 border-amber-400";
  return "border-l-4 border-blue-300";
};
const URGENCY_LABEL = (u: number) => {
  if (u >= 4) return "Urgente";
  if (u >= 3) return "Prioritário";
  return "Monitorar";
};

export default function StrategyPage() {
  const { signals, hasKeywords, keywords, signalsLoading, hydrated } = useKeywords();
  const [actions, setActions] = useState<{ termo: string; action: Action }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!hydrated || signalsLoading || signals.length === 0) return;

    setLoading(true);
    fetch(`${API}/api/v8/intelligence/actions/batch`, {
      method: "POST",
      headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ signals }),
    })
      .then((r) => r.json())
      .then((d) => {
        const raw: any[] = d?.data?.results ?? [];
        const mapped = signals.map((sig, i) => ({
          termo: sig.termo,
          action: Array.isArray(raw[i]) ? raw[i][0] : raw[i],
        })).filter((a) => a.action);
        setActions(mapped);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [signals]);

  const sorted = [...actions].sort((a, b) => (b.action.urgency ?? 0) - (a.action.urgency ?? 0));

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">Enterprise</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Ações Estratégicas</h1>
        <p className="text-sm text-gray-500 mt-1">
          Recomendações acionáveis baseadas nos {sorted.length} sinais culturais analisados
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
          Gerando recomendações...
        </div>
      )}
      {signalsLoading && !loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
          Buscando sinais reais...
        </div>
      )}

      <div className="space-y-4">
        {sorted.map(({ termo, action }, i) => {
          const u = action.urgency ?? 1;
          return (
            <div key={i} className={"rounded-2xl bg-white border border-gray-200 shadow-sm p-5 " + URGENCY_COLOR(u)}>
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-[10px] font-bold uppercase text-gray-400">{termo}</span>
                    <span className="text-[10px] font-bold uppercase text-gray-500">{URGENCY_LABEL(u)}</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{action.title}</p>
                  {action.rationale && <p className="text-xs text-gray-500 mt-1">{action.rationale}</p>}
                </div>
                <div className="text-right shrink-0">
                  <p className="text-lg font-bold text-gray-700">{u}/5</p>
                  <p className="text-[10px] text-gray-400">urgência</p>
                </div>
              </div>

              {action.playbook && action.playbook.length > 0 && (
                <div className="mb-3">
                  <p className="text-[10px] font-semibold text-gray-500 uppercase mb-1">Playbook</p>
                  <ol className="space-y-0.5">
                    {action.playbook.slice(0, 4).map((step, si) => (
                      <li key={si} className="text-xs text-gray-600">{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              <div className="flex flex-wrap gap-4 text-[10px] text-gray-500">
                {action.channels && action.channels.length > 0 && (
                  <div>
                    <span className="font-semibold uppercase">Canais: </span>
                    {action.channels.slice(0, 3).join(", ")}
                  </div>
                )}
                {action.kpis && action.kpis.length > 0 && (
                  <div>
                    <span className="font-semibold uppercase">KPIs: </span>
                    {action.kpis.slice(0, 3).join(", ")}
                  </div>
                )}
                {action.impact_estimate && (
                  <div>
                    <span className="font-semibold uppercase">Impacto: </span>
                    {action.impact_estimate}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
