"use client";

import { useState } from "react";
import { Send, Bot, CheckCircle, AlertCircle } from "lucide-react";

interface BriefingInputProps {
  onRefine: (text: string) => Promise<{
    suggestions: { editable_keywords: string[] };
    next_steps: { questions: any[] };
  }>;
}

export default function BriefingInput({ onRefine }: BriefingInputProps) {
  const [text, setText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentSource, setCurrentSource] = useState<string | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<"idle" | "success" | "asking">("idle");

  const sources = [
    { name: "YouTube", label: "Mapeando vídeos e momentum cultural..." },
    { name: "Reddit", label: "Capturando veracidade em comunidades..." },
    { name: "Spotify", label: "Analisando tendências sonoras brasileiras..." },
    { name: "Google Trends", label: "Validando volumes de busca real..." },
  ];

  const handleRefine = async () => {
    if (!text || isAnalyzing) return;
    setIsAnalyzing(true);
    setAnalysisStatus("idle");

    // Efeito visual de busca em tempo real nas redes
    let sourceIdx = 0;
    const sourceInterval = setInterval(() => {
      setCurrentSource(sources[sourceIdx].label);
      sourceIdx = (sourceIdx + 1) % sources.length;
    }, 1500);

    try {
      const result = await onRefine(text);
      clearInterval(sourceInterval);
      setCurrentSource(null);
      if (result.next_steps.questions.length > 0) {
        setAnalysisStatus("asking");
      } else {
        setAnalysisStatus("success");
      }
    } catch (error) {
      clearInterval(sourceInterval);
      setCurrentSource(null);
      console.error("Refinement error:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="relative">
        <label className="block text-sm font-semibold text-gray-800 mb-2">
          Briefing Conversacional
          <span className="text-gray-400 font-normal ml-2">Descreva seu objetivo em linguagem natural</span>
        </label>
        
        <div className={`relative px-4 py-4 bg-white border-2 rounded-2xl shadow-sm transition-all overflow-hidden ${
          isAnalyzing ? "border-violet-500 ring-4 ring-violet-100" : "border-gray-100 hover:border-gray-200"
        }`}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isAnalyzing}
            placeholder="Ex: Quero lançar um novo tênis streetwear focado na periferia de SP, mas não sei qual tom de voz usar..."
            rows={4}
            className="w-full text-base text-gray-800 placeholder-gray-400 focus:outline-none resize-none bg-transparent"
          />

          <div className="flex items-center justify-between mt-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2 text-xs font-medium text-violet-600">
                <Bot size={16} className={isAnalyzing ? "animate-bounce" : ""} />
                <span>{isAnalyzing ? "Pulso Cultural coletando dados..." : "Pronto para sintetizar"}</span>
              </div>
              {isAnalyzing && currentSource && (
                <div className="text-[10px] text-gray-400 italic animate-pulse flex items-center gap-1 ml-6">
                  <span className="w-1 h-1 bg-amber-400 rounded-full"></span>
                  {currentSource}
                </div>
              )}
            </div>
            
            <button
              onClick={handleRefine}
              disabled={isAnalyzing || !text}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all ${
                isAnalyzing || !text
                  ? "bg-gray-100 text-gray-400"
                  : "bg-gradient-to-r from-violet-600 to-violet-500 text-white shadow-lg shadow-violet-200 hover:scale-105 active:scale-95"
              }`}
            >
              {isAnalyzing ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Sintetizar Briefing <Send size={16} /></>
              )}
            </button>
          </div>
        </div>

        {/* Status Indicators */}
        {analysisStatus === "success" && (
          <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-700 text-xs font-medium animate-in fade-in slide-in-from-top-2">
            <CheckCircle size={16} />
            Contexto compreendido! Sugestões de palavras-chave aplicadas.
          </div>
        )}
        
        {analysisStatus === "asking" && (
          <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-100 rounded-xl text-amber-700 text-xs font-medium animate-in fade-in slide-in-from-top-2">
            <AlertCircle size={16} />
            Para maior precisão, o motor solicita 2 respostas complementares abaixo.
          </div>
        )}
      </div>
    </div>
  );
}
