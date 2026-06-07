import React from 'react';
import MarketGapChart from './MarketGapChart';

const MarketGapChartTest = () => {
  return (
    <div className="p-10 bg-gray-100 min-h-screen space-y-10">
      <h1 className="text-2xl font-bold mb-6">Teste de Visualização Alpha Slope (V9.5)</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Caso 1: Inflexão Alpha (Lente Exploração) */}
        <div className="space-y-2">
          <p className="text-sm font-bold text-gray-500 uppercase">Cenário 1: Inflexão / Oceano Azul</p>
          <MarketGapChart 
            alphaValue={0.85} 
            slopeValue={0.12} 
            stdDevValue={0.05} 
            sectorName="Cosméticos Naturais" 
            lensType="Exploração" 
          />
        </div>

        {/* Caso 2: Momentum de Ação (Lente Ação) */}
        <div className="space-y-2">
          <p className="text-sm font-bold text-gray-500 uppercase">Cenário 2: Aceleração / ROI</p>
          <MarketGapChart 
            alphaValue={0.45} 
            slopeValue={0.09} 
            stdDevValue={0.15} 
            sectorName="Varejo de Moda" 
            lensType="Ação" 
          />
        </div>

        {/* Caso 3: Estabilidade / Risco (Lente Proteção) */}
        <div className="space-y-2">
          <p className="text-sm font-bold text-gray-500 uppercase">Cenário 3: Estabilidade / Blindagem</p>
          <MarketGapChart 
            alphaValue={0.30} 
            slopeValue={0.01} 
            stdDevValue={0.45} 
            sectorName="Serviços Financeiros" 
            lensType="Proteção" 
          />
        </div>
      </div>
    </div>
  );
};

export default MarketGapChartTest;
