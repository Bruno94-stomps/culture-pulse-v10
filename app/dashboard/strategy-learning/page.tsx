import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import StrategyLearnerMonitor from "@/components/dashboard/StrategyLearnerMonitor";

export const revalidate = 60;

interface StrategyLearnerStatus {
  engine_name: string;
  status: string;
  is_running: boolean;
  context_count: number;
  contexts: string[];
  data_buffer_size: number;
  performance_history_count: number;
  supabase_connected: boolean;
  model_weights: Record<string, number>;
  last_updated: string | null;
}

async function getStrategyLearnerStatus() {
  const res = await fetch(`${FASTAPI_BASE_URL}/api/v8/ml/strategy-status`, {
    next: { revalidate: 60 },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch StrategyLearner status: ${res.status}`);
  }

  const json = await res.json();
  return json as StrategyLearnerStatus;
}

export default async function StrategyLearningPage() {
  let status: StrategyLearnerStatus | null = null;
  let errorMessage: string | null = null;

  try {
    status = await getStrategyLearnerStatus();
  } catch (error) {
    errorMessage = (error as Error).message;
  }

  return (
    <main className="min-h-screen bg-slate-50 py-10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Pipeline de Aprendizado</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-900">Monitor de Strategy Learner</h1>
          <p className="mt-4 max-w-3xl text-lg text-slate-600">
            Painel de monitoramento do aprendizado automático do backend. Exibe o estado do scheduler, contexto de onboarding e pesos adaptativos atuais.
          </p>
        </div>

        {status ? (
          <StrategyLearnerMonitor status={status} />
        ) : (
          <div className="rounded-3xl border border-orange-200 bg-orange-50 p-8 text-orange-900 shadow-sm">
            <h2 className="text-2xl font-bold">Monitor de Aprendizado indisponível</h2>
            <p className="mt-3 text-sm text-orange-800">
              Não foi possível carregar o status do backend de ML.
              {errorMessage ? ` Erro: ${errorMessage}` : ""}
            </p>
            <p className="mt-4 text-sm text-orange-700">
              Verifique se o serviço FastAPI está ativo e se `FASTAPI_URL` está configurado corretamente.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
