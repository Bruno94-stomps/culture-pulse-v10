"use client";

import React from "react";
import { CheckCircle2, AlertCircle, Globe, Video, MessageSquare, Newspaper, Image as ImageIcon, Link as LinkIcon } from "lucide-react";

interface VeracityLineageProps {
  signal: {
    reliability?: string;
    accuracy_score?: number;
    is_verified?: boolean;
    visual_proof?: boolean;
    cross_verified?: boolean;
    plataforma?: string;
    source?: string;
    thumbnail?: string;
    image_url?: string;
    url?: string;
    calculation_details?: {
      authority?: number;
      visual?: number;
      historical?: number;
      cross_platform?: number;
    };
  };
}

export const VeracityLineage: React.FC<VeracityLineageProps> = ({ signal }) => {
  const isHigh = signal.reliability === "ALTA";
  const isMed = signal.reliability === "MEDIA";
  const score = signal.accuracy_score || 0;
  
  const getProgressColor = () => {
    if (score >= 0.8) return "bg-green-500";
    if (score >= 0.5) return "bg-amber-500";
    return "bg-rose-500";
  };

  const platformIcon = (plat: string) => {
    const p = plat.toLowerCase();
    if (p.includes("youtube")) return <Video className="w-4 h-4" />;
    if (p.includes("twitter") || p.includes("social")) return <MessageSquare className="w-4 h-4" />;
    if (p.includes("news") || p.includes("g1") || p.includes("cnn")) return <Newspaper className="w-4 h-4" />;
    return <Globe className="w-4 h-4" />;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-6">
      {/* Header: Status de Veracidade */}
      <div className={`px-4 py-3 flex items-center justify-between ${signal.is_verified ? 'bg-green-50' : 'bg-slate-50'}`}>
        <div className="flex items-center gap-2">
          {signal.is_verified ? (
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-amber-500" />
          )}
          <span className={`text-sm font-bold tracking-tight uppercase ${signal.is_verified ? 'text-green-700' : 'text-slate-700'}`}>
            {signal.is_verified ? 'EVIDÊNCIA BIOGRÁFICA VERIFICADA' : 'STATUS EM AUDITORIA'}
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-slate-400 font-bold uppercase">Accuracy Score (V9.9)</span>
          <span className={`text-lg font-black leading-none ${getProgressColor().replace('bg-', 'text-')}`}>
            {(score * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Grid de Evidências */}
      <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Coluna 1: Prova Visual (The "Smoking Gun") */}
        <div className="space-y-3">
          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
            <ImageIcon className="w-3 h-3" /> Prova Visual de Campo
          </h4>
          
          {signal.visual_proof ? (
            <div className="relative group aspect-video rounded-lg overflow-hidden border border-slate-200 bg-slate-100 shadow-inner">
              <img 
                src={signal.thumbnail || signal.image_url} 
                alt="Visual Evidence" 
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-white text-[9px] px-2 py-1 rounded-full font-bold flex items-center gap-1">
                {platformIcon(signal.plataforma || "")} {signal.plataforma}
              </div>
              {signal.url && (
                <a 
                  href={signal.url} 
                  target="_blank" 
                  rel="noreferrer"
                  className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/20 transition-all opacity-0 group-hover:opacity-100"
                >
                  <LinkIcon className="text-white w-8 h-8 drop-shadow-lg" />
                </a>
              )}
            </div>
          ) : (
            <div className="aspect-video rounded-lg border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-400 bg-slate-50/50">
              <ImageIcon className="w-8 h-8 mb-2 opacity-20" />
              <span className="text-xs font-medium">Nenhuma mídia extraída</span>
            </div>
          )}
        </div>

        {/* Coluna 2: Linhagem e Cross-Verification */}
        <div className="space-y-4">
          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
            <Globe className="w-3 h-3" /> Linhagem de Distribuição
          </h4>
          
          <div className="space-y-3">
            {/* Fonte Primária */}
            <div className={`p-3 rounded-lg border flex items-center justify-between ${isHigh ? 'border-green-100 bg-green-50/30' : 'border-slate-100 bg-slate-50/50'}`}>
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-md ${isHigh ? 'bg-green-100 text-green-600' : 'bg-slate-200 text-slate-500'}`}>
                  {platformIcon(signal.plataforma || "")}
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-800">{signal.plataforma}</p>
                  <p className="text-[10px] text-slate-500 font-medium">Autoridade da Fonte: {(signal.calculation_details?.authority || 0.5).toFixed(2)}</p>
                </div>
              </div>
              <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${isHigh ? 'bg-green-600 text-white' : 'bg-slate-400 text-white'}`}>
                {signal.reliability}
              </span>
            </div>

            {/* Cross-Verification Bonus */}
            <div className={`p-3 rounded-lg border transition-all ${signal.cross_verified ? 'border-violet-200 bg-violet-50/50 shadow-sm' : 'border-slate-100 opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-md ${signal.cross_verified ? 'bg-violet-600 text-white shadow-md' : 'bg-slate-200 text-slate-500'}`}>
                    <Globe className="w-4 h-4" />
                  </div>
                  <div>
                    <p className={`text-xs font-bold ${signal.cross_verified ? 'text-violet-900' : 'text-slate-800'}`}>
                      {signal.cross_verified ? 'Confirmado Cross-Platform' : 'Pendente em outras redes'}
                    </p>
                    <p className="text-[10px] text-slate-500 font-medium">Bônus de Veracidade: +0.15</p>
                  </div>
                </div>
                {signal.cross_verified && (
                  <span className="text-[10px] bg-violet-600 text-white px-2 py-0.5 rounded-full font-black animate-pulse">
                    V9.9
                  </span>
                )}
              </div>
            </div>

            {/* Historical Accuracy */}
            <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/30">
               <div className="flex items-center gap-3 text-slate-500">
                  <AlertCircle className="w-4 h-4" />
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-tight">Cálculo de Incerteza</p>
                    <p className="text-xs font-medium italic">Baseado em Histórico de Aprendizado Ativo</p>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer: Metodologia */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex justify-between items-center text-[9px] font-bold text-slate-400 uppercase tracking-widest">
        <span>© Culture Pulse V9.9 Veracity Engine</span>
        <span>H.I.T.L. Validated</span>
      </div>
    </div>
  );
};
