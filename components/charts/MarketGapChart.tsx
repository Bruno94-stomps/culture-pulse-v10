import React from 'react';

interface MarketGapChartProps {
  alphaValue: number;
  slopeValue?: number; // V9.5: Inclinação da Curva (Momentum)
  stdDevValue?: number; // V9.5: Desvio Padrão (Filtro de Ruído)
  sectorName: string;
  lensType: string;
  predictionMode?: 'none' | 'competitor' | 'economic'; // V9.6: Motor Contrafactual
}

/**
 * Componente Visual de Benchmark Cultural (V9.6 - Contrafactual Edition)
 * Traduz a "Física do Momentum" e Projeções de Cenário.
 */
const MarketGapChart: React.FC<MarketGapChartProps> = ({ 
  alphaValue, 
  slopeValue = 0, 
  stdDevValue = 0, 
  sectorName, 
  lensType,
  predictionMode = 'none'
}) => {
  const alphaPercent = (alphaValue * 100).toFixed(0);
  const isHighSlope = slopeValue > 0.05;
  const isStable = stdDevValue < 0.2;
  
  // Lógica de Inflexão (V9.5)
  const isInflexion = isHighSlope && isStable;

  // 🔮 [V9.6] Lógica Contrafactual (Delta de Impacto)
  const scenarios = {
    'none': { label: 'Baseline', alpha: 0, slope: 0, color: '#8b5cf6', description: 'Visão atual do mercado.' },
    'competitor': { label: 'Risco Concorrente', alpha: -0.15, slope: -0.05, color: '#ef4444', description: 'Simulação: Ataque via Mídia Massiva.' },
    'economic': { label: 'Oportunidade Econômica', alpha: 0.25, slope: 0.12, color: '#10b981', description: 'Simulação: Choque de Necessidade (Cluster Y).' }
  };

  const activeScenario = scenarios[predictionMode];

  // Lógica de Labels baseada na Lente (Storytelling Lenses)
  const lensLabels: Record<string, { label: string, strategy: string, description: string }> = {
    'Ação': { 
      label: 'Velocidade de ROI', 
      strategy: 'Escalonamento Imediato',
      description: 'FOCO: Capturar momentum antes da saturação.' 
    },
    'Exploração': { 
      label: 'Discovery Yield', 
      strategy: 'Oceano Azul / Ruptura',
      description: 'FOCO: Territórios onde o mercado é cego.' 
    },
    'Proteção': { 
      label: 'Saúde de Médio Prazo', 
      strategy: 'Blindagem de Território',
      description: 'FOCO: Minimizar volatilidade e reter audiência.' 
    }
  };

  const currentLensKey = (Object.keys(lensLabels).find(key => lensType.includes(key)) || 'Exploração');
  const currentLens = lensLabels[currentLensKey];

  // Composição de Natureza do Sinal (Taxonomia V9.5)
  const getNatureComposition = (alpha: number, slope: number) => {
    if (alpha > 0.7 && slope > 0.08) return { main: 'Inflexão Alpha', sub: 'Tendência em Expansão Exponencial', color: 'text-emerald-500' };
    if (alpha > 0.4) return { main: 'Sinal Consolidado', sub: 'Crescimento Linear / Baixo Risco', color: 'text-violet-500' };
    return { main: 'Ruído de Nicho', sub: 'Volatilidade Alta / Sem Tração', color: 'text-gray-400' };
  };

  const nature = getNatureComposition(alphaValue, slopeValue);

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm space-y-6 relative overflow-hidden group">
      {/* Badge de Inflexão (V9.5) */}
      {isInflexion && (
        <div className="absolute top-0 left-0 bg-emerald-500 text-white text-[10px] font-black px-4 py-1 rounded-br-xl shadow-lg z-20">
          TOP ALPHAS: INFLEXÃO DETECTADA
        </div>
      )}

      {predictionMode !== 'none' && (
        <div className={`absolute top-0 right-0 px-4 py-1 rounded-bl-xl text-[10px] font-black uppercase text-white ${predictionMode === 'competitor' ? 'bg-red-500' : 'bg-emerald-500'} animate-pulse`}>
          Modo Projeção: {activeScenario.label}
        </div>
      )}

      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">{currentLens.label}</h3>
            {isInflexion && <span className="bg-emerald-100 text-emerald-600 text-[9px] px-2 py-0.5 rounded-full font-black uppercase">Ponto de Inflexão</span>}
          </div>
          <p className="text-lg font-bold text-gray-900">{sectorName || "Global Market"}</p>
          <p className="text-[10px] text-gray-500 italic">{currentLens.description}</p>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-1">
            <span className={`text-3xl font-black ${predictionMode !== 'none' ? 'opacity-50 blur-[1px]' : 'text-violet-600'}`}>+{alphaPercent}%</span>
            {predictionMode !== 'none' && (
              <span className={`text-3xl font-black ml-2 ${predictionMode === 'competitor' ? 'text-red-500' : 'text-emerald-500'}`}>
                → +{((alphaValue + activeScenario.alpha) * 100).toFixed(0)}%
              </span>
            )}
            {isHighSlope && <span className="text-emerald-500 font-bold text-sm">↑</span>}
          </div>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-tighter">Cultural Alpha (α)</p>
        </div>
      </div>

      <div className="relative h-44 w-full mt-4 bg-gray-50/50 rounded-xl overflow-hidden pt-4 border border-gray-50">
        <div className="absolute bottom-10 left-0 right-0 h-px border-t border-dashed border-gray-200" />
        
        <svg className="w-full h-full" viewBox="0 0 400 150" preserveAspectRatio="none">
          {/* Linha de Base (Sombra se em predição) */}
          <path 
            d={`M 0 140 Q 200 ${140 - (alphaValue * 80)} 400 ${140 - (alphaValue * 120 + (slopeValue * 100))}`}
            fill="none" 
            stroke={isInflexion ? "#10b981" : "#8b5cf6"}
            strokeWidth="3"
            strokeDasharray={predictionMode !== 'none' ? "5,5" : "none"}
            className="opacity-40"
          />
          
          {/* Linha de Projeção (V9.6) */}
          {predictionMode !== 'none' && (
            <path 
              d={`M 0 140 Q 200 ${140 - ((alphaValue + activeScenario.alpha * 0.5) * 80)} 400 ${140 - ((alphaValue + activeScenario.alpha) * 120 + ((slopeValue + activeScenario.slope) * 100))}`}
              fill="none" 
              stroke={activeScenario.color}
              strokeWidth="4"
              className="animate-in fade-in slide-in-from-left duration-1000"
            />
          )}

          {/* Área de Incerteza (Sombra) */}
          {predictionMode !== 'none' && (
            <path 
                d={`M 0 140 L 400 ${140 - ((alphaValue + activeScenario.alpha + 0.1) * 120)} L 400 ${140 - ((alphaValue + activeScenario.alpha - 0.1) * 120)} Z`}
                fill={activeScenario.color}
                fillOpacity="0.05"
            />
          )}
        </svg>

        <div className="absolute bottom-2 left-4 flex gap-4 text-[9px] font-bold uppercase text-gray-400">
          <p>Slope: {slopeValue.toFixed(4)}</p>
          <p>StdDev: {stdDevValue.toFixed(2)}</p>
        </div>

        <div className="absolute right-4 bottom-2 bg-white/90 backdrop-blur-sm border border-gray-100 p-2 rounded-lg shadow-sm">
          <p className="text-[8px] font-black text-gray-400 uppercase mb-1">Estratégia:</p>
          <p className={`text-[10px] font-bold ${isInflexion ? 'text-emerald-600' : 'text-violet-600'}`}>
            {currentLens.strategy}
          </p>
        </div>
      </div>
      
      <div className="pt-2 border-t border-gray-50">
        <p className={`text-xs font-black uppercase ${nature.color}`}>{nature.main}</p>
        <p className="text-[10px] text-gray-500 font-medium">{nature.sub}</p>
      </div>
    </div>
  );
};

export default MarketGapChart;
