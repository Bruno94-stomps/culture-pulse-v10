"use client";

import { useMemo, useState } from "react";

/**
 * StabilityRiskMatrix — Heatmap interativo da matriz 5×5 (Natureza × Estabilidade).
 *
 * Cada célula mostra a prioridade e recomendação de ação.
 * Clicar numa célula expande os detalhes (mensagem + ação recomendada).
 *
 * Dados vindos de GET /api/v8/stability-risk/matrix
 */

interface MatrixCell {
  natureza: string;
  estabilidade: string;
  prioridade: string;
  mensagem: string;
  acao: string;
}

interface Props {
  matrix: MatrixCell[];
  natures: string[];
  stabilities: string[];
  apiToken: string;
}

const PRIORITY_COLORS: Record<string, { bg: string; text: string; hover: string }> = {
  OPORTUNIDADE: { bg: "bg-emerald-100", text: "text-emerald-800", hover: "hover:bg-emerald-200" },
  VALIDADO:     { bg: "bg-emerald-50",  text: "text-emerald-700", hover: "hover:bg-emerald-100" },
  OK:           { bg: "bg-blue-50",     text: "text-blue-700",    hover: "hover:bg-blue-100"    },
  MONITORAR:    { bg: "bg-amber-50",    text: "text-amber-700",   hover: "hover:bg-amber-100"   },
  INVESTIGAR:   { bg: "bg-orange-50",   text: "text-orange-700",  hover: "hover:bg-orange-100"  },
  ALERTA:       { bg: "bg-red-50",      text: "text-red-700",     hover: "hover:bg-red-100"     },
  CRÍTICO:      { bg: "bg-red-100",     text: "text-red-900",     hover: "hover:bg-red-200"     },
};

const NATURE_LABELS: Record<string, string> = {
  "ORGÂNICO":     "🌱 Orgânico",
  "RESONÂNCIA":   "🔄 Resonância",
  "COMERCIAL":    "💰 Comercial",
  "SIMULAÇÃO":    "🤖 Simulação",
  "APROPRIAÇÃO":  "⚠️ Apropriação",
};

const STABILITY_LABELS: Record<string, string> = {
  estável:       "🟢 Estável",
  emergindo:     "🔵 Emergindo",
  fragmentando:  "🟡 Fragmentando",
  instável:      "🔴 Instável",
  sem_dados:     "⚪ Sem Dados",
};

export default function StabilityRiskMatrix({
  matrix,
  natures: naturesRaw,
  stabilities: stabilitiesRaw,
}: Props) {
  const [selectedCell, setSelectedCell] = useState<MatrixCell | null>(null);

  // Use defaults if API didn't return data
  const natures = naturesRaw.length > 0
    ? naturesRaw
    : ["ORGÂNICO", "RESONÂNCIA", "COMERCIAL", "SIMULAÇÃO", "APROPRIAÇÃO"];
  const stabilities = stabilitiesRaw.length > 0
    ? stabilitiesRaw
    : ["estável", "emergindo", "fragmentando", "instável", "sem_dados"];

  // Build lookup map: "ORGÂNICO|estável" → cell
  const cellMap = useMemo(() => {
    const map: Record<string, MatrixCell> = {};
    for (const cell of matrix) {
      map[`${cell.natureza}|${cell.estabilidade}`] = cell;
    }
    return map;
  }, [matrix]);

  const isEmpty = matrix.length === 0;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-700">
            Matriz de Decisão 5×5
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">
            Natureza do Sinal × Estabilidade do Cluster → Prioridade de ação
          </p>
        </div>
        <span className="text-xs font-medium text-gray-400">
          {matrix.length} células
        </span>
      </div>

      {isEmpty ? (
        <div className="text-center py-12 text-gray-400 text-sm">
          <p>Matriz indisponível — API não respondeu.</p>
          <p className="text-xs mt-1">
            Verifique se o FastAPI está rodando com os endpoints de stability-risk.
          </p>
        </div>
      ) : (
        <>
          {/* Matrix table */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="p-2 text-xs text-gray-500 font-medium text-left border-b border-gray-100">
                    Natureza ↓ / Estab. →
                  </th>
                  {stabilities.map((s) => (
                    <th
                      key={s}
                      className="p-2 text-xs text-gray-500 font-medium text-center border-b border-gray-100 whitespace-nowrap"
                    >
                      {STABILITY_LABELS[s] ?? s}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {natures.map((n) => (
                  <tr key={n}>
                    <td className="p-2 text-xs font-medium text-gray-700 whitespace-nowrap border-b border-gray-50">
                      {NATURE_LABELS[n] ?? n}
                    </td>
                    {stabilities.map((s) => {
                      const cell = cellMap[`${n}|${s}`];
                      if (!cell) {
                        return (
                          <td
                            key={s}
                            className="p-1 border-b border-gray-50"
                          >
                            <div className="rounded-lg bg-gray-50 p-2 text-center text-xs text-gray-300">
                              —
                            </div>
                          </td>
                        );
                      }

                      const colors =
                        PRIORITY_COLORS[cell.prioridade] ??
                        PRIORITY_COLORS.MONITORAR;
                      const isSelected =
                        selectedCell?.natureza === n &&
                        selectedCell?.estabilidade === s;

                      return (
                        <td
                          key={s}
                          className="p-1 border-b border-gray-50"
                        >
                          <button
                            onClick={() =>
                              setSelectedCell(isSelected ? null : cell)
                            }
                            className={`w-full rounded-lg p-2 text-center text-xs font-bold transition cursor-pointer ${
                              colors.bg
                            } ${colors.text} ${colors.hover} ${
                              isSelected ? "ring-2 ring-violet-400" : ""
                            }`}
                          >
                            {cell.prioridade}
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Detail panel */}
          {selectedCell && (
            <div className="mt-4 rounded-xl bg-violet-50 border border-violet-200 p-4 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs text-gray-500">
                    {NATURE_LABELS[selectedCell.natureza] ?? selectedCell.natureza}
                    {" × "}
                    {STABILITY_LABELS[selectedCell.estabilidade] ?? selectedCell.estabilidade}
                  </p>
                  <p className="text-sm font-bold text-gray-800 mt-1">
                    {selectedCell.prioridade}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedCell(null)}
                  className="text-gray-400 hover:text-gray-600 text-sm"
                >
                  ✕
                </button>
              </div>
              <div className="mt-3 space-y-2">
                <div>
                  <p className="text-xs font-semibold text-gray-600">Diagnóstico</p>
                  <p className="text-sm text-gray-700">{selectedCell.mensagem}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-600">Ação Recomendada</p>
                  <p className="text-sm text-gray-700">{selectedCell.acao}</p>
                </div>
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.entries(PRIORITY_COLORS).map(([label, colors]) => (
              <span
                key={label}
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors.bg} ${colors.text}`}
              >
                {label}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
