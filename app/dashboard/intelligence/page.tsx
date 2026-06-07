import { createClient } from "@/lib/supabase/server";
import PlanGate from "@/components/auth/PlanGate";
import BrazilianCulturalTwin from "@/components/intelligence/BrazilianCulturalTwin";
import CulturalShield from "@/components/intelligence/CulturalShield";
import FuturesTimeline from "@/components/intelligence/FuturesTimeline";
import ExportDataPublisher from "@/components/dashboard/ExportDataPublisher";
import type { ExportData } from "@/lib/utils/pdf-export";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getCurrentPlan } from "@/lib/plan";
import { getDashboardAuthHeaders } from "@/lib/dashboard";

export const revalidate = 60; // ISR 1 min

/**
 * Inteligência Cultural — Blindagem & Futuros — Server Component.
 *
 * Substitui os Pilares 2 e 3 do Streamlit (que eram 100% hardcoded)
 * por dados REAIS dos 5 engines de inteligência cultural.
 *
 * Endpoint principal:
 *   POST /api/v8/intelligence/full → roda 5 engines de uma vez:
 *     - VulnerabilityEngine   → assess_signal()
 *     - CulturalAlertsEngine  → evaluate_dict()
 *     - StrategicActionsEngine → recommend_dict()
 *     - ScenarioEngine        → generate_dict()
 *     - OpportunityEngine     → detect_dict()
 *
 * Também consome Supabase para top sinais recentes como input.
 */

interface IntelligenceResult {
  signal: Record<string, any>;
  vulnerability: Record<string, any>;
  cultural_alerts: Record<string, any>;
  strategic_action: Record<string, any>;
  scenarios: Record<string, any>;
  opportunities: Record<string, any>;
}

