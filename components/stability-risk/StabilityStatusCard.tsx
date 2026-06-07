"use client";

import { useMemo, useState } from "react";

/**
 * StabilityStatusCard — Exibe o status atual de estabilidade dos clusters
 * com badge emoji, métricas ARI/NMI e histórico resumido.
 */

interface StabilityData {
  stability_status: string;
  badge: string;
  description: string;
  ari_score: number;
  nmi_score: number;
  n_clusters_prev: number;
  n_clusters_curr: number;
  new_clusters: number;
  lost_clusters: number;
  snapshot_count: number;
  history: Array<{
    status: string;
    badge: string;
    ari_score: number;
    nmi_score: number;
  }>;
}

interface Props {
  data: StabilityData | null;
  apiToken: string;
}

const STATUS_COLORS: Record<string, { bg: string; text: string; ring: string }> = {
  estável:       { bg: "bg-emerald-50",  text: "text-emerald-700", ring: "ring-emerald-200" },
  emergindo:     { bg: "bg-blue-50",     text: "text-blue-700",    ring: "ring-blue-200"    },
  fragmentando:  { bg: "bg-amber-50",    text: "text-amber-700",   ring: "ring-amber-200"   },
  instável:      { bg: "bg-red-50",      text: "text-red-700",     ring: "ring-red-200"     },
  sem_dados:     { bg: "bg-gray-50",     text: "text-gray-500",    ring: "ring-gray-200"    },
};

export default function StabilityStatusCard({ data }: Props) {
  const [showHistory, setShowHistory] = useState(false);

  if (!data) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Status de Estabilidade
        </h3>
        <p className="text-sm text-gray-400">
          API indisponível — dados de estabilidade não carregados.
        </p>
      </div>
    );
  }

  const status = data.stability_status ?? "sem_dados";
  const colors = STATUS_COLORS[status] ?? STATUS_COLORS.sem_dados;

  const metrics = useMemo(
    () => [
      { label: "ARI Score", value: data.ari_score?.toFixed(3) ?? "—" },
      { label: "NMI Score", value: data.nmi_score?.toFixed(3) ?? "—" },
      { label: "Clusters Atual", value: data.n_clusters_curr ?? "—" },
      { label: "Clusters Anterior", value: data.n_clusters_prev ?? "—" },
      { label: "Novos", value: data.new_clusters ?? 0 },
      { label: "Perdidos", value: data.lost_clusters ?? 0 },
      { label: "Snapshots", value: data.snapshot_count ?? 0 },
    ],
    [data]
  );

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Status de Estabilidade
        </h3>
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold ring-1 ${colors.bg} ${colors.text} ${colors.ring}`}
        >
          <span className="text-base">{data.badge}</span>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-500 mb-4">{data.description}</p>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-xl bg-gray-50 px-3 py-2 text-center"
          >
            <p className="text-xs text-gray-400">{m.label}</p>
            <p className="text-sm font-bold text-gray-800 mt-0.5">
              {m.value}
            </p>
          </div>
        ))}
      </div>

      {/* History toggle */}
      {data.history && data.history.length > 0 && (
        <div className="mt-4">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-xs text-violet-600 hover:text-violet-800 font-medium transition"
          >
            {showHistory ? "Ocultar histórico ↑" : `Ver histórico (${data.history.length}) ↓`}
          </button>

          {showHistory && (
            <div className="mt-2 max-h-40 overflow-y-auto space-y-1">
              {data.history.map((h, i) => {
                const hColors = STATUS_COLORS[h.status] ?? STATUS_COLORS.sem_dados;
                return (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-xs px-2 py-1 rounded-lg bg-gray-50"
                  >
                    <span>{h.badge}</span>
                    <span className={`font-medium ${hColors.text}`}>
                      {h.status}
                    </span>
                    <span className="text-gray-400">
                      ARI: {h.ari_score?.toFixed(3)} · NMI:{" "}
                      {h.nmi_score?.toFixed(3)}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
