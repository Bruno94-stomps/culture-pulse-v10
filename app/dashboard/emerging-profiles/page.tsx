import PlanGate from "@/components/auth/PlanGate";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getCurrentPlan } from "@/lib/plan";
import { Activity, ArrowUpRight, Sparkles, User2, Zap } from "lucide-react";

export const revalidate = 120;

interface ProfileItem {
  name: string;
  description: string;
  relevance: number;
  growth: string;
  behaviors: string[];
  connected_circles: string[];
  is_omnidata: boolean;
}

function parsePlan(plan: string) {
  return plan === "enterprise" || plan === "executive" || plan === "pro" || plan === "free"
    ? plan
    : "free";
}

function normalizeProfile(item: any): ProfileItem {
  return {
    name: item.name || "Perfil emergente",
    description: item.description || item.summary || "Sem descrição disponível.",
    relevance: typeof item.relevance === "number" ? item.relevance : 0,
    growth: item.growth || "+0%",
    behaviors: Array.isArray(item.behaviors) ? item.behaviors : [String(item.behaviors || "-")],
    connected_circles: Array.isArray(item.connected_circles) ? item.connected_circles : [],
    is_omnidata: Boolean(item.is_omnidata),
  };
}

async function fetchEmergingProfiles(plan: string, projectId?: string) {
  const planParam = parsePlan(plan);
  const projectQuery = projectId ? `&project_id=${encodeURIComponent(projectId)}` : "";
  const res = await fetch(
    `${FASTAPI_BASE_URL}/api/v8/dashboard/emerging-profiles?plan=${planParam}&top_n=6${projectQuery}`,
    {
      next: { revalidate: 120 },
    } as any
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch emerging profiles: ${res.status}`);
  }

  const data = await res.json();
  return Array.isArray(data.data) ? data.data.map(normalizeProfile) : [];
}

export default async function EmergingProfilesPage({ searchParams }: { searchParams?: { projectId?: string } }) {
  const plan = await getCurrentPlan();
  const projectId = searchParams?.projectId;

  let profiles: ProfileItem[] = [];
  let hasRealData = false;
  let errorMessage: string | null = null;

  try {
    profiles = await fetchEmergingProfiles(plan, projectId);
    hasRealData = profiles.length > 0;
  } catch (error) {
    errorMessage = (error as Error).message;
  }

  return (
    <PlanGate required="pro" current={plan}>
      <div className="min-h-screen bg-slate-50 py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8 space-y-3">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Dashboard de Perfis Emergentes</p>
            <h1 className="text-4xl font-black tracking-tight text-slate-900">Perfis Emergentes</h1>
            <p className="max-w-3xl text-lg text-slate-600">
              Identifica perfis de público emergentes a partir dos dados culturais e apresenta métricas de relevância, crescimento e conectividade.
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-[0.7fr,0.3fr]">
            <section className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <MetricCard icon={<Zap className="text-amber-500" />} label="Fonte de dados" value="Pipeline" />
                <MetricCard icon={<Activity className="text-sky-500" />} label="Plan" value={plan.toUpperCase()} />
              </div>

              {!hasRealData && !errorMessage ? (
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                  Nenhum perfil emergente foi gerado a partir dos dados atuais. Verifique se há sinais culturais disponíveis no Supabase ou se o pipeline está populado.
                </div>
              ) : null}

              {errorMessage ? (
                <AlertBox message={errorMessage} />
              ) : null}

              {!hasRealData && !errorMessage ? (
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                  Nenhum perfil emergente foi gerado a partir dos dados atuais. Verifique se há sinais culturais disponíveis no Supabase ou se o pipeline está populado.
                </div>
              ) : null}

              <div className="grid gap-4 lg:grid-cols-2">
                {profiles.map((profile, index) => (
                  <div key={`${profile.name}-${index}`} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h2 className="text-xl font-bold text-slate-900">{profile.name}</h2>
                        <p className="mt-2 text-sm text-slate-500">{profile.description}</p>
                      </div>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-600">
                        {profile.growth}
                      </span>
                    </div>

                    <div className="mt-5 space-y-3 text-sm text-slate-700">
                      <InfoLine label="Relevância" value={`${profile.relevance.toFixed(1)}%`} />
                      <InfoLine label="Behaviors" value={profile.behaviors.join(" • ")} />
                      <InfoLine label="Círculos conexos" value={profile.connected_circles.join(", ")} />
                      <InfoLine label="Omni-data" value={profile.is_omnidata ? "Sim" : "Não"} />
                    </div>

                    <div className="mt-6 flex flex-wrap gap-2">
                      <Badge icon={<Sparkles />} label="Emergente" />
                      <Badge icon={<ArrowUpRight />} label={profile.growth} />
                      {profile.is_omnidata && <Badge icon={<User2 />} label="Omnichannel" />}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <aside className="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Como funciona</p>
                <h2 className="mt-2 text-xl font-semibold text-slate-900">Visão rápida</h2>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  Os perfis emergentes são derivados de agrupamentos culturais e sinais verificados. Este painel mostra dados reais de backend e depende da disponibilidade do pipeline de sinais culturais.
                </p>
              </div>

              <div className="space-y-3 rounded-3xl bg-slate-50 p-4">
                <h3 className="text-sm font-semibold text-slate-900">Ações recomendadas</h3>
                <ul className="list-disc space-y-2 pl-5 text-sm text-slate-600">
                  <li>Validar dados de `cultural_signals` no pipeline.</li>
                  <li>Executar refresh manual para coletar perfis mais recentes.</li>
                  <li>Associar perfis a projetos e planos de campanha.</li>
                </ul>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </PlanGate>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-100 text-slate-700">{icon}</div>
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
          <p className="mt-2 text-xl font-bold text-slate-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}

function Badge({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-violet-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-violet-700">
      {icon}
      {label}
    </span>
  );
}

function AlertBox({ message }: { message: string }) {
  return (
    <div className="rounded-3xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
      <strong className="font-semibold">Falha ao carregar o backend:</strong>
      <p className="mt-2">{message}</p>
    </div>
  );
}
