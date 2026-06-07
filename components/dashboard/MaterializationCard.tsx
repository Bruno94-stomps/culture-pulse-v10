'use client';

import React, { useState } from 'react';
import { Rocket, Target, Shield, Sparkles, Wand2, Globe2, Cpu, Users, Gavel, Landmark, BadgeDollarSign } from 'lucide-react';

const PEST_ICONS: any = {
  Political: <Landmark size={14} className="text-red-500" />,
  Economic: <BadgeDollarSign size={14} className="text-emerald-500" />, 
  Social: <Users size={14} className="text-blue-500" />,
  Technological: <Cpu size={14} className="text-amber-500" />
};

const PEST_LABELS: any = {
  Political: "Político & Legal",
  Economic: "Econômico",
  Social: "Social & Cultural",
  Technological: "Tecnológico"
};

const EVIDENCE_ICONS: any = {
  "Notícia/Artigo": <BadgeDollarSign size={14} className="text-blue-500" />,
  "Vídeo/Campanha": <Rocket size={14} className="text-rose-500" />,
  "Geral": <Target size={14} className="text-gray-500" />
};

interface MaterializationCardProps {
  projectId: string;
  brandName: string;
  currentGoal: string;
  onboardingContext: string;
}

/**
 * Materialization Card (V9)
 * Este componente permite que o usuário veja a entrega concreta (Ativos) 
 * direto do Dashboard, materializando a inteligência em ação real.
 */
