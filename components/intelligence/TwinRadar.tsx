"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

interface TwinRadarProps {
  brandScores: Record<string, number>;
  audienceScores: Record<string, number>;
}

export default function TwinRadar({ brandScores, audienceScores }: TwinRadarProps) {
  // Mapeamento dos 16 Círculos com seus respectivos Macro-Quadrantes (V10.4)
  const circleToQuadrant: Record<string, string> = {
    // 1. SOCIOCULTURAL
    'adaptacao_flexibilidade': 'SOCIOCULTURAL',
    'musicabilidade_expressao': 'SOCIOCULTURAL',
    'criatividade_improvisacao': 'SOCIOCULTURAL',
    'sincretismo_cultural': 'SOCIOCULTURAL',
    // 2. ECONOMICO E SISTEMICO
    'economia_informal': 'ECONÔMICO',
    'festa_luta': 'ECONÔMICO',
    'ascensao_oportunidade': 'ECONÔMICO',
    'desigualdade_solidariedade': 'ECONÔMICO',
    // 3. AMBIENTAL E ESTRUTURAL
    'natureza_coletivo': 'AMBIENTAL',
    'urbano_rural': 'AMBIENTAL',
    'diversidade_geografica': 'AMBIENTAL',
    'relacao_caos': 'AMBIENTAL',
    // 4. EMOCIONAL E COMPORTAMENTAL
    'astucia_sagacidade': 'EMOCIONAL',
    'alegria_celebracao': 'EMOCIONAL',
    'resiliencia_fe': 'EMOCIONAL',
    'legado_comunitario': 'EMOCIONAL'
  };

  // Transformar no formato Recharts + Cálculo de Tensão + Injeção de Quadrante
  const data = Object.keys(brandScores).map((circle) => {
    const brandValue = brandScores[circle] * 100;
    const audienceValue = audienceScores[circle] * 100;
    const tension = Math.abs(brandValue - audienceValue);
    const quadrant = circleToQuadrant[circle] || 'GERAL';

    return {
      subject: circle.replace(/_/g, " ").toUpperCase(),
      quadrant: quadrant,
      brand: brandValue,
      audience: audienceValue,
      tension: tension,
      fullMark: 100,
      isHighTension: tension > 35,
    };
  });

  // Cálculo de Dissonância Geral (%)
  const totalTension = data.reduce((acc, curr) => acc + curr.tension, 0);
  const dissonancePercentage = Math.round(totalTension / data.length);
  const fitStatus = dissonancePercentage < 20 ? 'Sinergia' : dissonancePercentage < 40 ? 'Desvio' : 'Dissonância';

  return (
    <div className="flex flex-col gap-4 w-full h-full">
      {/* Header de Diagnóstico (V10.4) */}
      <div className="flex items-center justify-between px-2">
        <div className="flex flex-col">
          <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Fit Cultural Global</span>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-black tracking-tighter ${dissonancePercentage > 40 ? 'text-rose-600' : 'text-emerald-600'}`}>
              {100 - dissonancePercentage}%
            </span>
            <span className={`text-[10px] font-bold uppercase ${dissonancePercentage > 40 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {fitStatus} Identificado
            </span>
          </div>
        </div>
        
        {/* Chips de Tensão Localizada */}
        <div className="flex gap-1.5 overflow-x-auto max-w-[50%] no-scrollbar px-1">
          {data.filter(d => d.isHighTension).slice(0, 2).map((d, i) => (
            <div key={i} className="flex flex-col items-end px-2 py-1 bg-amber-50 border border-amber-100 rounded-lg animate-pulse whitespace-nowrap">
               <span className="text-[7px] font-black text-amber-600 uppercase">Ponto de Tensão</span>
               <span className="text-[9px] font-bold text-amber-900">{d.subject}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="h-[400px] w-full bg-white rounded-3xl p-4 border border-gray-100 shadow-sm relative group">
        {/* Overlay de Círculos Centrais (Metodologia ALMA) */}
        <div className="absolute bottom-4 right-4 z-10 flex gap-2">
           {['SOCIOCULTURAL', 'ECONÔMICO', 'AMBIENTAL', 'EMOCIONAL'].map((q) => (
             <div key={q} className="px-2 py-0.5 bg-gray-50 border border-gray-100 rounded text-[7px] font-black text-gray-400">
               {q}
             </div>
           ))}
        </div>

        {/* Overlay de Área de Sombra */}
        <div className="absolute top-4 left-4 z-10 px-3 py-1.5 bg-white/40 backdrop-blur-md border border-white/20 rounded-xl pointer-events-none group-hover:opacity-0 transition-opacity">
           <span className="text-[9px] font-black text-gray-500 uppercase tracking-widest">Disfunção (Shadow):</span>
           <p className="text-sm font-black text-gray-900">{dissonancePercentage}%</p>
        </div>

        <ResponsiveContainer width="100%" height="100%" minHeight={400}>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
            <PolarGrid stroke="#f1f5f9" strokeWidth={2} />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={({ payload, x, y, textAnchor, stroke, radius }: any) => {
                const item = data.find(d => d.subject === payload.value);
                const isHigh = item?.isHighTension;
                const quadrant = item?.quadrant;
                
                return (
                  <g>
                    <text
                      x={x}
                      y={y}
                      textAnchor={textAnchor}
                      fill={isHigh ? "#f43f5e" : "#94a3b8"}
                      fontSize={isHigh ? 9 : 8}
                      fontWeight="black"
                      className={isHigh ? "animate-pulse" : ""}
                    >
                      {payload.value}
                    </text>
                    {/* Indicador de Quadrante (V10.4) */}
                    <text
                      x={x}
                      y={y + 10}
                      textAnchor={textAnchor}
                      fill="#cbd5e1"
                      fontSize={6}
                      fontWeight="bold"
                    >
                      {quadrant}
                    </text>
                  </g>
                );
              }}
            />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
            <Radar
              name="DNA da Marca"
              dataKey="brand"
              stroke="#8b5cf6"
              fill="#8b5cf6"
              fillOpacity={0.5}
            />
            <Radar
              name="Realidade do Público"
              dataKey="audience"
              stroke="#f5b32e" // Amber mais quente
              strokeWidth={3}
              fill="#f59e0b"
              fillOpacity={0.2}
            />
            <Tooltip 
              contentStyle={{ borderRadius: "20px", border: "1px solid #f1f5f9", boxShadow: "0 20px 25px -5px rgba(0,0,0,0.1)", padding: "12px" }}
              itemStyle={{ fontWeight: "bold", fontSize: "11px" }}
            />
            <Legend 
              verticalAlign="bottom" 
              height={36} 
              wrapperStyle={{ paddingTop: "20px", fontSize: "10px", fontWeight: "900", textTransform: "uppercase", letterSpacing: "1px" }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
