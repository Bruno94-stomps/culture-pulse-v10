"use client";

import { useState } from "react";
import { API_BASE_URL } from "@/lib/fastapi";

interface GeographicSignal {
  city: string;
  state: string;
  region: string;
  coordinates: [number, number];
  intensity: number;
  sentiment: number;
  main_circle: string;
  trending_topics: string[];
}

interface MatchResult {
  match_score: number;
  authenticity_score: number;
  sentiment_alignment: number;
  risks: string[];
  strengths: string[];
  suggestions: string[];
  detected_circles: string[];
  geographic_spread?: GeographicSignal[];
  suggested_sources?: string[];
  strategic_context_applied?: string;
}

import RegionalHeatmap from "../analytics/RegionalHeatmap";

export default function CampaignMatchTester({ brandName, segment }: { brandName: string, segment: string }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [showMap, setShowMap] = useState(false);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev => 
      prev.includes(source) ? prev.filter(s => s !== source) : [...prev, source]
    );
  };

  const handleAnalyze = async () => {
    if (!text || text.length < 10) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v8/analysis/campaign-match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: brandName,
          segment: segment,
          campaign_text: text,
          target_circles: ["Urban Culture", "Sport Performance", "Eco Conscious"]
        }),
      });
      const data = await response.json();
      setResult(data);
      if (data.suggested_sources) {
        setSelectedSources(data.suggested_sources);
      }
    } catch (error) {
      console.error("Erro ao analisar campanha:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden flex flex-col md:flex-row">
        {/* Input de Texto */}
        <div className="flex-1 p-6 border-r border-gray-50 bg-gray-50/20">
          <label className="block text-[10px] font-black text-violet-600 uppercase tracking-widest mb-3">
            Simulador de Aderência Cultural
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Cole aqui o texto da sua campanha, post ou roteiro para validar o match cultural..."
            className="w-full h-40 bg-white border border-gray-200 rounded-2xl p-4 text-sm focus:outline-none focus:border-violet-400 focus:ring-4 focus:ring-violet-500/5 transition-all resize-none font-medium"
          />
          
          {/* Nova Seção de Seleção de APIs Sugeridas */}
          {result?.suggested_sources && (
            <div className="mt-4 animate-in fade-in slide-in-from-top-2">
              <p className="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                📡 APIs Recomendadas para Coleta em Tempo Real
                <span className="text-violet-600 bg-violet-50 px-2 py-0.5 rounded-full">{result.strategic_context_applied}</span>
              </p>
              <div className="flex flex-wrap gap-2">
                {["youtube", "reddit", "instagram", "threads", "spotify", "google_trends", "news"].map((source) => {
                  const isSuggested = result.suggested_sources?.includes(source);
                  const isSelected = selectedSources.includes(source);
                  return (
                    <button
                      key={source}
                      onClick={() => handleSourceToggle(source)}
                      className={`text-[9px] px-3 py-1.5 rounded-xl font-bold uppercase transition-all flex items-center gap-1.5 border ${
                        isSelected 
                          ? 'bg-violet-600 border-violet-600 text-white shadow-md shadow-violet-200' 
                          : isSuggested 
                            ? 'bg-violet-50 border-violet-200 text-violet-600' 
                            : 'bg-white border-gray-100 text-gray-400 opacity-60'
                      }`}
                    >
                      {source.replace('_', ' ')}
                      {isSuggested && !isSelected && <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-pulse"></span>}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || text.length < 10}
            className="w-full mt-4 bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 text-white font-bold py-3 rounded-xl shadow-lg shadow-violet-200 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>Validar Match Cultural</span>
                <span className="text-lg leading-none">⚡</span>
              </>
            )}
          </button>
        </div>

        {/* Resultados */}
        <div className="flex-1 p-6 flex flex-col justify-center min-h-[300px]">
          {result ? (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Match Score</p>
                  <p className="text-4xl font-black text-gray-900">{(result.match_score * 100).toFixed(0)}%</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="text-right">
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Autenticidade</p>
                    <p className={`text-xl font-bold ${result.authenticity_score > 0.6 ? 'text-emerald-500' : 'text-amber-500'}`}>
                      {(result.authenticity_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  {result.geographic_spread && (
                    <button 
                      onClick={() => setShowMap(!showMap)}
                      className={`text-[9px] font-bold uppercase px-3 py-1 rounded-full border transition-all ${
                        showMap ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-violet-600 border-violet-100 hover:border-violet-300'
                      }`}
                    >
                      {showMap ? "Ocultar Mapa" : "Ver Dispersão Regional"}
                    </button>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-emerald-50 rounded-2xl border border-emerald-100">
                    <p className="text-[10px] font-black text-emerald-600 uppercase mb-2">Pontos Fortes</p>
                    <ul className="text-[10px] space-y-1 text-emerald-800 font-medium italic">
                      {result.strengths.slice(0, 2).map((s, i) => <li key={i}>✓ {s}</li>)}
                    </ul>
                  </div>
                  <div className="p-3 bg-red-50 rounded-2xl border border-red-100">
                    <p className="text-[10px] font-black text-red-600 uppercase mb-2">Riscos</p>
                    <ul className="text-[10px] space-y-1 text-red-800 font-medium italic">
                      {result.risks.slice(0, 2).map((r, i) => <li key={i}>⚠ {r}</li>)}
                    </ul>
                  </div>
                </div>

                <div>
                  <p className="text-[10px] font-black text-violet-600 uppercase tracking-widest mb-2">Sugestões de Ajuste</p>
                  <div className="space-y-2">
                    {result.suggestions.map((s, i) => (
                      <div key={i} className="flex gap-2 text-xs text-gray-600 border-l-2 border-violet-200 pl-3 py-0.5">
                        <span className="font-bold text-violet-600">PRO:</span>
                        {s}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center opacity-30">
              <div className="text-6xl mb-4">🧪</div>
              <p className="text-sm font-bold text-gray-400">
                Aguardando texto da campanha...<br/>
                <span className="text-xs font-normal">O motor V9.1 analisará léxico, gírias e autenticidade.</span>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Mapa de Dispersão Integrado */}
      {showMap && result?.geographic_spread && (
        <div className="animate-in fade-in zoom-in-95 duration-500">
          <RegionalHeatmap 
            data={result.geographic_spread.map(s => ({
              region: s.region, 
              cvi_score: s.intensity
            }))} 
          />
        </div>
      )}
    </div>
  );
}