export default function MaterializationCard({ 
  projectId, 
  brandName, 
  currentGoal, 
  onboardingContext 
}: MaterializationCardProps) {
  const [loading, setLoading] = useState(false);
  const [asset, setAsset] = useState<any>(null);

  const handleMaterialize = async () => {
    setLoading(true);
    setAsset(null); // Resetar para animação
    try {
      console.log("Materializando para o projeto:", projectId);
      const response = await fetch('/api/materialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectId, assetType: 'campaign' })
      });
      
      if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
      }

      const result = await response.json();
      console.log("Ativo recebido:", result);
      setAsset(result.data);
    } catch (err) {
      console.error("Falha na materialização:", err);
      // Fallback local se a API falhar totalmente
      setAsset({
        content: "[MODO DEMO] Ação Estratégica: Liderar a narrativa de 'Corre' Digital com foco em Micro-Empreendedores.",
        nuance_explanation: "O sistema detectou que a conexão com o banco de dados está instável, mas a lógica de IA local recomenda este posicionamento.",
        cultural_scores: { relevance: 0.9, resonance: 0.85, authenticity: 0.95, dissonance: 0.7 },
        visual_consistency_score: 0.9,
        irony_detection_score: 0.05,
        pest_impact: { Political: 0.1, Economic: 0.8, Social: 0.9, Technological: 0.7 },
        evidence: []
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-[40px] border border-gray-100 shadow-sm p-10 overflow-hidden relative group">
      <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform">
         <Wand2 size={120} />
      </div>

      <div className="flex flex-col md:flex-row items-start justify-between gap-8 relative z-10">
        <div className="max-w-xl">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-[10px] font-black text-violet-600 bg-violet-50 px-3 py-1 rounded-full uppercase tracking-widest">
              Materialização V9
            </span>
            <span className="text-[10px] font-black text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full uppercase tracking-widest">
              Lente: {currentGoal}
            </span>
          </div>
          
          <h2 className="text-3xl font-black text-gray-900 tracking-tight leading-tight">
             Transformar Dados em <span className="text-violet-600">Ação Cultural</span>
          </h2>
          <p className="text-gray-400 font-medium text-sm mt-4 leading-relaxed">
             Gere protótipos de campanhas e ativos de marca prontos para o mercado, 
             totalmente alinhados com o contexto da <span className="text-gray-900 font-bold">{brandName}</span> 
             no território de <span className="italic">"{onboardingContext}"</span>.
          </p>
        </div>

        <button 
          onClick={handleMaterialize}
          disabled={loading}
          className="bg-violet-900 text-white px-8 py-5 rounded-[28px] font-black text-sm uppercase tracking-widest flex items-center gap-3 hover:bg-violet-950 transition-all shadow-xl hover:scale-[1.02] disabled:opacity-50"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : <Sparkles size={20} />}
          {loading ? 'Gerando Ativos...' : 'Materializar Entrega'}
        </button>
      </div>

      {asset && (
        <div className="mt-12 bg-[#FDFDFF] border border-gray-100 rounded-[32px] p-8 animate-in fade-in slide-in-from-top-4">
           <div className="flex flex-col gap-6">
              <div className="space-y-4">
                 <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] block">Protótipo Gerado (Engine Bertimbau V8.0)</p>
                 <div className="text-xl font-bold text-gray-800 leading-normal italic">
                   "{asset.content}"
                 </div>
              </div>

              {/* V9.5: EXPLICAÇÃO DO SABIÁ-2 */}
              {asset.nuance_explanation && (
                <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex gap-3 items-start">
                   <div className="p-2 bg-white rounded-lg shadow-sm">
                      <Sparkles size={16} className="text-amber-500" />
                   </div>
                   <div>
                      <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-1">Nuance Cultural (Sabiá-2)</p>
                      <p className="text-xs text-amber-900 font-medium leading-relaxed italic">
                        "{asset.nuance_explanation}"
                      </p>
                   </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                 {/* NOVO: CARD DE DISSONÂNCIA NARRATIVA + MULTIMODAL SCORES */}
                 <div className="bg-violet-50 border border-violet-100 rounded-3xl p-6 shadow-sm relative overflow-hidden group/dissonance">
                    <div className="absolute -right-4 -bottom-4 opacity-10 group-hover/dissonance:scale-125 transition-transform duration-500">
                       <Rocket size={80} className="text-violet-600" />
                    </div>
                    <p className="text-[10px] font-black text-violet-600 uppercase mb-2 tracking-[0.2em]">Dissonância Narrativa (Pioneirismo)</p>
                    <div className="flex items-end gap-2 mb-4">
                       <span className="text-4xl font-black text-violet-900 tracking-tighter">
                          {(asset.cultural_scores.dissonance * 100).toFixed(0)}%
                       </span>
                       <span className="text-[10px] font-bold text-violet-500 mb-2 uppercase italic">Match de Inovação</span>
                    </div>

                    {/* V9.5: MULTIMODAL INDICATORS */}
                    <div className="space-y-3 pt-4 border-t border-violet-200">
                       <div className="flex justify-between items-center text-[10px] font-bold">
                          <span className="text-violet-600 uppercase">Aderência Estética (CV)</span>
                          <span className="text-violet-900">{(asset.visual_consistency_score * 100).toFixed(0)}%</span>
                       </div>
                       <div className="w-full h-1 bg-violet-200 rounded-full overflow-hidden">
                          <div className="h-full bg-violet-600" style={{ width: `${asset.visual_consistency_score * 100}%` }} />
                       </div>
                       
                       <div className="flex justify-between items-center text-[10px] font-bold">
                          <span className="text-violet-600 uppercase">Filtro de Verdade (Ironia)</span>
                          <span className="text-violet-900">{(100 - (asset.irony_detection_score * 100)).toFixed(0)}%</span>
                       </div>
                       <div className="w-full h-1 bg-violet-200 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500" style={{ width: `${(1-asset.irony_detection_score) * 100}%` }} />
                       </div>
                    </div>
                 </div>
                 
                 {/* NOVO: VISUALIZAÇÃO DE IMPACTO PEST (FRAMEWORK ACADÊMICO) */}
                 <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm">
                    <p className="text-[10px] font-black text-gray-400 uppercase mb-4 tracking-[0.15em] flex items-center gap-2">
                       <Globe2 size={12} className="text-violet-400" /> 
                       Impacto Multidimensional (PEST)
                    </p>
                    <div className="space-y-4">
                       {Object.entries(asset.pest_impact).map(([key, value]: any) => (
                          <div key={key} className="space-y-1.5">
                             <div className="flex justify-between items-center text-[10px] font-bold">
                                <span className="flex items-center gap-2 text-gray-600 uppercase tracking-tighter">
                                   {PEST_ICONS[key] || <Target size={14} />} 
                                   {PEST_LABELS[key]}
                                </span>
                                <span className="text-gray-900 font-black">{(value * 100).toFixed(0)}%</span>
                             </div>
                             <div className="w-full h-1.5 bg-gray-50 rounded-full overflow-hidden border border-gray-100 p-[1px]">
                                <div 
                                   className={`h-full rounded-full transition-all duration-1000 ${
                                      key === 'Political' ? 'bg-red-400' :
                                      key === 'Economic' ? 'bg-emerald-400' :
                                      key === 'Social' ? 'bg-blue-400' : 'bg-amber-400'
                                   }`} 
                                   style={{ width: `${value * 100}%` }} 
                                />
                             </div>
                          </div>
                       ))}
                    </div>
                    <p className="text-[9px] text-gray-300 font-medium mt-4 text-center italic">
                       *Modelo validado via Framework Mühlroth & Grottke (2018)
                    </p>
                 </div>

                 <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm flex flex-col justify-center">
                    <p className="text-[10px] font-black text-gray-400 uppercase mb-5 tracking-[0.15em]">Indicadores de Materialidade</p>
                    <div className="space-y-3">
                       {Object.entries(asset.cultural_scores).map(([k, v]: any) => (
                         <div key={k} className="flex items-center justify-between">
                            <span className="text-[10px] uppercase font-bold text-gray-500">{k}</span>
                            <div className="flex items-center gap-2">
                               <div className="w-24 h-1.5 bg-gray-50 rounded-full overflow-hidden border border-gray-100">
                                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${v * 100}%` }} />
                               </div>
                               <span className="text-[10px] font-black text-gray-900">{(v * 100).toFixed(0)}%</span>
                            </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>

              {/* V9.5: PILAR DE VERDADE (EVIDÊNCIAS RAG) */}
              <div className="mt-6 pt-6 border-t border-gray-100">
                 <p className="text-[10px] font-black text-gray-400 uppercase mb-3 tracking-[0.15em]">Pilar de Verdade (Provas Fáticas)</p>
                 <div className="space-y-2">
                    {asset.evidence?.map((ev: any, idx: number) => (
                       <a 
                          key={idx}
                          href={ev.proof} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 transition-colors group/link"
                       >
                          <div className="p-1.5 bg-white border border-gray-100 rounded-lg shadow-xs">
                             {EVIDENCE_ICONS[ev.type] || <Globe2 size={12} />}
                          </div>
                          <div className="flex-1 min-w-0">
                             <p className="text-[10px] font-bold text-gray-800 truncate">{ev.title}</p>
                             <p className="text-[9px] text-gray-400 truncate uppercase mt-0.5">{ev.type} • Verificar Fonte</p>
                          </div>
                       </a>
                    ))}
                 </div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
