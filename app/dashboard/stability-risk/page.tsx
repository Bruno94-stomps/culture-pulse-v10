import { createClient } from "@/lib/supabase/server";
import PlanGate from "@/components/auth/PlanGate";
import StabilityRiskMatrix from "@/components/stability-risk/StabilityRiskMatrix";
import StabilityStatusCard from "@/components/stability-risk/StabilityStatusCard";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getCurrentPlan } from "@/lib/plan";
import { getDashboardAuthHeaders, getDashboardAuthToken } from "@/lib/dashboard";
import { Activity, LayoutGrid, Zap, TrendingUp } from "lucide-react";

export const revalidate = 300; // ISR 5 min

/**
 * Stability × Risk — Server Component.
 * Busca matrix 5×5 e status de estabilidade do FastAPI.
 * Requer plano PRO+.
 */
export default async function StabilityRiskPage() {
  const supabase = createClient();
  const plan = await getCurrentPlan();
  const authHeaders = await getDashboardAuthHeaders(plan);
  const apiToken = await getDashboardAuthToken(plan);

  let matrixData: any[] = [];
  let natures: string[] = [];
  let stabilities: string[] = [];
  let statusData: any = null;

  try {
    const baseUrl = FASTAPI_BASE_URL;
    const headers = authHeaders;

    const [matrixRes, statusRes] = await Promise.allSettled([
      fetch(`${baseUrl}/api/v8/stability-risk/matrix`, {
        headers,
        next: { revalidate: 300 },
      }),
      fetch(`${baseUrl}/api/v8/stability-risk/status`, {
        headers,
        next: { revalidate: 60 },
      }),
    ]);

    if (matrixRes.status === "fulfilled" && matrixRes.value.ok) {
      const json = await matrixRes.value.json();
      matrixData = json.data?.matrix ?? [];
      natures = json.data?.natures ?? [];
      stabilities = json.data?.stabilities ?? [];
    }

    if (statusRes.status === "fulfilled" && statusRes.value.ok) {
      const json = await statusRes.value.json();
      statusData = json.data ?? null;
    }
  } catch {
    // API indisponível — componentes mostram estado vazio
  }

  return (
    <div className="p-8 space-y-10 max-w-7xl mx-auto bg-[#FDFDFF] min-h-screen">
      {/* Header Premium */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="w-2 h-10 bg-violet-600 rounded-full" />
          <h1 className="text-3xl font-black text-gray-900 tracking-tight">
            Sinais & Estabilidade
          </h1>
        </div>
        <p className="text-gray-400 font-medium italic pl-5">
          Análise longitudinal de clusters culturais, resiliência de mercado e riscos de apropriação.
        </p>
      </div>

      <PlanGate required="pro" current={plan}>
        {/* Top Intelligence Row */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2">
            <StabilityStatusCard
              data={statusData}
              apiToken={apiToken}
            />
          </div>
          
          {/* Quick Metrics Overlay */}
          <div className="grid grid-cols-2 gap-4">
             <div className="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex flex-col justify-between group hover:border-violet-200 transition-all">
                <Activity size={20} className="text-violet-500 mb-4" />
                <div>
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1">Health Score</span>
                  <span className="text-2xl font-black text-gray-900">88.4%</span>
                </div>
             </div>
             <div className="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex flex-col justify-between group hover:border-emerald-200 transition-all">
                <Zap size={20} className="text-emerald-500 mb-4" />
                <div>
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1">Capturas/Dia</span>
                  <span className="text-2xl font-black text-gray-900">1.2k</span>
                </div>
             </div>
          </div>
        </div>

        {/* Captured Signals Section - NOVO bloco lateral/focado */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <LayoutGrid size={20} className="text-gray-400" />
            <h2 className="text-xl font-black text-gray-900 uppercase tracking-widest">Sinais Ativos no Radar</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {[
              { label: 'Festival Almoço no Coreto', val: '84.5%', trend: 'up', color: 'emerald' },
              { label: 'Dancinha Viral Sertaneja', val: '72.1%', trend: 'up', color: 'amber' },
              { label: 'Robô de Suporte em Zap', val: '95.8%', trend: 'stable', color: 'blue' },
              { label: 'Painel Solar Comunitário', val: '64.2%', trend: 'down', color: 'red' },
              { label: 'Revenda de Tênis Usado', val: '88.4%', trend: 'up', color: 'violet' },
            ].map((sig, i) => (
              <div key={i} className="bg-white p-5 rounded-[28px] border border-gray-100 shadow-sm hover:shadow-md transition-all group flex flex-col justify-between min-h-[140px]">
                <div className="flex justify-between items-start">
                  <div className={`w-2 h-2 rounded-full bg-${sig.color}-500 shadow-[0_0_8px_rgba(0,0,0,0.1)]`} />
                  {sig.trend === 'up' && <TrendingUp size={14} className="text-emerald-500" />}
                </div>
                <div>
                  <h3 className="text-xs font-black text-gray-800 leading-tight mb-2 group-hover:text-violet-600 transition-colors">{sig.label}</h3>
                  <div className="flex items-end justify-between">
                    <span className="text-[10px] font-bold text-gray-400 uppercase">Affinity</span>
                    <span className="text-lg font-black text-gray-900">{sig.val}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Row 2: Decision matrix 5×5 */}
        <div className="mt-10">
          <div className="mb-6">
             <h2 className="text-xl font-black text-gray-900 tracking-tight">Matriz Decisional de Risco</h2>
             <p className="text-sm text-gray-400">Cruzamento de natureza sistêmica vs. estabilidade longitudinal</p>
          </div>
          <div className="bg-white rounded-[40px] border border-gray-100 shadow-sm p-4 overflow-hidden min-h-[700px]">
            <StabilityRiskMatrix
              matrix={matrixData}
              natures={natures}
              stabilities={stabilities}
              apiToken={apiToken}
            />
          </div>
        </div>
      </PlanGate>
    </div>
  );
}
