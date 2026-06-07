import { createClient } from "@/lib/supabase/server";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { getServerDashboardApiHeaders } from "@/lib/dashboard";

export const revalidate = 0; // não cachear — cada execução é única

/**
 * Página de clustering on-demand para sinais "emergente_desconhecido".
 *
 * Fluxo:
 *   1. Faz query Supabase para contar sinais desconhecidos
 *   2. Se ≥ 10 sinais: chama API FastAPI /api/v8/circles/detect para rodar Ward clustering
 *   3. Exibe candidatos a novos círculos com botão de promoção
 *
 * Nota: a chamada de clustering é feita no server component via fetch
 * para a API Python backend (não diretamente no browser).
 */

interface ClusterCandidate {
  cluster_id: number;
  size: number;
  top_terms: string[];
  suggested_name: string;
  avg_score: number;
  platforms: string[];
  sample_texts: string[];
}

export default async function ClusterPage() {
  const supabase = createClient();

  // Contagem de sinais na fila
  const { count: queueSize } = await supabase
    .from("cultural_signals")
    .select("id", { count: "exact", head: true })
    .eq("circulo", "emergente_desconhecido");

  const total = queueSize ?? 0;
  const canCluster = total >= 10;

  // Tentar chamar API de clustering (se ≥ 10 sinais)
  let candidates: ClusterCandidate[] = [];
  let clusterError: string | null = null;

  if (canCluster) {
    try {
      const apiBase = FASTAPI_BASE_URL;
      const res = await fetch(`${apiBase}/api/v8/circles/detect`, {
        method: "POST",
        headers: {
          ...getServerDashboardApiHeaders(),
          "Content-Type": "application/json",
        },
        cache: "no-store",
      });

      if (res.ok) {
        const body = await res.json();
        candidates = body.data?.candidates ?? body.candidates ?? [];
      } else {
        clusterError = `API retornou ${res.status}: ${res.statusText}`;
      }
    } catch (err: any) {
      clusterError = `Não foi possível conectar à API: ${err.message ?? err}`;
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            🔬 Clustering de Sinais Desconhecidos
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Ward Agglomerative Clustering sobre TF-IDF dos sinais
            &quot;emergente_desconhecido&quot;
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href="/dashboard/unknowns"
            className="text-xs bg-gray-100 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-200 transition"
          >
            ← Voltar para fila
          </a>
          <a
            href="/dashboard/unknowns/cluster"
            className="text-xs bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition"
          >
            ↻ Re-executar
          </a>
        </div>
      </div>

      {/* Status */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <StatusCard
          label="Sinais na fila"
          value={String(total)}
          ok={canCluster}
        />
        <StatusCard
          label="Mínimo para clustering"
          value="10"
          ok={canCluster}
        />
        <StatusCard
          label="Candidatos encontrados"
          value={String(candidates.length)}
          ok={candidates.length > 0}
        />
      </div>

      {/* Erro da API */}
      {clusterError && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm">
          ⚠️ Erro ao executar clustering: {clusterError}
          <p className="text-xs mt-1 text-red-600">
            Verifique se a API FastAPI está rodando em {FASTAPI_BASE_URL}
          </p>
        </div>
      )}

      {/* Sinais insuficientes */}
      {!canCluster && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl">
          <p className="text-sm font-semibold text-yellow-800">
            ⏳ Poucos sinais ({total}) — clustering requer ≥10
          </p>
          <p className="text-xs text-yellow-700 mt-1">
            Continue coletando dados. Sinais não classificados serão acumulados
            automaticamente pelo Worker async.
          </p>
        </div>
      )}

      {/* Candidatos */}
      {candidates.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">
            🆕 Candidatos a Novos Círculos Culturais
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {candidates.map((c) => (
              <CandidateCard key={c.cluster_id} candidate={c} />
            ))}
          </div>
        </div>
      )}

      {/* Sem candidatos mas com sinais suficientes */}
      {canCluster && !clusterError && candidates.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-4xl mb-3">🔍</p>
          <p className="font-medium">
            Clustering executado, mas nenhum cluster atingiu o tamanho mínimo
            (10 sinais).
          </p>
          <p className="text-sm mt-1">
            Os sinais podem ser muito dispersos. Aguarde mais dados serem
            acumulados.
          </p>
        </div>
      )}

      {/* Explicação do algoritmo */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mt-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          ℹ️ Como funciona o clustering
        </h3>
        <ol className="text-xs text-gray-500 space-y-1 list-decimal list-inside">
          <li>
            Sinais com max_circle_score &lt; 0.3 são marcados como
            &quot;emergente_desconhecido&quot;
          </li>
          <li>
            Acumulados na fila (Redis + Supabase) pelo Worker async
          </li>
          <li>
            TF-IDF extrai features dos termos/textos de cada sinal
          </li>
          <li>
            Ward Agglomerative Clustering agrupa sinais similares
          </li>
          <li>
            Clusters com ≥10 sinais → candidatos a novo círculo cultural
          </li>
          <li>
            Admin pode promover candidato a círculo oficial (17º, 18º, etc.)
          </li>
        </ol>
      </div>
    </div>
  );
}

// ── Sub-componentes ──────────────────────────────────────────────────────────

function StatusCard({
  label,
  value,
  ok,
}: {
  label: string;
  value: string;
  ok: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        ok
          ? "bg-green-50 text-green-700 border-green-100"
          : "bg-yellow-50 text-yellow-700 border-yellow-100"
      }`}
    >
      <p className="text-2xl">{ok ? "✅" : "⏳"}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs opacity-70 mt-0.5">{label}</p>
    </div>
  );
}

function CandidateCard({ candidate: c }: { candidate: any }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-base font-bold text-gray-800">
            🆕 {c.suggested_name}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Cluster #{c.cluster_id} · {c.size} sinais ·{" "}
            {c.platforms?.join(", ")}
          </p>
        </div>
        <span className="text-xs bg-violet-100 text-violet-700 px-2 py-1 rounded-full font-semibold">
          {((c.avg_score ?? 0) * 100).toFixed(0)}%
        </span>
      </div>

      {/* Top termos */}
      <div className="flex flex-wrap gap-1.5 mt-3">
        {(c.top_terms ?? []).slice(0, 8).map((t: string) => (
          <span
            key={t}
            className="px-2 py-0.5 bg-yellow-50 text-yellow-800 rounded text-xs border border-yellow-100"
          >
            {t}
          </span>
        ))}
      </div>

      {/* Textos de amostra */}
      {c.sample_texts && c.sample_texts.length > 0 && (
        <div className="mt-3 space-y-1">
          <p className="text-xs font-medium text-gray-500">Amostras:</p>
          {c.sample_texts.slice(0, 3).map((text: string, i: number) => (
            <p
              key={i}
              className="text-xs text-gray-400 line-clamp-1 italic"
            >
              &quot;{text}&quot;
            </p>
          ))}
        </div>
      )}

      {/* Ações */}
      <div className="flex gap-2 mt-4 pt-3 border-t border-gray-50">
        <a
          href={`/api/unknown/promote?cluster_id=${c.cluster_id}&name=${encodeURIComponent(c.suggested_name)}`}
          className="flex-1 text-center px-3 py-2 bg-violet-600 text-white rounded-lg text-xs font-medium hover:bg-violet-700 transition"
        >
          Promover a Círculo
        </a>
        <a
          href={`/api/unknown/dismiss?cluster_id=${c.cluster_id}`}
          className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-xs hover:bg-gray-200 transition"
        >
          Ignorar
        </a>
      </div>
    </div>
  );
}
