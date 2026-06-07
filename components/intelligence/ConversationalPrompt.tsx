"use client";
import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/fastapi";

interface UncertainQuery {
  query: string;
  confidence: number;
  reason?: string;
}

export default function ConversationalPrompt() {
  const [uncertainQueries, setUncertainQueries] = useState<UncertainQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [expanded, setExpanded] = useState(false);

  const API_BASE = API_BASE_URL;

  useEffect(() => {
    fetchUncertainQueries();
  }, []);

  async function fetchUncertainQueries() {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/v8/active-learning/uncertain`);
      const data = await res.json();
      if (data.status === "success" && data.data) {
        // V10.4: Injetando contexto estratégico (A-HA Moment) baseado nos objetivos do usuário
        const enriched = data.data.map((q: UncertainQuery) => {
          let ahaInsight = "";
          // Lógica simplificada de contexto para Mock (Pesquisa, Lançamento, Crise)
          if (q.query.toLowerCase().includes('tendência') || q.query.length < 5) {
            ahaInsight = "Para sua Pesquisa: Esse sinal tem 'fogo' (Reação real), não é só barulho passageiro.";
          } else if (q.confidence > 0.8) {
            ahaInsight = "Para seu Lançamento: Alta predição D+90 detectada. É um sinal seguro para escala.";
          } else {
            ahaInsight = "Para seu Tracking: A recorrência aqui indica se o movimento é pontual ou está se espalhando.";
          }

          return {
            ...q,
            context_insight: ahaInsight
          };
        });
        setUncertainQueries(enriched);
      }
    } catch (err) {
      console.error("Erro ao buscar queries incertas:", err);
    } finally {
      setLoading(false);
    }
  }

  async function submitFeedback(relevant: boolean) {
    if (uncertainQueries.length === 0) return;
    
    const current = uncertainQueries[currentIdx];
    try {
      await fetch(`${API_BASE}/api/v8/active-learning/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: current.query,
          relevant: relevant,
          confidence: 1.0,
          source: "analyst"
        }),
      });

      // Passar para a próxima ou recarregar
      if (currentIdx < uncertainQueries.length - 1) {
        setCurrentIdx(currentIdx + 1);
      } else {
        setUncertainQueries([]);
        fetchUncertainQueries();
      }
    } catch (err) {
      console.error("Erro ao enviar feedback:", err);
    }
  }

  if (loading && uncertainQueries.length === 0) return null;
  if (!loading && uncertainQueries.length === 0) return null;

  const current = (uncertainQueries[currentIdx] as any);

  return (
    <div className={`fixed bottom-6 right-6 w-80 bg-white border border-violet-100 shadow-2xl rounded-2xl overflow-hidden transition-all duration-300 transform ${expanded ? 'scale-100' : 'scale-95 opacity-90'}`}>
      <div className="bg-gradient-to-r from-violet-600 to-indigo-600 p-4 flex justify-between items-center text-white">
        <div className="flex items-center gap-2">
          <span className="animate-pulse w-2 h-2 bg-green-400 rounded-full"></span>
          <h3 className="text-sm font-bold uppercase tracking-wider">Active Learning IA</h3>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="text-white/80 hover:text-white">
          {expanded ? '−' : '+'}
        </button>
      </div>

      <div className={`p-4 ${expanded ? 'block' : 'hidden'}`}>
        <p className="text-[10px] font-black text-violet-600 uppercase tracking-widest mb-2">Momento A-HA:</p>
        <div className="bg-gradient-to-br from-violet-600 to-indigo-700 rounded-xl p-4 mb-4 border border-white/20 shadow-xl relative overflow-hidden group">
           {/* Efeito de Vidro/Brilho */}
           <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-white/20 transition-all" />
           
           <p className="text-[13px] font-bold text-white relative z-10 leading-snug">
              {current.context_insight}
           </p>
           
           <div className="mt-3 pt-3 border-t border-white/10 flex items-center gap-2 relative z-10">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-[9px] font-black text-white/70 uppercase tracking-tighter">Sinal analisado: "{current.query}"</span>
           </div>
        </div>

        <p className="text-[11px] text-gray-500 mb-4 leading-relaxed line-clamp-2">
          Sua decisão agora calibra a inteligência para os próximos sinais de {current.query}.
        </p>

        <div className="flex gap-2">
          <button 
            onClick={() => submitFeedback(true)}
            className="flex-1 bg-green-500 hover:bg-green-600 text-white text-xs font-bold py-2 rounded-lg transition"
          >
            RELEVANTE
          </button>
          <button 
            onClick={() => submitFeedback(false)}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-bold py-2 rounded-lg transition"
          >
            DESCARTAR
          </button>
        </div>
        
        <div className="mt-4 flex justify-between items-center">
          <span className="text-[10px] text-gray-400">
            {currentIdx + 1} de {uncertainQueries.length} pendentes
          </span>
          <button 
            onClick={fetchUncertainQueries}
            className="text-[10px] text-violet-600 hover:underline"
          >
            Recarregar
          </button>
        </div>
      </div>

      {!expanded && (
        <div className="p-4 cursor-pointer" onClick={() => setExpanded(true)}>
          <p className="text-xs font-medium text-gray-700">
            {uncertainQueries.length} termos aguardando sua validação...
          </p>
        </div>
      )}
    </div>
  );
}
