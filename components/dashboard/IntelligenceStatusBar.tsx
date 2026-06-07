"use client";

import React from 'react';
import { Search, Target, Rocket, RefreshCw, TrendingUp } from 'lucide-react';

interface IntelligenceStatusBarProps {
  totalSignals: number;
  activeImpact: number; // Alpha (geometric distance)
  discoveryRate: string | number; // Narrativa do Objetivo (Ex: "Lançamento Estratégico")
  signalRecurrence?: number; 
  reactionRate?: number;
  predictionConfidence?: number;
}

/**
 * Componente de Top-Bar de Inteligência do Dashboard (V10.4)
 * Focado na simplicidade e ganho estratégico.
 */
const IntelligenceStatusBar: React.FC<IntelligenceStatusBarProps> = ({ 
  totalSignals, 
  activeImpact, 
  discoveryRate,
  signalRecurrence = 68,
  reactionRate = 84,
  predictionConfidence = 92
}) => {
  const [mounted, setMounted] = React.useState(false);
  const [showDetails, setShowDetails] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const alphaValue = activeImpact / 100;
  
  // ── Reaction Speed (Latência em ms) baseada no Alpha ────────────────────
  // V9.9: Inverte a lógica para ser intuitiva (Alpha Alto = Reação Rápida = Menor Latência)
  const currentReactionSpeed = Math.max(12, Math.round(150 - (alphaValue * 120))); 
  const isOptimal = currentReactionSpeed < 50;

  const tractionAvg = (signalRecurrence + reactionRate + predictionConfidence) / 3;
  const ipcValue = Math.round((activeImpact / 100) * tractionAvg * 1.5);

  const narrative = typeof discoveryRate === 'string' ? discoveryRate : "Análise em Curso";

  return (
    <div className="space-y-4 mb-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric 1: Volume */}
        <div className="flex items-center p-5 bg-white rounded-3xl border border-gray-100 shadow-sm">
          <div className="bg-blue-50 p-3.5 rounded-2xl mr-4">
            <Search className="w-6 h-6 text-blue-600" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-2xl font-black text-gray-900 leading-tight">
              {mounted ? totalSignals.toLocaleString('pt-BR') : ""}
            </p>
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-0.5">
              Sinais Captados
            </p>
            <p className="text-[9px] text-gray-400 font-medium">Nas plataformas selecionadas</p>
          </div>
        </div>

        {/* Metric 2: Ganhos (IPC) - Interativa */}
        <button 
          onClick={() => setShowDetails(!showDetails)}
          className={`group flex items-center p-5 rounded-3xl border transition-all text-left ${
            showDetails 
              ? 'bg-violet-600 border-violet-500 shadow-lg shadow-violet-200' 
              : 'bg-white border-gray-100 hover:border-violet-100 shadow-sm'
          }`}
        >
          <div className={`${showDetails ? 'bg-violet-500' : 'bg-violet-50'} p-3.5 rounded-2xl mr-4 transition-colors`}>
            <TrendingUp className={`w-6 h-6 ${showDetails ? 'text-white' : 'text-violet-600'}`} strokeWidth={2.5} />
          </div>
          <div className="flex-1">
            <p className={`text-2xl font-black leading-tight ${showDetails ? 'text-white' : 'text-gray-900'}`}>
              {ipcValue} pts
            </p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <p className={`text-[10px] font-black uppercase tracking-widest ${showDetails ? 'text-violet-200' : 'text-gray-400'}`}>
                Ganhos de Sinais (IPC)
              </p>
              {isOptimal && !showDetails && (
                 <div className="px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded text-[8px] font-black">JANELA DE AÇÃO</div>
              )}
            </div>
            <p className={`text-[9px] font-medium ${showDetails ? 'text-violet-200' : 'text-gray-400'}`}>Potencial Cultural do Sinal</p>
          </div>
          <div className={`ml-2 transition-transform duration-300 ${showDetails ? 'rotate-180' : ''}`}>
             <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className={showDetails ? 'text-violet-200' : 'text-gray-300'}>
                <polyline points="6 9 12 15 18 9"></polyline>
             </svg>
          </div>
        </button>

        {/* Metric 3: Narrativa do Objetivo (RESTAURADO) */}
        <div className="flex items-center p-5 bg-white rounded-3xl border border-gray-100 shadow-sm transition-all text-left">
          <div className="bg-rose-50 p-3.5 rounded-2xl mr-4 flex-shrink-0">
            <Rocket className="w-6 h-6 text-rose-600" strokeWidth={2.5} />
          </div>
          <div className="overflow-hidden">
            <p className="text-xl font-black text-gray-900 leading-tight truncate">
              {narrative}
            </p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none">
                Objetivo Atual
              </p>
              <div className={`px-1.5 py-0.5 rounded text-[8px] font-black uppercase ${
                isOptimal ? 'bg-amber-50 text-amber-600 animate-pulse' : 'bg-gray-100 text-gray-500'
              }`}>
                {currentReactionSpeed}ms Latência
              </div>
            </div>
            <p className="text-[9px] text-gray-400 font-medium">Insights descobertos</p>
          </div>
        </div>
      </div>

      {/* Subtópico Expandível: Drivers Técnicos (RESTAURADO V10.4) */}
      {showDetails && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6 bg-gray-50/50 rounded-3xl border border-gray-100 border-dashed animate-in fade-in slide-in-from-top-2">
          <div className="flex flex-col">
            <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-1 flex items-center gap-1">
              <RefreshCw size={10} /> Recorrência
            </p>
            <p className="text-sm font-bold text-gray-700">{signalRecurrence}%</p>
            <p className="text-[9px] text-gray-400">Consistência do sinal no setor</p>
          </div>
          <div className="flex flex-col border-x border-gray-200 px-4">
            <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-1 flex items-center gap-1">
              <Target size={10} /> Taxa de Reação
            </p>
            <p className="text-sm font-bold text-gray-700">{reactionRate}%</p>
            <p className="text-[9px] text-gray-400">Velocidade de resposta da audiência</p>
          </div>
          <div className="flex flex-col">
            <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-1 flex items-center gap-1">
              <TrendingUp size={10} /> Predição
            </p>
            <p className="text-sm font-bold text-gray-700">{predictionConfidence}%</p>
            <p className="text-[9px] text-gray-400">Probabilidade de escala em D+90</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceStatusBar;
