"use client";

import ReactECharts from "echarts-for-react";
import { useEffect, useRef, useState, useCallback } from "react";

/**
 * SignalStream — gráfico de linha com streaming via WebSocket.
 *
 * Conecta ao endpoint:
 *   ws://{host}/ws/signals/{clientId}?token={apiToken}
 *
 * Usa ECharts com appendData para performance O(1) sem re-render completo.
 * Mantém até maxPoints pontos no gráfico.
 */
interface StreamPoint {
  ts:     number;
  score:  number;
  circulo: string;
  termo:   string;
}

import { FASTAPI_WS_URL } from "@/lib/fastapi";

interface Props {
  clientId:  string;
  apiToken:  string;
  wsBaseUrl?: string;
  maxPoints?: number;
  height?:    number;
  plan?:      "free" | "pro" | "executive" | "enterprise";
}

export default function SignalStream({
  clientId,
  apiToken,
  wsBaseUrl = FASTAPI_WS_URL,
  maxPoints = 60,
  height = 280,
  plan = "free",
}: Props) {
  const chartRef = useRef<any>(null);
  const wsRef    = useRef<WebSocket | null>(null);
  const bufferRef = useRef<StreamPoint[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [lastSignal, setLastSignal] = useState<StreamPoint | null>(null);

  // Cores por intensidade
  const SCORE_COLOR = (score: number) =>
    score >= 0.8 ? "#10B981" : score >= 0.6 ? "#F59E0B" : "#7C3AED";

  // Opção base do gráfico
  const BASE_OPTION = {
    animation: false,
    tooltip: {
      trigger: "axis",
      formatter: (params: any[]) => {
        const p = params[0];
        const pt: StreamPoint = bufferRef.current[p.dataIndex] ?? { circulo: "", termo: "" };
        return `<b>${pt.circulo}</b><br/>${pt.termo}<br/>Score: ${(p.value * 100).toFixed(0)}%`;
      },
    },
    grid: { top: 24, right: 16, bottom: 24, left: 44 },
    xAxis: {
      type: "category",
      data: [] as string[],
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: "#E5E7EB" } },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 1,
      axisLabel: { formatter: (v: number) => `${(v * 100).toFixed(0)}%`, fontSize: 10 },
      splitLine: { lineStyle: { color: "#F3F4F6" } },
    },
    series: [
      {
        type: "line",
        data: [] as number[],
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#7C3AED", width: 2 },
        itemStyle: { color: "#7C3AED" },
        areaStyle: { color: { type: "linear", x:0,y:0,x2:0,y2:1,
          colorStops: [
            { offset: 0, color: "rgba(124,58,237,0.25)" },
            { offset: 1, color: "rgba(124,58,237,0.02)" },
          ],
        }},
      },
    ],
  };

  // Atualiza o gráfico com append sem re-render
  const pushPoint = useCallback((point: StreamPoint) => {
    bufferRef.current.push(point);
    if (bufferRef.current.length > maxPoints) {
      bufferRef.current.shift();
    }

    const chart = chartRef.current?.getEchartsInstance();
    if (!chart) return;

    const xs = bufferRef.current.map((p) =>
      new Date(p.ts * 1000).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    );
    const ys = bufferRef.current.map((p) => p.score);

    chart.setOption({
      xAxis: { data: xs },
      series: [{ data: ys }],
    }, false, true);
  }, [maxPoints]);

  // WebSocket
  useEffect(() => {
    const url = `${wsBaseUrl}/ws/signals/${clientId}?token=${apiToken}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === "signal" && msg.data) {
          const point: StreamPoint = {
            ts:      msg.data.ts ?? Date.now() / 1000,
            score:   msg.data.score ?? 0,
            circulo: msg.data.circulo ?? "—",
            termo:   msg.data.termo ?? "—",
          };
          setLastSignal(point);
          pushPoint(point);
        }
        if (msg.event === "ping") ws.send("ping");
      } catch {}
    };

    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("disconnected");

    // Intervalo de reconexão simples
    const retry = setInterval(() => {
      if (ws.readyState === WebSocket.CLOSED) {
        setStatus("connecting");
        ws.close();
      }
    }, 10_000);

    return () => {
      clearInterval(retry);
      ws.close();
    };
  }, [clientId, apiToken, wsBaseUrl, pushPoint]);

  const STATUS_INDICATOR = {
    connecting:   { color: "bg-yellow-400", label: "Conectando..." },
    connected:    { color: "bg-green-400",  label: "Ao vivo"       },
    disconnected: { color: "bg-red-400",    label: "Desconectado"  },
  }[status];

  const INTERVAL_LABELS: Record<string, string> = { free: "60s", pro: "30s", executive: "15s", enterprise: "5s" };

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${STATUS_INDICATOR.color} animate-pulse`} />
          <span className="text-sm font-semibold text-gray-700">Streaming de Sinais</span>
          <span className="text-xs text-gray-400">{STATUS_INDICATOR.label}</span>
        </div>
        <span className="text-xs text-gray-400">
          intervalo {INTERVAL_LABELS[plan]} · {bufferRef.current.length}/{maxPoints} pts
        </span>
      </div>

      {/* Último sinal */}
      {lastSignal && (
        <div className="mb-3 px-3 py-2 bg-violet-50 rounded-lg flex items-center gap-3 text-sm">
          <span
            className="font-bold"
            style={{ color: SCORE_COLOR(lastSignal.score) }}
          >
            {(lastSignal.score * 100).toFixed(0)}%
          </span>
          <span className="text-violet-700 font-medium">{lastSignal.circulo}</span>
          <span className="text-gray-500 truncate">{lastSignal.termo}</span>
        </div>
      )}

      {/* Gráfico */}
      <ReactECharts
        ref={chartRef}
        option={BASE_OPTION}
        style={{ height }}
        notMerge={false}   // false = merge incremental para performance
      />
    </div>
  );
}
