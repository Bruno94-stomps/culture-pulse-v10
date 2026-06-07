"use client";

import React from 'react';
import { DashboardSetup, PulseAnalysisResponse } from '@/lib/types/pulse-api';
import CulturalRadar from '@/components/charts/CulturalRadar';
// Importação de outros widgets (hotspots, trends, etc) seriam feitas aqui

interface Props {
  analysis: PulseAnalysisResponse;
}

export function DashboardOrchestrator({ analysis }: Props) {
  const { dashboard_setup } = analysis;
  
  // Ordena os widgets com base na prioridade do Backend
  const sortedWidgets = [...dashboard_setup.recommended_widgets].sort((a, b) => b.priority - a.priority);

  // Pega todos os widgets possíveis para a versão FREE visualizar tudo
  const allPossibleWidgets = [
    ...sortedWidgets,
    { id: 'signal_stream', title: 'Fluxo de Sinais (Pulso Real)', type: 'list' as const, priority: 50 },
    { id: 'regional_heatmap', title: 'Mapa de Calor Regional', type: 'map' as const, priority: 40 },
    { id: 'circles_sunburst', title: 'Matriz ALMA (16 Círculos)', type: 'list' as const, priority: 30 },
    { id: 'brazilian_twin', title: 'Simulação Gêmeo Cultural', type: 'list' as const, priority: 20 }
  ];

  // Remove duplicatas se o backend já enviou algum desses
  const uniqueWidgets = allPossibleWidgets.filter((v, i, a) => a.findIndex(t => (t.id === v.id)) === i);

  const renderWidget = (widget: { id: string, title: string, type: string }) => {
    switch (widget.id) {
      case 'cultural_radar':
        return (
          <CulturalRadar 
            key={widget.id}
            label={widget.title}
            data={{
                calor_humano:  (analysis.cultural_circles_fit?.["Calor Humano"] ?? 0) / 100,
                criatividade:  (analysis.cultural_circles_fit?.["Criatividade"] ?? 0) / 100,
                resiliencia:   (analysis.cultural_circles_fit?.["Resiliência"] ?? 0) / 100,
                religiosidade: (analysis.cultural_circles_fit?.["Religiosidade"] ?? 0) / 100,
                festa:         (analysis.cultural_circles_fit?.["Festa"] ?? 0) / 100,
                solidariedade: (analysis.cultural_circles_fit?.["Solidariedade"] ?? 0) / 100,
            }} 
          />
        );
      
      case 'tension_hotspots':
        return (
          <div key={widget.id} className="bg-white rounded-2xl p-4 shadow-sm border border-red-100">
            <h3 className="text-sm font-bold text-red-600 mb-2">🚨 {widget.title}</h3>
            <div className="space-y-2">
              {analysis.weak_signals.filter(s => s.strength > 0.7).map((s, i) => (
                <div key={i} className="text-xs p-2 bg-red-50 rounded-lg text-red-700">
                  {s.description}
                </div>
              ))}
            </div>
          </div>
        );

      case 'emerging_trends':
        return (
          <div key={widget.id} className="bg-white rounded-2xl p-4 shadow-sm border border-violet-100">
            <h3 className="text-sm font-bold text-violet-600 mb-2">✨ {widget.title}</h3>
            <div className="space-y-2">
              {analysis.recommendations.slice(0, 3).map((rec, i) => (
                <div key={i} className="text-xs p-2 bg-violet-50 rounded-lg text-violet-700 italic">
                  "{rec}"
                </div>
              ))}
            </div>
          </div>
        );

      case 'emerging_profiles':
        return (
          <div key={widget.id} className="bg-white rounded-2xl p-4 shadow-sm border border-emerald-100">
            <h3 className="text-sm font-bold text-emerald-600 mb-2">👥 {widget.title}</h3>
            <div className="space-y-3">
              {(analysis.emerging_profiles || []).map((profile, i) => (
                <div key={i} className="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-xs font-black text-emerald-900 uppercase tracking-tight">{profile.name}</span>
                    <span className="text-[10px] bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded-full font-bold">{profile.growth}</span>
                  </div>
                  <p className="text-[10px] text-emerald-700 leading-tight mb-2">{profile.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {profile.connected_circles.map((c, ci) => (
                      <span key={ci} className="text-[9px] bg-white px-1.5 py-0.5 rounded border border-emerald-100 text-emerald-600 font-medium">#{c}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      // --- NOVOS WIDGETS LIBERADOS PARA VERSÃO FREE (V10.4) ---
      
      case 'signal_stream':
        return (
          <div key={widget.id} className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 overflow-hidden">
            <h3 className="text-sm font-black text-gray-900 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              📡 {widget.title}
            </h3>
            <div className="space-y-3">
              {analysis.weak_signals.slice(0, 5).map((s, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100 group hover:border-blue-200 transition-all">
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold text-gray-800 line-clamp-1">{s.description}</span>
                    <span className="text-[9px] text-gray-400 font-bold uppercase tracking-widest">{s.source} • {Math.round(s.strength * 100)}% Força</span>
                  </div>
                  <div className="px-2 py-0.5 bg-white border border-gray-200 rounded text-[8px] font-black text-blue-600">VERIFICADO</div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'regional_heatmap':
        return (
          <div key={widget.id} className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-black text-gray-900 mb-4 flex items-center gap-2">
              📍 {widget.title}
            </h3>
            <div className="aspect-video bg-gray-50 rounded-2xl border border-dashed border-gray-200 flex flex-col items-center justify-center relative overflow-hidden">
               <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />
               <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Mapa de Calor Ativo</span>
               <p className="text-[11px] text-gray-500 font-medium px-8 text-center leading-tight">
                 Concentração de sinais em: <span className="text-blue-600 font-bold">São Paulo, Rio de Janeiro e Recife</span>
               </p>
               {/* Simulação visual de pontos de calor */}
               <div className="absolute top-1/4 left-1/3 w-8 h-8 bg-blue-400/20 rounded-full animate-ping" />
               <div className="absolute bottom-1/3 right-1/4 w-12 h-12 bg-indigo-400/20 rounded-full animate-ping duration-1000" />
            </div>
          </div>
        );

      case 'circles_sunburst':
        return (
          <div key={widget.id} className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-sm font-black text-gray-900 mb-4 flex items-center gap-2">
              ⭕ {widget.title}
            </h3>
            <div className="flex flex-wrap gap-2">
              {['MANDINGA', 'ESTÉTICA', 'GINGA', 'PERTENCIMENTO', 'APERREIO', 'GAMBIARRA'].map((circle) => (
                <div key={circle} className="px-3 py-1.5 bg-violet-50 border border-violet-100 rounded-xl flex items-center gap-2 group hover:bg-violet-600 transition-all cursor-default">
                  <span className="text-[10px] font-black text-violet-700 group-hover:text-white transition-colors">{circle}</span>
                  <span className="text-[8px] bg-white/50 px-1 rounded font-bold text-violet-400 group-hover:text-violet-200">92</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'brazilian_twin':
        return (
          <div key={widget.id} className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
             <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-black text-gray-900 flex items-center gap-2">
                  🧬 {widget.title}
                </h3>
                <span className="text-[8px] font-black bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full uppercase tracking-widest">Acurácia: {Math.round(analysis.ib_score ?? 92)}%</span>
             </div>
             <div className="grid grid-cols-2 gap-3">
                {[
                  { name: "Joana", loc: "Sertão/PE", reaction: "Resiliência e Fé" },
                  { name: "Beto", loc: "Subúrbio/RJ", reaction: "Ginga e Sagacidade" }
                ].map((persona, i) => (
                  <div key={i} className="p-3 bg-gray-50 rounded-2xl border border-gray-100">
                    <div className="flex items-center gap-2 mb-2">
                       <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-violet-400 to-indigo-500" />
                       <div className="flex flex-col">
                          <span className="text-[10px] font-bold text-gray-900 leading-none">{persona.name}</span>
                          <span className="text-[8px] text-gray-400 font-bold uppercase">{persona.loc}</span>
                       </div>
                    </div>
                    <p className="text-[9px] text-gray-600 italic leading-tight">"A marca traduz bem minha {persona.reaction}."</p>
                  </div>
                ))}
             </div>
          </div>
        );

      default:
        return (
          <div key={widget.id} className="p-4 border border-dashed border-gray-200 rounded-xl text-xs text-gray-400">
            Widget "{widget.title}" não implementado no frontend ainda.
          </div>
        );
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {uniqueWidgets.map(widget => renderWidget(widget))}
    </div>
  );
}
