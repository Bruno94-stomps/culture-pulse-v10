"use client";
import { useEffect, useState } from "react";
import { useKeywords } from "@/contexts/KeywordContext";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getClientDashboardHeaders } from "@/lib/dashboard";

const API = FASTAPI_BASE_URL;

type AlertResult = {
  alert_type?: string;
  severity?: string;
  title?: string;
  description?: string;
  termo?: string;
  recommended_action?: string;
};

const SEV: Record<string, string> = {
  high:     "bg-red-50 border-red-200 text-red-700",
  critical: "bg-red-100 border-red-300 text-red-800",
  medium:   "bg-amber-50 border-amber-200 text-amber-700",
  low:      "bg-blue-50 border-blue-200 text-blue-700",
};
const SEV_BADGE: Record<string, string> = {
  high: "bg-red-200 text-red-800", critical: "bg-red-300 text-red-900",
  medium: "bg-amber-200 text-amber-800", low: "bg-blue-200 text-blue-800",
};

export default function AlertsPage() {
  const { signals, hasKeywords, keywords, signalsLoading, hydrated } = useKeywords();
  const [alerts, setAlerts] = useState<AlertResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hydrated || signalsLoading || signals.length === 0) return;

    setLoading(true);
    setError("");
    fetch(`${API}/api/v8/intelligence/alerts/batch`, {
      method: "POST",
      headers: { ...getClientDashboardHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ signals }),
    })
      .then((r) => r.json())
      .then((d) => {
        const results: any[] = d?.data?.results ?? [];
        const flat = results.flatMap((r: any) => (Array.isArray(r) ? r : [r]));
        setAlerts(flat);
      })
      .catch(() => setError("Não foi possível carregar alertas"))
      .finally(() => setLoading(false));
  }, [signals]);

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-6">
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-100 text-violet-700">Core</span>
        <h1 className="text-2xl font-bold text-gray-900 mt-2">Alertas</h1>
        <p className="text-sm text-gray-500 mt-1">
          Notificações automáticas quando sinais culturais mudam — {alerts.length} ativos
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
          <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          Avaliando sinais...
        </div>
      )}
      {signalsLoading && !loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
          Buscando sinais reais...
        </div>
      )}
      {error && <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">{error}</div>}
      {!loading && !error && hasKeywords && alerts.length === 0 && (
        <div className="rounded-2xl bg-white border border-gray-200 p-8 text-center">
          <p className="text-sm text-gray-500">Nenhum alerta ativo nos sinais atuais.</p>
        </div>
      )}

      {!loading && alerts.length > 0 && (
        <div className="space-y-3">
          {alerts.map((a, i) => {
            const sev = (a.severity ?? "low").toLowerCase();
            return (
              <div key={i} className={"rounded-2xl border p-5 " + (SEV[sev] ?? "bg-gray-50 border-gray-200 text-gray-700")}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={"text-[10px] font-bold uppercase px-1.5 py-0.5 rounded " + (SEV_BADGE[sev] ?? "bg-gray-200 text-gray-700")}>
                        {sev}
                      </span>
                      {a.alert_type && (
                        <span className="text-[10px] opacity-70 uppercase tracking-wider">{a.alert_type}</span>
                      )}
                    </div>
                    <p className="text-sm font-semibold">{a.title ?? a.termo ?? `Alerta ${i + 1}`}</p>
                    {a.description && <p className="text-xs mt-1 opacity-80">{a.description}</p>}
                    {a.recommended_action && (
                      <p className="text-xs mt-2 font-medium opacity-90">→ {a.recommended_action}</p>
                    )}
                  </div>
                  {a.termo && <span className="text-[10px] shrink-0 opacity-60 mt-0.5">{a.termo}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
