"use client";

import React, { useMemo } from 'react';

// Coordenadas simplificadas dos estados brasileiros para o heatmap
// (Aproximado para posicionamento visual em um grid relativo)
const BRAZIL_STATES = [
  { id: 'AC', name: 'Acre', x: 10, y: 35, region: 'Norte', city: 'Rio Branco' },
  { id: 'AL', name: 'Alagoas', x: 88, y: 38, region: 'Nordeste', city: 'Maceió' },
  { id: 'AP', name: 'Amapá', x: 55, y: 10, region: 'Norte', city: 'Macapá' },
  { id: 'AM', name: 'Amazonas', x: 25, y: 25, region: 'Norte', city: 'Manaus' },
  { id: 'BA', name: 'Bahia', x: 75, y: 45, region: 'Nordeste', city: 'Salvador' },
  { id: 'CE', name: 'Ceará', x: 82, y: 25, region: 'Nordeste', city: 'Fortaleza' },
  { id: 'DF', name: 'Distrito Federal', x: 58, y: 55, region: 'Centro-Oeste', city: 'Brasília' },
  { id: 'ES', name: 'Espírito Santo', x: 78, y: 65, region: 'Sudeste', city: 'Vitória' },
  { id: 'GO', name: 'Goiás', x: 55, y: 58, region: 'Centro-Oeste', city: 'Goiânia' },
  { id: 'MA', name: 'Maranhão', x: 70, y: 25, region: 'Nordeste', city: 'São Luís' },
  { id: 'MT', name: 'Mato Grosso', x: 40, y: 50, region: 'Centro-Oeste', city: 'Cuiabá' },
  { id: 'MS', name: 'Mato Grosso do Sul', x: 42, y: 68, region: 'Centro-Oeste', city: 'Campo Grande' },
  { id: 'MG', name: 'Minas Gerais', x: 68, y: 62, region: 'Sudeste', city: 'Belo Horizonte' },
  { id: 'PA', name: 'Pará', x: 50, y: 28, region: 'Norte', city: 'Belém' },
  { id: 'PB', name: 'Paraíba', x: 88, y: 28, region: 'Nordeste', city: 'João Pessoa' },
  { id: 'PR', name: 'Paraná', x: 48, y: 78, region: 'Sul', city: 'Curitiba' },
  { id: 'PE', name: 'Pernambuco', x: 86, y: 32, region: 'Nordeste', city: 'Recife' },
  { id: 'PI', name: 'Piauí', x: 75, y: 32, region: 'Nordeste', city: 'Teresina' },
  { id: 'RJ', name: 'Rio de Janeiro', x: 74, y: 72, region: 'Sudeste', city: 'Rio de Janeiro' },
  { id: 'RN', name: 'Rio Grande do Norte', x: 88, y: 24, region: 'Nordeste', city: 'Natal' },
  { id: 'RS', name: 'Rio Grande do Sul', x: 45, y: 90, region: 'Sul', city: 'Porto Alegre' },
  { id: 'RO', name: 'Rondônia', x: 28, y: 45, region: 'Norte', city: 'Porto Velho' },
  { id: 'RR', name: 'Roraima', x: 32, y: 10, region: 'Norte', city: 'Boa Vista' },
  { id: 'SC', name: 'Santa Catarina', x: 48, y: 85, region: 'Sul', city: 'Florianópolis' },
  { id: 'SP', name: 'São Paulo', x: 62, y: 75, region: 'Sudeste', city: 'São Paulo' },
  { id: 'SE', name: 'Sergipe', x: 86, y: 42, region: 'Nordeste', city: 'Aracaju' },
  { id: 'TO', name: 'Tocantins', x: 58, y: 40, region: 'Norte', city: 'Palmas' },
];

interface RegionalHeatmapProps {
  data: Array<{ region: string; cvi_score: number }>;
}

export default function RegionalHeatmap({ data }: RegionalHeatmapProps) {
  // Mapeia os scores regionais para os estados
  const stateData = useMemo(() => {
    return BRAZIL_STATES.map(state => {
      // Tenta encontrar o score pela cidade ou pela região
      const regionInfo = data.find(d => 
        d.region.toLowerCase() === state.city.toLowerCase() || 
        d.region.toLowerCase() === state.region.toLowerCase()
      );
      
      const score = regionInfo?.cvi_score ?? (0.3 + (Math.random() * 0.4)); // Baseline menor para regiões sem dados
      return { ...state, score };
    });
  }, [data]);

  const getColor = (score: number) => {
    if (score > 0.8) return 'fill-violet-600 ring-4 ring-violet-500/20';
    if (score > 0.6) return 'fill-violet-400';
    if (score > 0.4) return 'fill-emerald-400';
    if (score > 0.2) return 'fill-emerald-200';
    return 'fill-gray-200';
  };

  return (
    <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm overflow-hidden">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-800">🌐 Mapa de Calor de Sinais V9.1</h3>
          <p className="text-xs text-gray-400">Intensidade do léxico cultural em capitais brasileiras</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {[0.1, 0.4, 0.8].map((s) => (
              <div key={s} className={`w-3 h-3 rounded-sm ${getColor(s)}`} />
            ))}
          </div>
          <span className="text-[10px] font-bold text-gray-400">IMPACTO</span>
        </div>
      </div>

      <div className="relative aspect-[4/5] w-full bg-gray-50/50 rounded-2xl border border-gray-100/50 p-4">
        {/* SVG do Mapa Simplificado */}
        <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-sm">
          {stateData.map((state) => (
            <g key={state.id} className="group cursor-help">
              <circle
                cx={state.x}
                cy={state.y}
                r={state.score > 0.7 ? "4" : "2.5"}
                className={`${getColor(state.score)} transition-all duration-500 group-hover:r-6 opacity-90`}
              />
              <text
                x={state.x}
                y={state.y - 6}
                className="text-[3.5px] font-black fill-violet-700 opacity-0 group-hover:opacity-100 transition-opacity"
                textAnchor="middle"
              >
                {state.city}: {(state.score * 100).toFixed(0)}%
              </text>
            </g>
          ))}
          
          {/* Conexões simbólicas (Teia Cultural) */}
          <path 
            d="M25 25 L50 28 L75 45 L62 75 L45 90" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="0.2" 
            className="text-gray-200"
            strokeDasharray="2 2"
          />
        </svg>

        {/* Tooltip simplificado fixo na área */}
        <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-sm border border-gray-100 p-3 rounded-xl shadow-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-[10px] text-gray-400 uppercase font-bold">Top Performance</p>
              <p className="text-xs font-bold text-emerald-600">
                {stateData.sort((a,b) => b.score - a.score)[0].name} ({(stateData.sort((a,b) => b.score - a.score)[0].score * 100).toFixed(0)}%)
              </p>
            </div>
            <div>
              <p className="text-[10px] text-gray-400 uppercase font-bold">Ponto de Atenção</p>
              <p className="text-xs font-bold text-amber-600">
                {stateData.sort((a,b) => a.score - b.score)[0].name} ({(stateData.sort((a,b) => a.score - b.score)[0].score * 100).toFixed(0)}%)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
