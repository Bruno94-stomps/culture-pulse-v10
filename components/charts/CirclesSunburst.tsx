"use client";

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";
import * as echarts from "echarts/core";

/**
 * CirclesSunburst — Sunburst dos 16 círculos culturais brasileiros.
 * Nível 1: categoria macro  |  Nível 2: círculos  |  Nível 3: termos top
 */
export interface CircleSignal {
  circulo:   string;
  categoria: string;   // ex: "Entretenimento", "Comportamento", "Consumo"
  score:     number;   // 0–100
  termos?:   Array<{ termo: string; score: number }>;
}

interface Props {
  signals: CircleSignal[];
  height?: number;
}

// Paleta por categoria
const CAT_COLORS: Record<string, string> = {
  "Entretenimento": "#7C3AED",
  "Comportamento":  "#F59E0B",
  "Consumo":        "#10B981",
  "Espiritualidade":"#EC4899",
  "Identidade":     "#3B82F6",
};

export default function CirclesSunburst({ signals, height = 380 }: Props) {
  const option = useMemo(() => {
    // Agrupar por categoria
    const catMap: Record<string, CircleSignal[]> = {};
    for (const s of signals) {
      (catMap[s.categoria] ??= []).push(s);
    }

    const data = Object.entries(catMap).map(([cat, items]) => ({
      name:  cat,
      value: items.reduce((acc, s) => acc + s.score, 0),
      itemStyle: { color: CAT_COLORS[cat] ?? "#6B7280" },
      children: items.map((s) => ({
        name:  s.circulo,
        value: s.score,
        itemStyle: { color: (CAT_COLORS[s.categoria] ?? "#6B7280") + "99" },
        children: (s.termos ?? []).slice(0, 4).map((t) => ({
          name:  t.termo,
          value: Math.round(t.score),
        })),
      })),
    }));

    return {
      tooltip: {
        trigger: "item",
        formatter: (p: { name: string; value: number }) =>
          `<b>${p.name}</b><br/>Score: ${p.value}`,
      },
      series: [
        {
          type: "sunburst",
          data,
          radius: ["15%", "90%"],
          label: {
            rotate: "radial",
            fontSize: 10,
            color: "#374151",
            overflow: "truncate",
            width: 60,
          },
          itemStyle: { borderRadius: 4, borderWidth: 1, borderColor: "#fff" },
          emphasis: { focus: "ancestor" },
          levels: [
            {},
            { r0: "15%", r: "40%", label: { rotate: 0, fontSize: 11, fontWeight: "bold" } },
            { r0: "40%", r: "70%", label: { fontSize: 10 } },
            { r0: "70%", r: "90%", label: { show: false } },
          ],
        },
      ],
    };
  }, [signals]);

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">
        🔵 16 Círculos Culturais
      </h3>
      <ReactECharts option={option} style={{ height }} notMerge />
    </div>
  );
}
