import PlanGate from "@/components/auth/PlanGate";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getCurrentPlan } from "@/lib/plan";
import { getDashboardAuthHeaders } from "@/lib/dashboard";
import { TrendingUp, Search, User, Activity, Zap, Share2 } from "lucide-react";

export const revalidate = 120; // ISR 2 min

/**
 * Tendências & Sinais Fracos — Server Component.
 *
 * Consome dados REAIS do pipeline via FastAPI:
 *   GET /api/v8/dashboard/insights      → dashboard_insights (dashboard_insights.py)
 *
 * Usa rota única para evitar duplicação de chamadas e remove qualquer fallback simulado.
 */

interface TrendItem {
  name: string;
  category: string;
  description: string;
  momentum: number;
  growth: string;
}

interface WeakSignalItem {
  title: string;
  description: string;
  strength: number;
  source: string;
  actionable: boolean;
  action: string;
}

interface ProfileItem {
  name: string;
  description: string;
  demographics: string;
  behaviors: string;
  relevance: number;
  growth: string;
  size: string;
  opportunity: string;
  connected_circles: string[];
}

interface RelationshipItem {
  circle_1: string;
  circle_2: string;
  strength: number;
  type: string;
  description: string;
  opportunity: string;
  risk?: string;
}

export default async function TrendsPage({ searchParams }: { searchParams?: { projectId?: string } }) {
  const plan = await getCurrentPlan();
  const projectId = searchParams?.projectId;
  const headers = await getDashboardAuthHeaders(plan);
  const baseUrl = FASTAPI_BASE_URL;
  const planParam = ["enterprise", "executive", "pro", "free"].includes(plan) ? plan : "free";

  let trends: TrendItem[] = [];
  let weakSignals: WeakSignalItem[] = [];
  let profiles: ProfileItem[] = [];
  let relationships: RelationshipItem[] = [];
  let hasRealData = false;
  let errorMessage: string | null = null;

  try {
    const projectQuery = projectId ? `&project_id=${encodeURIComponent(projectId)}` : "";
    const response = await fetch(
      `${baseUrl}/api/v8/dashboard/insights?plan=${planParam}&count=200&realtime=true${projectQuery}`,
      {
        headers,
        next: { revalidate: 120 },
      }
    );

    if (!response.ok) {
      throw new Error(`FastAPI error ${response.status}`);
    }

    const json = await response.json();
    trends = Array.isArray(json.emerging_trends) ? json.emerging_trends : [];
    weakSignals = Array.isArray(json.weak_signals) ? json.weak_signals : [];
    profiles = Array.isArray(json.emerging_profiles) ? json.emerging_profiles : [];
    relationships = Array.isArray(json.cultural_relationships) ? json.cultural_relationships : [];
    hasRealData = trends.length > 0 || weakSignals.length > 0 || profiles.length > 0 || relationships.length > 0;
  } catch (error) {
    errorMessage = (error as Error).message;
    trends = [];
    weakSignals = [];
    profiles = [];
    relationships = [];
  }

  return (
    <div className="p-8 space-y-10 max-w-7xl mx-auto bg-[#FDFDFF] min-h-screen">
      {/* Header Premium (v10.1) */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-10 bg-violet-600 rounded-full" />
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">
              Tendências & Descobertas (APIs)
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <div className={`px-4 py-1.5 rounded-full flex items-center gap-2 border ${hasRealData ? "bg-emerald-50 border-emerald-100 text-emerald-700" : "bg-amber-50 border-amber-100 text-amber-900"}`}>
              <span className={`w-2 h-2 rounded-full ${hasRealData ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
              <span className="text-[10px] font-black uppercase tracking-widest leading-none">
                {hasRealData ? "Live Pipeline Active" : "Waiting for Worker"}
              </span>
            </div>
            <button className="h-10 px-6 bg-gray-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg shadow-black/10">
              Exportar Insights
            </button>
          </div>
        </div>
        <p className="text-gray-400 font-medium italic pl-5 max-w-3xl">
          Descobertas derivadas em tempo real via EnrichedDataReader (Redis) processadas por 18 engines de análise.
          Foco em sinais fracos e hibridismo cultural.
        </p>
      </div>

      <PlanGate 
        required="free" 
        current={plan} 
      >
        {/* KPI Cards (v10.2) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <TrendKpiCard label="Emergentes" value={String(trends.length)} desc="Novas tendências" icon={<TrendingUp className="text-violet-500" />} />
          <TrendKpiCard label="Sinais Fracos" value={String(weakSignals.length)} desc="Descobertas latentes" icon={<Search className="text-amber-500" />} />
          <TrendKpiCard label="Perfis" value={String(profiles.length)} desc="Novos clusters" icon={<User className="text-emerald-500" />} />
          <TrendKpiCard label="Relações" value={String(relationships.length)} desc="Conexões culturais" icon={<Share2 className="text-sky-500" />} />
        </div>
        {errorMessage ? (
          <div className="rounded-3xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Erro ao carregar dados do backend: {errorMessage}
          </div>
        ) : null}

        {/* ── SECTION 0: Emerging Profiles Scatter (V9.9 - NOVO) ── */}
        <div className="mt-8 bg-slate-100/50 rounded-2xl p-6 border border-slate-200 shadow-inner">
          <div className="mb-4">
             <h2 className="text-lg font-black text-slate-800 uppercase tracking-tighter flex items-center gap-2">
                🛸 Radar de Emergência (X: Tamanho | Y: Score)
             </h2>
             <p className="text-[10px] text-slate-500 font-bold uppercase">Mapeamento Biográfico vs. Densidade de Amostragem</p>
          </div>
          
          <div className="relative aspect-[21/9] bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
             {/* Grid Lines */}
             <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 opacity-[0.05] pointer-events-none">
                {[...Array(16)].map((_, i) => <div key={i} className="border border-slate-900"/>)}
             </div>

             {/* Y-Axis Label */}
             <div className="absolute left-2 top-1/2 -rotate-90 origin-left text-[8px] font-black text-slate-400 uppercase tracking-widest">
                Score de Emergência (Cultural Fit)
             </div>

             {/* Scatter Dots */}
             <div className="absolute inset-8">
                {profiles.map((p, i) => {
                  const sizeVal = p.size?.toLowerCase().includes('pequeno') ? 20 : (p.size?.toLowerCase().includes('medio') ? 50 : 80);
                  const growthVal = p.relevance; // Usando relevância como proxy de emergência para o gráfico
                  const isVerified = (p as any).is_verified || p.opportunity?.includes('Confirmado');
                  
                  return (
                    <div 
                      key={i}
                      className={`absolute cursor-pointer transition-all hover:scale-125 group shadow-lg rounded-full flex items-center justify-center border-2 ${
                        isVerified ? 'bg-violet-600 border-violet-400 shadow-violet-200' : 'bg-slate-400 border-slate-300'
                      }`}
                      style={{ 
                        left: `${sizeVal}%`, 
                        bottom: `${growthVal}%`, 
                        width: `${12 + (p.relevance / 10)}px`, 
                        height: `${12 + (p.relevance / 10)}px` 
                      }}
                      title={`${p.name}: ${p.size} / ${p.relevance}`}
                    >
                      <div className="opacity-0 group-hover:opacity-100 absolute bottom-full mb-2 bg-slate-900 text-white text-[9px] px-2 py-1 rounded font-bold whitespace-nowrap z-50 shadow-xl pointer-events-none uppercase">
                        {p.name} <br/> 
                        <span className="text-slate-400">Score: {p.relevance}</span> | 
                        <span className={isVerified ? 'text-green-400' : 'text-amber-400'}> {isVerified ? '✓ Verificado' : '⏳ Experimental'}</span>
                      </div>
                    </div>
                  );
                })}
             </div>
             
             {/* X-Axis Label */}
             <div className="absolute bottom-1 w-full text-center text-[8px] font-black text-slate-400 uppercase tracking-widest">
                Tamanho do Segmento (Clustering Density)
             </div>
          </div>
        </div>

        {/* ── SECTION 1: Emerging Trends ────────────────────────────── */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">📈 Tendências Emergentes</h2>
          {trends.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {trends.map((t, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-bold text-gray-800">{t.name}</h3>
                      <span className="text-xs text-violet-600 font-medium">{t.category}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        t.growth === "🚀 Explosivo" ? "bg-red-100 text-red-700" :
                        t.growth === "📈 Alto" ? "bg-amber-100 text-amber-700" :
                        "bg-green-100 text-green-700"
                      }`}>{t.growth}</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{t.description}</p>
                  <div className="flex items-center gap-2 mt-3">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-violet-500 rounded-full transition-all"
                           style={{ width: `${Math.min(100, t.momentum)}%` }} />
                    </div>
                    <span className="text-xs font-mono text-gray-500 w-12 text-right">
                      {t.momentum.toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="Nenhuma tendência detectada. Execute o Worker para popular dados." />
          )}
        </div>

        {/* ── SECTION 2: Weak Signals ───────────────────────────────── */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">🔍 Sinais Fracos</h2>
          {weakSignals.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {weakSignals.map((ws, i) => {
                // 🧪 V9.9: Feedback Visual de Confiabilidade
                const isLowReliability = (ws as any).reliability === "BAIXA" || ws.description.includes("[EXPERIMENTAL]");
                
                return (
                  <div key={i} className={`bg-white rounded-xl border shadow-sm p-5 transition-all ${
                    isLowReliability 
                      ? "border-amber-200 bg-amber-50/20 ring-1 ring-amber-100" 
                      : "border-gray-100"
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex flex-col">
                        <h3 className="text-sm font-bold text-gray-800">{ws.title}</h3>
                        {isLowReliability && (
                          <span className="text-[9px] font-black text-amber-600 uppercase tracking-tighter bg-amber-100 px-1.5 py-0.5 rounded w-fit mt-1">
                            ⚠️ [CONTEÚDO EXPERIMENTAL / SIMULADO]
                          </span>
                        )}
                      </div>
                      {ws.actionable && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">Acionável</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{ws.description}</p>
                    <div className="flex items-center gap-3 mt-3 text-xs text-gray-400">
                      <span>📡 {ws.source}</span>
                      <span>💪 Força: {(ws.strength * 100).toFixed(0)}%</span>
                    </div>
                    {ws.action && (
                      <div className="mt-2 px-3 py-2 bg-violet-50 rounded-lg">
                        <p className="text-xs text-violet-700"><strong>Ação:</strong> {ws.action}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState message="Nenhum sinal fraco detectado. Sinais com baixo momentum e alta velocidade aparecem aqui." />
          )}
        </div>

        {/* ── SECTION 3: Emerging Profiles ──────────────────────────── */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">👤 Perfis Emergentes</h2>
          {profiles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {profiles.map((p, i) => (
                <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <h3 className="text-sm font-bold text-gray-800">{p.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">{p.description}</p>
                  <div className="mt-3 space-y-1.5 text-xs">
                    <InfoRow label="Demografia" value={p.demographics} />
                    <InfoRow label="Comportamento" value={p.behaviors} />
                    <InfoRow label="Tamanho" value={p.size} />
                    <InfoRow label="Crescimento" value={p.growth} />
                  </div>
                  {p.connected_circles && p.connected_circles.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {p.connected_circles.slice(0, 4).map(c => (
                        <span key={c} className="px-2 py-0.5 bg-violet-50 text-violet-700 rounded text-xs">{c}</span>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-50">
                    <span className="text-xs text-gray-400">Relevância: {p.relevance}/100</span>
                    <span className="text-xs text-amber-600">{p.opportunity}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
               {[1,2,3].map(i => (
                 <div key={i} className="bg-white rounded-xl border border-gray-50 p-5 opacity-60">
                    <div className="h-4 w-32 bg-gray-100 rounded mb-2 animate-pulse" />
                    <div className="h-3 w-full bg-gray-50 rounded mb-4" />
                    <div className="space-y-2">
                       <div className="h-2 w-full bg-gray-50 rounded" />
                       <div className="h-2 w-2/3 bg-gray-50 rounded" />
                    </div>
                 </div>
               ))}
            </div>
          )}
        </div>

        {/* ── SECTION 4: Cultural Relationships ──────────────────────── */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">🔗 Relações Culturais</h2>
          {relationships.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {relationships.map((rel, i) => (
                <div key={`${rel.circle_1}-${rel.circle_2}-${i}`} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <h3 className="text-sm font-bold text-gray-800">{rel.circle_1} → {rel.circle_2}</h3>
                      <p className="text-xs text-slate-500 mt-1">{rel.type}</p>
                    </div>
                    <span className="text-xs font-semibold text-slate-700">Força {rel.strength}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">{rel.description}</p>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
                    <span className="px-2 py-1 bg-slate-100 rounded-full text-slate-600">{rel.opportunity}</span>
                    {rel.risk && <span className="px-2 py-1 bg-amber-100 rounded-full text-amber-700">Risco: {rel.risk}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="Nenhuma relação cultural disponível no momento." />
          )}
        </div>
      </PlanGate>
    </div>
  );
}

function TrendKpiCard({ label, value, desc, icon }: { label: string, value: string, desc: string, icon: React.ReactNode }) {
  return (
    <div className="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:border-violet-100 transition-all hover:shadow-md">
       <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center group-hover:bg-violet-50 transition-colors">
          {icon}
       </div>
       <div>
         <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-0.5">{label}</span>
         <span className="text-2xl font-black text-gray-900 leading-none">{value}</span>
         <span className="text-[9px] font-bold text-gray-400 block mt-1 uppercase tracking-tighter">{desc}</span>
       </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-12 bg-gray-50 rounded-xl border border-gray-100">
      <p className="text-3xl mb-2">📭</p>
      <p className="text-sm text-gray-400">{message}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start gap-2">
      <span className="text-gray-400 w-24 shrink-0">{label}:</span>
      <span className="text-gray-600">{value}</span>
    </div>
  );
}
