import { createClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import AnalyzeButton from "./AnalyzeButton";
import Link from "next/link";

export const revalidate = 0;

interface Props {
  params: Promise<{ id: string }>;
}

interface Project {
  id: string;
  name: string;
  brand: string;
  keywords: string[];
  segment: string;
  objective: string;
  regions: string[];
  audiences: string[];
  circles: string[];
  period_days: number;
  status: string;
  signals_count: number;
  last_analysis_at: string | null;
  analysis_data: any;
  created_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  draft:      { label: "Rascunho",   color: "bg-gray-100 text-gray-600",     icon: "📝" },
  collecting: { label: "Coletando…", color: "bg-blue-100 text-blue-700",     icon: "🔄" },
  analyzing:  { label: "Analisando…",color: "bg-violet-100 text-violet-700", icon: "🧠" },
  ready:      { label: "Pronto",     color: "bg-green-100 text-green-700",   icon: "✅" },
  error:      { label: "Erro",       color: "bg-red-100 text-red-700",       icon: "❌" },
};

export default async function ProjectDetailPage({ params }: Props) {
  const { id } = await params;
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: project, error } = await supabase
    .from("projects")
    .select("*")
    .eq("id", id)
    .single();

  if (error || !project) notFound();

  const p = project as Project;
  const projectQuery = `?projectId=${encodeURIComponent(p.id)}`;
  const st = STATUS_CONFIG[p.status] ?? STATUS_CONFIG.draft;
  const analysis = p.analysis_data;
  const brandAnalysis = analysis?.brand_analysis;
  const businessInsights = analysis?.business_insights;
  const businessInsightItems = businessInsights?.insights ?? [];
  const businessInsightsSummary = businessInsights?.summary;
  const intelligence = analysis?.intelligence ?? [];

  // Fetch signals matching this project's keywords from Supabase
  let matchingSignals: any[] = [];
  if (p.keywords.length > 0) {
    // Use OR filter for any keyword match
    const filters = p.keywords.map((kw) => `termo.ilike.%${kw}%`).join(",");
    const { data } = await supabase
      .from("cultural_signals")
      .select("id, termo, score, plataforma, circulo, created_at")
      .or(filters)
      .order("created_at", { ascending: false })
      .limit(20);
    matchingSignals = data ?? [];
  }

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Breadcrumb + Header */}
      <div>
        <Link href="/dashboard/projects" className="text-xs text-gray-400 hover:text-violet-600 transition">
          ← Projetos
        </Link>
        <div className="flex items-center justify-between mt-2">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{p.name}</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              🏷️ {p.brand} · {p.segment} · {p.period_days} dias
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs font-semibold px-3 py-1 rounded-full ${st.color}`}>
              {st.icon} {st.label}
            </span>
            <AnalyzeButton projectId={p.id} status={p.status} />
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href={`/dashboard/insights${projectQuery}`}
            className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-semibold hover:bg-violet-700 transition"
          >
            Ver insights do projeto
          </Link>
          <Link
            href={`/dashboard/trends${projectQuery}`}
            className="px-4 py-2 rounded-xl bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition"
          >
            Ver tendências do projeto
          </Link>
          <Link
            href={`/dashboard/emerging-profiles${projectQuery}`}
            className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition"
          >
            Ver perfis do projeto
          </Link>
        </div>
      </div>

      {/* Briefing summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Keywords</h3>
          <div className="flex flex-wrap gap-1">
            {p.keywords.map((kw, i) => (
              <span key={i} className="text-xs bg-violet-50 text-violet-600 px-2 py-0.5 rounded-full">
                {kw}
              </span>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Configuração</h3>
          <p className="text-xs text-gray-600"><strong>Objetivo:</strong> {p.objective}</p>
          <p className="text-xs text-gray-600 mt-1"><strong>Regiões:</strong> {p.regions.join(", ")}</p>
          <p className="text-xs text-gray-600 mt-1"><strong>Audiências:</strong> {p.audiences.join(", ")}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Métricas</h3>
          <div className="space-y-2">
            <Metric label="Sinais coletados" value={String(p.signals_count)} />
            <Metric label="Círculos" value={String(p.circles.length || 16)} />
            <Metric label="Última análise" value={p.last_analysis_at ? new Date(p.last_analysis_at).toLocaleDateString("pt-BR") : "—"} />
          </div>
        </div>
      </div>

      {/* ═══ KPI Row from Analysis ═══ */}
      {brandAnalysis && (
        <>
          <SectionTitle title="📊 Resultado da Análise Cultural" />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <KpiCard label="Cultural Score" value={(brandAnalysis.cultural_score ?? brandAnalysis.data?.cultural_score ?? 0).toFixed(2)} icon="🎯" color="violet" />
            <KpiCard label="Autenticidade" value={(brandAnalysis.authenticity_score ?? brandAnalysis.data?.authenticity_score ?? 0).toFixed(2)} icon="✨" color="amber" />
            <KpiCard label="Círculos ativos" value={String(brandAnalysis.circles_count ?? brandAnalysis.data?.top_circles?.length ?? 0)} icon="🔵" color="blue" />
            <KpiCard label="Alma Brasileira" value={(brandAnalysis.alma_score ?? brandAnalysis.data?.alma_brasileira?.score_geral ?? 0).toFixed(2)} icon="🇧🇷" color="green" />
          </div>
        </>
      )}

      {businessInsights?.error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <p className="font-semibold">Erro ao carregar insights de negócio</p>
          <p>{String(businessInsights.error)}</p>
        </div>
      )}

      {businessInsightItems.length > 0 && (
        <>
          <SectionTitle title="💡 Insights de Negócio" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <InfoCard label="Total de insights" value={String(businessInsightItems.length)} />
            <InfoCard label="Confiança média" value={`${(businessInsightsSummary?.avg_confidence ?? 0).toFixed(2)}`} />
            <InfoCard label="Alinhamento médio" value={`${(businessInsightsSummary?.average_alignment ?? 0).toFixed(2)}`} />
          </div>

          <div className="grid grid-cols-1 gap-4">
            {businessInsightItems.slice(0, 3).map((item: any, index: number) => (
              <div key={`insight-${index}`} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                <p className="text-xs text-gray-500 uppercase tracking-[0.2em] mb-2">Insight {index + 1}</p>
                <p className="text-sm font-semibold text-gray-900 mb-2">{item.text}</p>
                <div className="text-xs text-gray-600 space-y-1">
                  <p><strong>Previsão:</strong> {item.prediction}</p>
                  <p><strong>Confiança:</strong> {item.confidence?.toFixed?.(2) ?? item.confidence}</p>
                  <p><strong>Alinhamento:</strong> {(item.business_alignment?.alignment_score ?? 0).toFixed(2)}</p>
                  <p><strong>Oportunidade:</strong> {(item.opportunity_score ?? 0).toFixed(2)}</p>
                  <p><strong>Risco:</strong> {(item.risk_score ?? 0).toFixed(2)}</p>
                  <p><strong>Recomendação:</strong> {item.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* ═══ Intelligence Results ═══ */}
      {intelligence.length > 0 && (
        <>
          <SectionTitle title="🛡️ Inteligência Cultural" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {intelligence.map((item: any, i: number) => {
              const vuln = item?.vulnerability;
              const alerts = item?.alerts ?? [];
              const actions = item?.actions ?? [];
              const scenarios = item?.scenarios ?? [];
              const opps = item?.opportunities ?? [];
              return (
                <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <h3 className="text-sm font-bold text-gray-800 mb-2">
                    Keyword: <span className="text-violet-600">{p.keywords[i] ?? `#${i + 1}`}</span>
                  </h3>

                  {vuln && (
                    <div className="mb-2">
                      <span className="text-xs text-gray-500">Vulnerabilidade:</span>
                      <span className={`ml-2 text-xs font-bold ${
                        (vuln.risk_level ?? vuln.nivel_risco) === "alto" ? "text-red-600" :
                        (vuln.risk_level ?? vuln.nivel_risco) === "medio" ? "text-amber-600" : "text-green-600"
                      }`}>
                        {vuln.risk_level ?? vuln.nivel_risco ?? "—"}
                      </span>
                    </div>
                  )}

                  {alerts.length > 0 && (
                    <div className="mb-2">
                      <span className="text-xs text-gray-500">{alerts.length} alertas</span>
                      <div className="mt-1 space-y-0.5">
                        {alerts.slice(0, 2).map((a: any, j: number) => (
                          <p key={j} className="text-xs text-red-600">⚠️ {a.message ?? a.mensagem ?? JSON.stringify(a).slice(0, 80)}</p>
                        ))}
                      </div>
                    </div>
                  )}

                  {opps.length > 0 && (
                    <div>
                      <span className="text-xs text-gray-500">{opps.length} oportunidades</span>
                      <div className="mt-1 space-y-0.5">
                        {opps.slice(0, 2).map((o: any, j: number) => (
                          <p key={j} className="text-xs text-green-600">💡 {o.description ?? o.descricao ?? JSON.stringify(o).slice(0, 80)}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* ═══ Matching Signals from Supabase ═══ */}
      <SectionTitle title={`📡 Sinais Relacionados (${matchingSignals.length})`} />
      {matchingSignals.length > 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500">
              <tr>
                <th className="text-left px-4 py-2">Termo</th>
                <th className="text-left px-4 py-2">Plataforma</th>
                <th className="text-left px-4 py-2">Círculo</th>
                <th className="text-right px-4 py-2">Score</th>
                <th className="text-right px-4 py-2">Data</th>
              </tr>
            </thead>
            <tbody>
              {matchingSignals.map((s) => (
                <tr key={s.id} className="border-t border-gray-50 hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium text-gray-800">{s.termo}</td>
                  <td className="px-4 py-2 text-gray-500">{s.plataforma}</td>
                  <td className="px-4 py-2 text-gray-500">{s.circulo ?? "—"}</td>
                  <td className="px-4 py-2 text-right text-violet-600 font-semibold">{(s.score ?? 0).toFixed(2)}</td>
                  <td className="px-4 py-2 text-right text-gray-400 text-xs">
                    {new Date(s.created_at).toLocaleDateString("pt-BR")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-8 bg-gray-50 rounded-xl border border-gray-100">
          <p className="text-2xl mb-1">📭</p>
          <p className="text-xs text-gray-400">
            {p.status === "draft"
              ? "Clique em \"Analisar\" para iniciar a coleta de dados."
              : "Nenhum sinal encontrado para as keywords deste projeto."}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────

function SectionTitle({ title }: { title: string }) {
  return <h2 className="text-lg font-semibold text-gray-800 mt-4">{title}</h2>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-gray-500">{label}</span>
      <span className="text-xs font-bold text-gray-700">{value}</span>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-[0.25em] text-gray-400">{label}</p>
      <p className="mt-3 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function KpiCard({ label, value, icon, color }: { label: string; value: string; icon: string; color: string }) {
  const colors: Record<string, string> = {
    violet: "border-violet-100 bg-violet-50 text-violet-700",
    amber:  "border-amber-100 bg-amber-50 text-amber-700",
    blue:   "border-blue-100 bg-blue-50 text-blue-700",
    green:  "border-green-100 bg-green-50 text-green-700",
  };
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <p className="text-lg">{icon}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs opacity-70">{label}</p>
    </div>
  );
}