export default async function IntelligencePage() {
  const supabase = createClient();
  const plan = await getCurrentPlan();
  const baseUrl = FASTAPI_BASE_URL;
  const authHeaders = await getDashboardAuthHeaders(plan);
  const headers = {
    ...authHeaders,
    "Content-Type": "application/json",
  };

  // ── Fetch top signals from Supabase as inputs ──────────────────────
  const { data: topSignals } = await supabase
    .from("cultural_signals")
    .select("termo, score, plataforma, raw_data")
    .order("score", { ascending: false })
    .limit(5);

  // ── Run full intelligence pipeline on each signal ──────────────────
  const results: IntelligenceResult[] = [];
  let apiAvailable = false;

  if (topSignals && topSignals.length > 0) {
    const promises = topSignals.slice(0, 3).map(async (sig) => {
      try {
        const momentum = (sig.raw_data?.momentum ?? (sig.score ?? 0) * 100);
        const sentiment = sig.raw_data?.sentiment ?? 0;
        const volume = sig.raw_data?.volume ?? 0;

        const res = await fetch(`${baseUrl}/api/v8/intelligence/full`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            termo: sig.termo,
            momentum: Math.min(100, Math.max(0, momentum)),
            sentiment: Math.min(1, Math.max(-1, sentiment)),
            volume: Math.max(0, volume),
            plataforma: sig.plataforma ?? "unknown",
          }),
          next: { revalidate: 60 },
        });

        if (res.ok) {
          const json = await res.json();
          apiAvailable = true;
          return json.data as IntelligenceResult;
        }
      } catch { /* skip signal */ }
      return null;
    });

    const settled = await Promise.allSettled(promises);
    for (const s of settled) {
      if (s.status === "fulfilled" && s.value) results.push(s.value);
    }
  }

  // ── Aggregate insights ─────────────────────────────────────────────
  const vulnerabilities = results.map(r => r.vulnerability).filter(Boolean);
  const alerts = results.flatMap(r => {
    const a = r.cultural_alerts;
    return Array.isArray(a?.alerts) ? a.alerts : [];
  });
  const actions = results.map(r => r.strategic_action).filter(Boolean);
  const scenarios = results.map(r => r.scenarios).filter(Boolean);
  const opportunities = results.flatMap(r => {
    const o = r.opportunities;
    return Array.isArray(o?.opportunities) ? o.opportunities : [];
  });

  const avgVulnerability = vulnerabilities.length > 0
    ? vulnerabilities.reduce((a, v) => a + (v.vulnerability_score ?? v.score ?? 0), 0) / vulnerabilities.length
    : 0;

  const criticalAlerts = alerts.filter(a => a.severity === "critical" || a.level === "critical").length;
  const warningAlerts = alerts.filter(a => a.severity === "warning" || a.level === "warning").length;

  const exportData: ExportData = {
    title: "Inteligência Cultural",
    brandName: results[0]?.signal?.termo ?? "Sua Marca",
    vulnerability: avgVulnerability,
    actions,
    scenarios,
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🛡️ Inteligência Cultural</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Blindagem, Cenários & Oportunidades · 5 engines reais analisando {results.length} sinais
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${apiAvailable ? "bg-green-400" : "bg-red-400"} animate-pulse`} />
          <span className="text-xs text-gray-400">
            {apiAvailable ? `Pipeline ativo · ${results.length} análises` : "API offline"}
          </span>
        </div>
      </div>

      <PlanGate required="pro" current={plan}>
        <ExportDataPublisher data={exportData} />
        {/* KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <KpiCard label="Vulnerabilidade" value={`${(avgVulnerability * 100).toFixed(0)}%`}
                   icon={avgVulnerability > 0.6 ? "🔴" : avgVulnerability > 0.3 ? "🟡" : "🟢"} color="red" />
          <KpiCard label="Alertas críticos" value={String(criticalAlerts)} icon="🚨" color="red" />
          <KpiCard label="Avisos" value={String(warningAlerts)} icon="⚠️" color="amber" />
          <KpiCard label="Oportunidades" value={String(opportunities.length)} icon="💎" color="green" />
          <KpiCard label="Cenários" value={String(scenarios.length * 3)} icon="🔮" color="violet" />
        </div>

        {/* ── NEW SECTION: Brazilian Cultural Twin (V9.1) ───────────────── */}
        <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm mt-8">
          <BrazilianCulturalTwin 
            brandName={results[0]?.signal?.termo ?? "Sua Marca"} 
            segment={results[0]?.signal?.segmento ?? "Geral"} 
          />
        </section>

        {/* ── NEW SECTION: Real-time Strategic Shield (V8.5) ───────────── */}
        <section className="mt-8">
          <SectionHeader 
            title="🛡️ Cultural Shield & Recomendações Críticas" 
            subtitle="Blindagem de marca contra crises emergentes — V8.5 Engine" 
          />
          <CulturalShield 
            shield={vulnerabilities[0] as any} 
            alerts={alerts as any[]} 
            actions={actions as any[]} 
          />
        </section>

        {/* ── SECTION 2: Cenários Preditivos & Oportunidades ─────────────── */}
        <section className="mt-8">
          <SectionHeader title="🔮 Cenários Preditivos & Futuros Culturais" subtitle="ScenarioEngine — Projeção de percepção de 30-180 dias" />
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-8">
              <FuturesTimeline scenarios={scenarios[0]?.scenarios ?? []} />
            </div>

            <div className="lg:col-span-4 space-y-6">
              <h3 className="text-sm font-bold text-gray-800 uppercase tracking-widest mb-4 flex items-center gap-2">
                💎 Oportunidades de Vanguarda
              </h3>
              {opportunities.slice(0, 4).map((o, i) => (
                <div key={i} className="bg-emerald-50 border border-emerald-100/50 p-5 rounded-3xl shadow-sm hover:translate-x-1 transition-transform cursor-pointer group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-black uppercase text-emerald-600 bg-white px-2 py-0.5 rounded-full border border-emerald-200">
                      Impacto {o.impact || "High"}
                    </span>
                    <span className="text-xl">✨</span>
                  </div>
                  <h4 className="text-sm font-bold text-gray-800 group-hover:text-emerald-700">{o.title}</h4>
                  <p className="text-xs text-gray-500 mt-1 mb-3 line-clamp-2">{o.description}</p>
                  <p className="text-[10px] font-bold text-emerald-600 uppercase">Ação: {o.action}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── SECTION 3: Detalhamento Técnico dos Sinais ───────────────── */}
        <SectionHeader title="🔍 Detalhamento Analítico" subtitle="Monitoramento em tempo real dos sinais individuais" />
        <Section title="🔍 Sinais Individuais" subtitle="Dados brutos e análises por sinal">
          {topSignals && topSignals.length > 0 ? (
            <div className="space-y-4">
              {topSignals.map((sig, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <h3 className="text-sm font-bold text-gray-800 mb-3">{sig.termo}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="p-3 rounded-lg border bg-gray-50">
                      <p className="text-xs font-bold text-gray-700 mb-1">Score</p>
                      <p className="text-lg font-semibold text-gray-900">{sig.score.toFixed(2)}</p>
                    </div>
                    <div className="p-3 rounded-lg border bg-gray-50">
                      <p className="text-xs font-bold text-gray-700 mb-1">Plataforma</p>
                      <p className="text-sm text-gray-800">{sig.plataforma}</p>
                    </div>
                    <div className="p-3 rounded-lg border bg-gray-50">
                      <p className="text-xs font-bold text-gray-700 mb-1">Momento</p>
                      <p className="text-sm text-gray-800">{sig.raw_data?.momentum ?? "N/A"}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs font-bold text-gray-700 mb-1">Dados Brutos</p>
                    <pre className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg overflow-auto">
                      {JSON.stringify(sig.raw_data, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState />
          )}
        </Section>
      </PlanGate>
    </div>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────

function Section({ title, subtitle, children }: {
  title: string; subtitle: string; children: React.ReactNode;
}) {
  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
      <p className="text-xs text-gray-400 mb-3">{subtitle}</p>
      {children}
    </div>
  );
}

function VulnBadge({ score }: { score: number }) {
  const label = score > 0.6 ? "Alto risco" : score > 0.3 ? "Moderado" : "Baixo risco";
  const cls = score > 0.6 ? "bg-red-100 text-red-700" :
              score > 0.3 ? "bg-amber-100 text-amber-700" :
                            "bg-green-100 text-green-700";
  return <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${cls}`}>{label}</span>;
}

function EmptyState() {
  return (
    <div className="text-center py-8 bg-gray-50 rounded-xl border border-gray-100">
      <p className="text-2xl mb-1">📭</p>
      <p className="text-xs text-gray-400">Sem dados. Inicie o FastAPI + Worker para análise em tempo real.</p>
    </div>
  );
}

function KpiCard({ label, value, icon, color }: {
  label: string; value: string; icon: string;
  color: "red" | "amber" | "green" | "violet";
}) {
  const colors = {
    red:    "bg-red-50 text-red-700 border-red-100",
    amber:  "bg-amber-50 text-amber-700 border-amber-100",
    green:  "bg-green-50 text-green-700 border-green-100",
    violet: "bg-violet-50 text-violet-700 border-violet-100",
  };
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <p className="text-2xl">{icon}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs opacity-70 mt-0.5">{label}</p>
    </div>
  );
}

function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
      <p className="text-xs text-gray-400">{subtitle}</p>
    </div>
  );
}
