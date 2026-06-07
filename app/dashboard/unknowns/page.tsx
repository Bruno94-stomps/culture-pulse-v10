import { createClient } from "@/lib/supabase/server";
import ActiveLearningCurator from "@/components/dashboard/ActiveLearningCurator";

export const revalidate = 30; // revalida a cada 30s — fila muda rápido

interface UnknownSignal {
  id: number;
  termo: string;
  circulo: string;
  score: number;
  plataforma: string;
  raw_data: Record<string, any>;
  ts: string;
}

export default async function UnknownsPage() {
  const supabase = createClient();
  // ── Fila completa de sinais desconhecidos ───────────────────────────────
  const { data: unknowns, error, count } = await supabase
    .from("cultural_signals")
    .select("id, termo, circulo, score, plataforma, raw_data, ts", {
      count: "exact",
    })
    .eq("circulo", "emergente_desconhecido")
    .order("ts", { ascending: false })
    .limit(10); // Reduzido pois agora temos o Active Learning como foco

  const rows = unknowns ?? [];
  const totalQueue = (count && count > 0) ? count : rows.length;

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            🧠 Curadoria & Aprendizado Ativo
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Treine a IA para identificar sinais culturais relevantes e reduzir ruído nas coletas.
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href="/dashboard/unknowns/cluster"
            className="text-xs bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition font-bold"
          >
            🔬 Rodar Clustering Ward
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Coluna Principal: Active Learning */}
        <div className="lg:col-span-2">
          <ActiveLearningCurator />
        </div>

        {/* Coluna Lateral: Últimos Sinais Desconhecidos */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
              📥 Fila de Sinais Recentes
            </h3>
            
            {rows.length > 0 ? (
              <div className="space-y-3">
                {rows.map((s) => (
                  <div key={s.id} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-gray-800 text-sm">{s.termo}</span>
                      <span className="text-[10px] bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded-full font-bold">
                        {((s.score ?? 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between mt-2 text-[10px] text-gray-400">
                      <span>{s.plataforma}</span>
                      <span>{new Date(s.ts).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
                <p className="text-[10px] text-center text-gray-400 mt-2">
                  Mostrando os últimos 10 de {totalQueue} sinais.
                </p>
              </div>
            ) : (
              <p className="text-xs text-center text-gray-400 py-8">Nenhum sinal desconhecido aguardando.</p>
            )}
          </div>

          <div className="bg-violet-600 rounded-xl p-5 text-white shadow-lg shadow-violet-200">
            <h4 className="font-bold text-sm mb-2">Como funciona?</h4>
            <p className="text-xs opacity-90 leading-relaxed">
              Quando você aprova um termo, o sistema aprende que ele é relevante e aumenta a prioridade de busca. 
              Ao rejeitar, você economiza créditos de API evitando lixo.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}