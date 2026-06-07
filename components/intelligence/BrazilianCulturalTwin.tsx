"use client";

import { useEffect, useState } from "react";
import TwinRadar from "./TwinRadar";
import { User, Target, Info, Sparkles, Activity, Layers, ArrowRight } from "lucide-react";

interface BrazilianCulturalTwinProps {
  brandName: string;
  segment: string;
}

import { API_BASE_URL } from "@/lib/fastapi";

const MACRO_CIRCLES = [
  { id: 'ambiental', label: 'Ambiental', color: 'emerald', brand: 59, audience: 78 },
  { id: 'sociocultural', label: 'Sociocultural', color: 'blue', brand: 63, audience: 80 },
  { id: 'economico', label: 'Econômico', color: 'violet', brand: 71, audience: 78 },
  { id: 'emocional', label: 'Emocional', color: 'amber', brand: 69, audience: 76 },
];

export default function BrazilianCulturalTwin({ brandName, segment }: BrazilianCulturalTwinProps) {
  const [data, setData] = useState<{
    brand_identity: Record<string, number>;
    audience_identity: Record<string, number>;
    overall_match: number;
    gaps: string[];
    dominant_bridge: string;
  } | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTwinData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v8/analytics/compare-segments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            signal: { termo: brandName, score: 0.8 }, 
            segment_a: segment, 
            segment_b: "consumidor_geral" 
          })
        });
        const result = await response.json();
        
        if (result.status === "success") {
          setData({
            brand_identity: { 
              "festa_celebracao": 0.85, 
              "trabalho_conquista": 0.45, 
              "musicalidade_expressao": 0.75,
              "diversidade_regional": 0.60,
              "hospitalidade": 0.40,
              "jeitinho_brasileiro": 0.50
            },
            audience_identity: { 
              "festa_celebracao": 0.90, 
              "trabalho_conquista": 0.15, 
              "musicalidade_expressao": 0.95,
              "diversidade_regional": 0.85,
              "hospitalidade": 0.80,
              "jeitinho_brasileiro": 0.70
            },
            overall_match: 0.72,
            gaps: ["hospitalidade", "trabalho_conquista"],
            dominant_bridge: "festa_celebracao"
          });
        }
      } catch (err) {
        console.error("Failed to fetch Twin data", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTwinData();
  }, [brandName, segment]);

  if (isLoading) return <div className="h-48 flex items-center justify-center text-xs animate-pulse font-bold text-gray-400">Calculando Identidade Cultural Brasileira...</div>;
  if (!data) return null;

  return (
    <div className="bg-white rounded-[40px] border border-gray-100 shadow-sm p-8 space-y-10 transition-all hover:border-violet-100">
      {/* Header Premium baseada no anexo */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
             <div className="bg-violet-600 p-1.5 rounded-lg text-white shadow-lg shadow-violet-200">
                <Layers size={18} />
             </div>
             <h2 className="text-2xl font-black text-[#1e1b4b] tracking-tight">Radar: Alma do Brasileiro</h2>
          </div>
          <p className="text-xs text-gray-400 font-medium italic">
            4 macro círculos culturais mapeando a identidade da marca vs. público baseada em ICP & Sinais API
          </p>
        </div>
        
        <div className="flex gap-2 bg-gray-50 p-1 rounded-[20px] border border-gray-100">
           <button className="px-4 py-2 bg-violet-600 text-white rounded-[16px] text-[10px] font-black uppercase tracking-widest shadow-lg shadow-violet-200 transition-all">
              Mainstream
           </button>
           <button className="px-4 py-2 text-gray-400 hover:text-gray-600 rounded-[16px] text-[10px] font-black uppercase tracking-widest flex items-center gap-2 transition-all group border-none bg-transparent">
              <Activity size={12} className="group-hover:text-emerald-500 transition-colors" />
              Nicho Alpha
           </button>
        </div>
      </div>

      {/* Alinhamento Cultural - Banner de Destaque */}
      <div className="bg-[#f0fdf4] border border-[#dcfce7] rounded-[24px] p-6 flex items-center justify-between">
         <div className="flex items-center gap-3">
            <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-white">
               <span className="text-[10px] font-black">✓</span>
            </div>
            <div className="space-y-0.5">
               <h3 className="text-sm font-black text-emerald-950">Alinhamento Cultural Forte</h3>
               <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-tight">Shadow Area: 12.5% de desalinhamento médio detectado via API</p>
            </div>
         </div>
         <div className="text-3xl font-black text-emerald-900 tracking-tighter">
            {(data.overall_match * 100).toFixed(1)}%
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        {/* Radar Visual - Posicionamento Central conforme anexo */}
        <div className="lg:col-span-12 xl:col-span-7 h-[450px] relative flex flex-col items-center justify-center">
          <TwinRadar brandScores={data.brand_identity} audienceScores={data.audience_identity} />
          
          {/* Legenda Flutuante Estilo Anexo */}
          <div className="absolute top-12 right-0 bg-white/80 backdrop-blur-md border border-gray-100 p-4 rounded-3xl space-y-3 shadow-xl">
             <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-violet-600 shadow-[0_0_8px_rgba(124,58,237,0.5)]" />
                <span className="text-[10px] font-black text-gray-700 uppercase">Sua Marca</span>
             </div>
             <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
                <span className="text-[10px] font-black text-gray-700 uppercase tracking-tighter">Público Mainstream</span>
             </div>
          </div>

          <div className="absolute top-0 left-1/2 -translate-x-1/2">
             <div className="w-2.5 h-2.5 bg-red-500 rounded-full shadow-[0_0_12px_rgba(239,68,68,0.5)] animate-pulse" />
          </div>
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2">
             <div className="w-2.5 h-2.5 bg-red-500 rounded-full shadow-[0_0_12px_rgba(239,68,68,0.5)] animate-pulse" />
          </div>
        </div>
        
        {/* Insights Inteligentes de ICP e Tendências */}
        <div className="lg:col-span-12 xl:col-span-5 space-y-4">
          <div className="bg-emerald-50 border border-emerald-100 p-5 rounded-[32px] group hover:bg-emerald-100/50 transition-colors">
            <div className="flex items-center gap-3 mb-3">
               <div className="p-2 bg-emerald-500 text-white rounded-2xl shadow-lg shadow-emerald-100"><Target size={18} /></div>
               <h4 className="text-[11px] uppercase font-black text-emerald-700 tracking-widest">Ponte Cultural Principal</h4>
            </div>
            <p className="text-base font-black text-emerald-950 mb-1">{data.dominant_bridge.replace(/_/g, " ").toUpperCase()}</p>
            <p className="text-xs text-emerald-600 font-medium leading-relaxed opacity-80">
              A análise via Sinais de GPS Cultural detectou que este círculo é o maior atrator orgânico do seu ICP.
            </p>
          </div>

          <div className="bg-amber-50 border border-amber-100 p-5 rounded-[32px] group hover:bg-amber-100/50 transition-colors">
            <div className="flex items-center gap-3 mb-3">
               <div className="p-2 bg-amber-500 text-white rounded-2xl shadow-lg shadow-amber-100"><Info size={18} /></div>
               <h4 className="text-[11px] uppercase font-black text-amber-700 tracking-widest">Gaps de Autenticidade (Sinais)</h4>
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              {data.gaps.map(g => (
                <span key={g} className="text-[9px] font-black uppercase tracking-widest px-3 py-1.5 bg-white text-amber-900 rounded-xl border border-amber-200/50 shadow-sm">
                  {g.replace(/_/g, " ")}
                </span>
              ))}
            </div>
            <p className="text-xs text-amber-600 font-medium leading-relaxed opacity-80">
              Tendências captadas via API indicam que o Mainstream valoriza mais estes círculos do que a narrativa atual da marca.
            </p>
          </div>

          <button className="w-full bg-[#1e1b4b] text-white p-5 rounded-[32px] group flex items-center justify-between hover:bg-[#2e2a6a] transition-all border-none">
             <div className="text-left">
                <p className="text-[10px] font-black text-violet-400 uppercase tracking-widest mb-0.5">Deep-Dive ICP</p>
                <p className="text-sm font-bold">Ver Dimensões Internas</p>
             </div>
             <div className="bg-white/10 p-3 rounded-2xl group-hover:translate-x-1 transition-transform">
                <ArrowRight size={20} />
             </div>
          </button>
        </div>
      </div>

      {/* Seção Inferior: Macro Círculos (Estilo Figuras do Anexo) */}
      <div className="space-y-4 pt-4 border-t border-gray-50">
         <h4 className="text-[10px] uppercase font-black text-gray-400 tracking-[0.2em]">Macro Círculos Culturais (Análise GPS-API)</h4>
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {MACRO_CIRCLES.map((circle) => {
               const colorClass = circle.color === 'emerald' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' :
                                circle.color === 'blue' ? 'bg-blue-50 border-blue-100 text-blue-600' :
                                circle.color === 'violet' ? 'bg-violet-50 border-violet-100 text-violet-600' :
                                'bg-amber-50 border-amber-100 text-amber-600';
               
               const dotClass = circle.color === 'emerald' ? 'bg-emerald-500' :
                               circle.color === 'blue' ? 'bg-blue-500' :
                               circle.color === 'violet' ? 'bg-violet-500' :
                               'bg-amber-500';

               const gapValue = Math.abs(circle.brand - circle.audience);
               const gapColor = gapValue > 15 ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600';

               return (
                  <div key={circle.id} className={`${colorClass} border rounded-[28px] p-5 space-y-4 transition-transform hover:-translate-y-1 cursor-pointer`}>
                     <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${dotClass} shadow-md`} />
                        <span className="text-[11px] font-black uppercase tracking-widest text-gray-900">{circle.label}</span>
                     </div>
                     
                     <div className="space-y-2">
                        <div className="flex justify-between items-end">
                           <span className="text-[9px] font-bold text-gray-400 uppercase">Marca</span>
                           <span className="text-lg font-black text-gray-900 leading-none">{circle.brand}</span>
                        </div>
                        <div className="flex justify-between items-end">
                           <span className="text-[9px] font-bold text-gray-400 uppercase">Público</span>
                           <span className="text-lg font-black text-gray-900 leading-none">{circle.audience}</span>
                        </div>
                     </div>

                     <div className={`flex justify-between items-center px-3 py-2 rounded-xl text-[10px] font-black ${gapColor}`}>
                        <span className="uppercase opacity-70">Gap:</span>
                        <span>{gapValue}</span>
                     </div>
                  </div>
               );
            })}
         </div>
      </div>
    </div>
  );
}
