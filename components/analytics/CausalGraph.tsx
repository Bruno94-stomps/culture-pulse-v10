"use client";

import React from 'react';

interface CausalNode {
  id: string;
  label: string;
  type: 'Political' | 'Economic' | 'Social' | 'Technological';
}

interface CausalLink {
  source: string;
  target: string;
  strength: number;
}

interface CausalChain {
  chain: string[];
  total_strength: number;
}

interface CausalGraphProps {
  chains: CausalChain[];
}

export default function CausalGraph({ chains }: CausalGraphProps) {
  if (!chains || chains.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-gray-50 rounded-xl border border-dashed border-gray-200">
        <span className="text-3xl mb-2">🔭</span>
        <p className="text-sm text-gray-500">Nenhuma cadeia causal identificada no momento.</p>
      </div>
    );
  }

  // Prepara cores por categoria
  const getCategoryColor = (label: string) => {
    const l = label.toLowerCase();
    if (l.includes('polit') || l.includes('polít')) return 'bg-blue-100 text-blue-700 border-blue-200';
    if (l.includes('econ')) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    if (l.includes('soc')) return 'bg-amber-100 text-amber-700 border-amber-200';
    if (l.includes('tec')) return 'bg-violet-100 text-violet-700 border-violet-200';
    return 'bg-gray-100 text-gray-700 border-gray-200';
  };

  return (
    <div className="space-y-6">
      {chains.slice(0, 5).map((c, i) => (
        <div key={i} className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Cadeia Causal #{i+1}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Força Acumulada:</span>
              <span className="px-2 py-0.5 bg-violet-600 text-white rounded-full text-xs font-bold">
                {(c.total_strength * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-y-4">
            {c.chain.map((step, idx) => (
              <React.Fragment key={idx}>
                <div className={`px-4 py-2 rounded-lg border text-sm font-semibold shadow-sm ${getCategoryColor(step)}`}>
                  {step}
                </div>
                {idx < c.chain.length - 1 && (
                  <div className="flex flex-col items-center px-2">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-300">
                      <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-50">
            <p className="text-xs text-gray-500 italic">
              💡 <span className="font-semibold text-gray-600">Insight:</span> Uma alteração em <span className="font-bold">{c.chain[0]}</span> tende a impactar dinamicamente <span className="font-bold">{c.chain[c.chain.length-1]}</span> através desta sequência de eventos.
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
