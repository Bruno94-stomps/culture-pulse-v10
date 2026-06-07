"use client";

import React from 'react';

interface Scenario {
  horizon: string;
  title: string;
  description: string;
  probability: number;
  impact: 'positive' | 'negative' | 'neutral';
  indicators: string[];
}

interface FuturesTimelineProps {
  scenarios: Scenario[];
}

export default function FuturesTimeline({ scenarios }: FuturesTimelineProps) {
  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
        <span className="text-4xl mb-3 opacity-50">🔮</span>
        <p className="text-sm text-gray-400">Nenhum cenário preditivo gerado para este sinal.</p>
      </div>
    );
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive': return 'bg-emerald-50 text-emerald-700 border-emerald-100';
      case 'negative': return 'bg-red-50 text-red-700 border-red-100';
      default: return 'bg-blue-50 text-blue-700 border-blue-100';
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'positive': return '↗️';
      case 'negative': return '↘️';
      default: return '➡️';
    }
  };

  return (
    <div className="relative">
      {/* Linha vertical centralizada */}
      <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-violet-200 via-violet-100 to-transparent transform -translate-x-1/2 hidden md:block" />

      <div className="space-y-12">
        {scenarios.map((s, i) => (
          <div key={i} className={`relative flex flex-col md:flex-row items-center ${i % 2 === 0 ? 'md:flex-row-reverse' : ''}`}>
            {/* Ponto na timeline */}
            <div className="absolute left-8 md:left-1/2 w-4 h-4 rounded-full bg-violet-600 border-4 border-white shadow-sm transform -translate-x-1/2 z-10" />

            {/* Content Card */}
            <div className="w-full md:w-[45%] pl-16 md:pl-0">
              <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow group">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-[10px] font-black uppercase tracking-widest text-violet-600 bg-violet-50 px-2.5 py-1 rounded-full">
                    {s.horizon}
                  </span>
                  <div className="flex items-center gap-1.5 font-bold text-xs">
                    <span className="text-gray-400">Prob:</span>
                    <span className="text-gray-900">{(s.probability * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <h3 className="text-lg font-bold text-gray-800 mb-2 group-hover:text-violet-700 transition-colors">
                  {s.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed mb-4">
                  {s.description}
                </p>

                <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold mb-4 ${getImpactColor(s.impact)}`}>
                  <span>Impacto {s.impact.toUpperCase()}:</span>
                  <span>{getImpactIcon(s.impact)}</span>
                </div>

                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Sinais Monitorar:</p>
                  <div className="flex flex-wrap gap-2">
                    {s.indicators.map((ind, j) => (
                      <span key={j} className="text-[10px] bg-gray-50 text-gray-500 px-2 py-0.5 rounded-lg border border-gray-100 italic">
                        👀 {ind}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Spacer para o outro lado da timeline em MD */}
            <div className="hidden md:block md:w-[45%]" />
          </div>
        ))}
      </div>
    </div>
  );
}
