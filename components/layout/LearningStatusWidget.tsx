"use client";

import { useEffect, useState } from "react";

interface LearningStatus {
  status: string;
  accuracy: number;
  last_update: string;
  total_samples: number;
}

import { FASTAPI_BASE_URL } from "@/lib/fastapi";

export default function LearningStatusWidget() {
  const [data, setData] = useState<LearningStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSources, setActiveSources] = useState<string[]>([]);

  useEffect(() => {
    // Lista de fontes para simular rotação visual de coleta se houver atividade
    const sources = ["YouTube", "Reddit", "Spotify", "Google Trends", "NewsAPI", "IBGE"];
    let idx = 0;
    
    async function fetchStatus() {
      try {
        // Usamos o token demo para o widget global
        const res = await fetch(`${FASTAPI_BASE_URL}/api/v8/analytics/learning-status`, {
          headers: {
            Authorization: "Bearer cp_demo_2025_free_tier",
          },
        });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Erro ao buscar status de aprendizado:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
    
    // Simulação visual de "Coleta Ativa" (Broadcast dinâmico)
    const intervalSources = setInterval(() => {
      if (Math.random() > 0.4) { // 60% de chance de mostrar uma fonte ativa
        const count = Math.floor(Math.random() * 2) + 1;
        const shuffled = [...sources].sort(() => 0.5 - Math.random());
        setActiveSources(shuffled.slice(0, count));
      } else {
        setActiveSources([]);
      }
    }, 4000);

    const interval = setInterval(fetchStatus, 300000);
    return () => {
      clearInterval(interval);
      clearInterval(intervalSources);
    };
  }, []);

  if (loading) return null;
  if (!data) return null;

  const accuracyPct = (data.accuracy * 100).toFixed(1);

  return (
    <div className="flex flex-col lg:flex-row items-center gap-2 lg:gap-4">
      {/* Fontes Ativas (Visual de Coleta em Tempo Real) */}
      {activeSources.length > 0 && (
        <div className="flex items-center gap-1.5 px-3 py-1 bg-violet-950/40 border border-violet-500/30 rounded-full animate-in fade-in zoom-in duration-500">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-violet-500"></span>
          </span>
          <span className="text-[9px] font-bold text-violet-300 uppercase tracking-tighter">
            Coletando: {activeSources.join(" + ")}
          </span>
        </div>
      )}

      <div className="hidden lg:flex items-center gap-3 px-3 py-1 bg-gray-900 border border-gray-800 rounded-full text-[10px] font-mono group hover:border-violet-500/50 transition-colors">
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-gray-400 group-hover:text-gray-300">IA LEARNING</span>
        </div>
        
        <div className="h-3 w-px bg-gray-800" />
        
        <div className="flex items-center gap-1">
          <span className="text-gray-500">ACC:</span>
          <span className="text-emerald-400 font-bold">{accuracyPct}%</span>
        </div>

        <div className="h-3 w-px bg-gray-800" />

        <div className="flex items-center gap-1">
          <span className="text-gray-500">SAMPLES:</span>
          <span className="text-gray-300">{data.total_samples}</span>
        </div>
      </div>
    </div>
  );
}
