"use client";

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";

/**
 * CulturalRadar — Radar chart das dimensões da Alma Brasileira.
 *
 * Dimensões (baseadas no modelo do engine):
 *   Calor Humano, Criatividade, Resiliência, Religiosidade,
 *   Festa & Celebração, Solidariedade
 */
export interface AlmaData {
  calor_humano:      number; // 0–1
  criatividade:      number;
  resiliencia:       number;
  religiosidade:     number;
  festa:             number;
  solidariedade:     number;
}

interface Props {
  data: AlmaData;
  label?: string;
  height?: number;
}

export default function CulturalRadar({ data, label = "Alma Brasileira", height = 320 }: Props) {
  const dimensions = [
    { name: "Calor Humano",    key: "calor_humano"  },
    { name: "Criatividade",    key: "criatividade"  },
    { name: "Resiliência",     key: "resiliencia"   },
    { name: "Religiosidade",   key: "religiosidade" },
    { name: "Festa",           key: "festa"         },
    { name: "Solidariedade",   key: "solidariedade" },
  ];

  const option = useMemo(() => ({
    tooltip: { trigger: "item" },
    legend: { data: [label], bottom: 0, textStyle: { color: "#6B7280" } },
    radar: {
      indicator: dimensions.map((d) => ({ name: d.name, max: 1 })),
      center: ["50%", "45%"],
      radius: "65%",
      splitNumber: 4,
      axisName: { color: "#374151", fontSize: 11 },
      splitArea: { areaStyle: { color: ["#F9FAFB", "#F3F4F6", "#E5E7EB", "#D1D5DB"] } },
      axisLine:  { lineStyle: { color: "#D1D5DB" } },
      splitLine: { lineStyle: { color: "#E5E7EB" } },
    },
    series: [
      {
        type: "radar",
        name: label,
        data: [
          {
            value: dimensions.map((d) => data[d.key as keyof AlmaData]),
            name: label,
            areaStyle: { color: "rgba(124, 58, 237, 0.15)" },
            lineStyle: { color: "#7C3AED", width: 2 },
            itemStyle: { color: "#7C3AED" },
          },
        ],
      },
    ],
  }), [data, label, dimensions]);

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{label}</h3>
      <ReactECharts option={option} style={{ height }} notMerge />
    </div>
  );
}
