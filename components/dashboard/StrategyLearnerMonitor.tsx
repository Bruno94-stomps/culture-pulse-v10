"use client";

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

export default function StrategyLearnerMonitor({ status }: { status: StrategyLearnerStatus }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/40">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Monitoramento de Aprendizado Automático</p>
            <h1 className="text-2xl font-black text-slate-900">Strategy Learner Status</h1>
          </div>
          <div className="inline-flex rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
            {status.is_running ? "Ativo" : "Inativo"}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-[11px] uppercase tracking-[0.25em] text-slate-500">Contextos carregados</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">{status.context_count}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-[11px] uppercase tracking-[0.25em] text-slate-500">Buffer de dados</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">{status.data_buffer_size}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-[11px] uppercase tracking-[0.25em] text-slate-500">Histórico de performance</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">{status.performance_history_count}</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-[11px] uppercase tracking-[0.25em] text-slate-500">Supabase conectado</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">{status.supabase_connected ? "Sim" : "Não"}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.2fr,0.8fr]">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-base font-semibold text-slate-900">Contextos Ativos</h2>
            {status.contexts.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">Nenhum contexto carregado no momento.</p>
            ) : (
              <ul className="mt-4 space-y-2 text-sm text-slate-700">
                {status.contexts.map((context) => (
                  <li key={context} className="rounded-2xl bg-white p-3 shadow-sm shadow-slate-200/70">
                    {context}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-base font-semibold text-slate-900">Pesos Atuais</h2>
            <div className="mt-4 grid grid-cols-1 gap-2 text-sm text-slate-700">
              {Object.entries(status.model_weights).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between rounded-2xl bg-white px-3 py-2 shadow-sm shadow-slate-200/70">
                  <span className="font-medium text-slate-800">{key}</span>
                  <span className="font-semibold text-slate-900">{Number(value).toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-900 px-6 py-5 text-slate-100">
          <p className="text-sm leading-6">
            Última atualização: <span className="font-semibold">{status.last_updated ?? "indisponível"}</span>.
          </p>
          <p className="mt-3 text-sm text-slate-300">
            O Strategy Learner é o componente de aprendizado adaptativo do pipeline. Ele consome contextos do onboarding e atualiza pesos automaticamente via SGD sempre que novos insight são processados.
          </p>
        </div>
      </div>
    </section>
  );
}
