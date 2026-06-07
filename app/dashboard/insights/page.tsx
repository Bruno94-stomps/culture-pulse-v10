import PlanGate from "@/components/auth/PlanGate";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getCurrentPlan } from "@/lib/plan";
import { getDashboardAuthHeaders } from "@/lib/dashboard";
import { TrendingUp, Zap, User, Share2, Activity } from "lucide-react";

export const revalidate = 120;

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
  warnings: string;
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

import { normalizePlan, type PlanTier } from "@/lib/plan";

async function fetchDashboardInsights(plan: PlanTier, projectId?: string) {
  const planParam: PlanTier = normalizePlan(plan);
  const headers = await getDashboardAuthHeaders(planParam);
  const baseUrl = FASTAPI_BASE_URL;
  const projectQuery = projectId ? `&project_id=${encodeURIComponent(projectId)}` : "";

  const response = await fetch(
    `${baseUrl}/api/v8/dashboard/insights?plan=${planParam}&count=100&realtime=true${projectQuery}`,
    {
      headers,
      next: { revalidate: 120 },
    } as any
  );

  if (!response.ok) {
    return {
      trends: [],
      weakSignals: [],
      profiles: [],
      relationships: [],
    };
  }

  const json = await response.json();

  return {
    trends: Array.isArray(json.emerging_trends) ? json.emerging_trends : [],
    weakSignals: Array.isArray(json.weak_signals) ? json.weak_signals : [],
    profiles: Array.isArray(json.emerging_profiles) ? json.emerging_profiles : [],
    relationships: Array.isArray(json.cultural_relationships) ? json.cultural_relationships : [],
  };
}

export default async function InsightsPage({ searchParams }: { searchParams?: { projectId?: string } }) {
  const plan = await getCurrentPlan();
  const projectId = searchParams?.projectId;
  const { trends, weakSignals, profiles, relationships } = await fetchDashboardInsights(plan, projectId);

  return (
    <PlanGate required="free" current={plan}>
      <div className="p-8 space-y-10 max-w-7xl mx-auto bg-[#FDFDFF] min-h-screen">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-10 bg-violet-600 rounded-full" />
              <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                Insights de Dashboard - FastAPI
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-4 py-1.5 rounded-full flex items-center gap-2 border bg-emerald-50 border-emerald-100 text-emerald-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest leading-none">
                  Pipeline ativo
                </span>
              </div>
            </div>
          </div>
          <p className="text-gray-400 font-medium italic pl-5 max-w-3xl">
            Esta página consome todos os endpoints de dashboard do backend FastAPI:
            trends, weak-signals, profiles e relationships.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Tendências</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{trends.length}</p>
              </div>
              <TrendingUp className="text-violet-500 w-8 h-8" />
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Sinais Fracos</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{weakSignals.length}</p>
              </div>
              <Zap className="text-amber-500 w-8 h-8" />
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Perfis</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{profiles.length}</p>
              </div>
              <User className="text-emerald-500 w-8 h-8" />
            </div>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Relações</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{relationships.length}</p>
              </div>
              <Share2 className="text-sky-500 w-8 h-8" />
            </div>
          </div>
        </div>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card title="Principais Tendências" icon={<TrendingUp className="w-5 h-5 text-violet-500" />}>
            {trends.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhuma tendência retornada.</p>
            ) : (
              <ul className="space-y-3">
                {trends.slice(0, 5).map((item: TrendItem, index: number) => (
                  <li key={`${item.name}-${index}`} className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                    <p className="font-semibold text-slate-900">{item.name}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                    <div className="mt-2 flex items-center gap-2 text-[13px] text-slate-600">
                      <span>{item.category}</span>
                      <span className="rounded-full bg-white px-2 py-0.5 border border-slate-200">{item.growth}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Sinais Fracos" icon={<Zap className="w-5 h-5 text-amber-500" />}>
            {weakSignals.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhum sinal fraco retornado.</p>
            ) : (
              <ul className="space-y-3">
                {weakSignals.slice(0, 5).map((item: WeakSignalItem, index: number) => (
                  <li key={`${item.title}-${index}`} className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                    <p className="font-semibold text-slate-900">{item.title}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                    <div className="mt-2 text-[13px] text-slate-600">Fonte: {item.source}</div>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card title="Perfis Emergentes" icon={<User className="w-5 h-5 text-emerald-500" />}>
            {profiles.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhum perfil retornado.</p>
            ) : (
              <ul className="space-y-3">
                {profiles.slice(0, 4).map((item: ProfileItem, index: number) => (
                  <li key={`${item.name}-${index}`} className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                    <p className="font-semibold text-slate-900">{item.name}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Relações Culturais" icon={<Activity className="w-5 h-5 text-sky-500" />}>
            {relationships.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhuma relação retornada.</p>
            ) : (
              <ul className="space-y-3">
                {relationships.slice(0, 5).map((item: RelationshipItem, index: number) => (
                  <li key={`${item.circle_1}-${item.circle_2}-${index}`} className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                    <p className="font-semibold text-slate-900">{item.circle_1} ↔ {item.circle_2}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                    <div className="mt-2 flex flex-wrap gap-2 text-[13px] text-slate-600">
                      <span className="rounded-full bg-white px-2 py-0.5 border border-slate-200">{item.type}</span>
                      <span className="rounded-full bg-white px-2 py-0.5 border border-slate-200">Força {item.strength}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </section>
      </div>
    </PlanGate>
  );
}

function Card({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-400">{title}</p>
        </div>
        <div className="rounded-2xl bg-slate-100 p-3 text-slate-700">{icon}</div>
      </div>
      {children}
    </div>
  );
}
