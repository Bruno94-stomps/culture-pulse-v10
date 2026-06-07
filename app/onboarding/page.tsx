"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useKeywords, DEMO_PROJECT } from "@/contexts/KeywordContext";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import ScenarioSelector from "@/components/onboarding/ScenarioSelector";
import BriefingInput from "@/components/onboarding/BriefingInput";

const SECTORS = [
  "Alimentação & Bebidas",
  "Moda & Beleza",
  "Tecnologia & Apps",
  "Entretenimento & Mídia",
  "Saúde & Bem-estar",
  "Esportes & Fitness",
  "Varejo & E-commerce",
  "Finanças & Fintech",
  "Educação",
  "Turismo & Viagem",
  "Outro",
];

const SUGGESTED_KEYWORDS = [
  "funk",
  "sertanejo",
  "sustentabilidade",
  "ia generativa",
  "cultura periférica",
  "streetwear",
  "veganismo",
  "saúde mental",
  "K-pop",
  "carnaval",
];

function OnboardingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setProject, hasKeywords } = useKeywords();

  const isDemo = searchParams.get("demo") === "true";

  const [keywordsText, setKeywordsText] = useState("");
  const [brand, setBrand] = useState("");
  const [sector, setSector] = useState(SECTORS[0]);
  const [periodDays, setPeriodDays] = useState(30);
  const [scenario, setScenario] = useState("launch");
  const [step, setStep] = useState(1); // 1: Setup, 2: Hipótese (Active Learning)

  const [activeHypothesis, setActiveHypothesis] = useState({
    x: "[Sinal Detectado]",
    y: "[Público-Alvo]",
    z: "[Tensão Cultural]",
    condition: "[Evento Acionador]"
  });

  // Se já tem keywords guardadas, pular para dashboard
  useEffect(() => {
    if (hasKeywords && !isDemo) {
      router.replace("/dashboard");
    }
  }, [hasKeywords, isDemo, router]);

  // Modo demo: pré-preencher
  useEffect(() => {
    if (isDemo) {
      setKeywordsText(DEMO_PROJECT.keywords.join(", "));
      setBrand(DEMO_PROJECT.brand);
      setSector(DEMO_PROJECT.sector);
      setActiveHypothesis({
        x: "Dumbphones / Desconexão",
        y: "Gen Z exausta",
        z: "Esgotamento Dopaminérgico Digital",
        condition: "saúde mental vire KPI de produtividade"
      });
    }
  }, [isDemo]);

  // Gerar Hipótese Inicial Baseada no Cenário (Active Learning)
  useEffect(() => {
    if (step === 2 && !isDemo) {
      const generated = {
        "launch": { x: "Uso de IAs Criativas", y: "Microempreendedores", z: "Necessidade de Produtividade em Crise", condition: "o acesso mobile for simplificado" },
        "repositioning": { x: "Busca por Ancestralidade", y: "Millennials Urbanos", z: "Crise de Identidade Globalizada", condition: "marcas regionais ganharem escala" },
        "rejuvenescence": { x: "Comunidades fechadas (Discord)", y: "Alpha Gen", z: "Fuga de Algoritmos de Massa", condition: "o custo de atenção em redes abertas saturar" },
        "crisis": { x: "Boicote por Ética", y: "Ativistas de Rede", z: "Quebra de Contrato Social", condition: "o silêncio da marca persistir" }
      }[scenario] || { x: "Comportamento X", y: "Grupo Y", z: "Tensão Z", condition: "Acontecer A" };
      
      setActiveHypothesis(generated);
    }
  }, [step, scenario]);

  const keywords = keywordsText
    .split(/[,\n]+/)
    .map((k) => k.trim())
    .filter(Boolean);

  function addSuggestion(kw: string) {
    const current = keywordsText
      .split(/[,\n]+/)
      .map((k) => k.trim())
      .filter(Boolean);
    if (!current.includes(kw)) {
      setKeywordsText([...current, kw].join(", "));
    }
  }

  async function handleStart() {
    if (keywords.length === 0) return;
    setProject({ keywords, brand, sector, periodDays });

    const createdProject = await createProject();
    if (createdProject?.id) {
      await analyzeProject(createdProject.id);
      router.push(`/dashboard?projectId=${createdProject.id}`);
      return;
    }

    router.push("/dashboard");
  }

  async function createProject() {
    const { createClient } = await import("@/lib/supabase/client");
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    const scenarioMap: Record<string, string> = {
      "launch": "lançamento de produto",
      "repositioning": "construção de marca",
      "rejuvenescence": "pesquisa de mercado",
      "crisis": "crise de reputação"
    };

    const mappedScenario = scenarioMap[scenario] || "pesquisa de mercado";

    try {
      const refineResponse = await fetch(`${FASTAPI_BASE_URL}/api/v8/analytics/consultant/refine-briefing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goal_text: `Marca: ${brand}. Setor: ${sector}. Cenário: ${mappedScenario}. Keywords: ${keywords.join(", ")}`,
          brand_name: brand,
          segment: sector,
        })
      });

      const refineResult = await refineResponse.json();
      const strategicKpis = {
        suggestions: refineResult.suggestions || {},
        dashboard_setup: refineResult.dashboard_setup || {},
        detected_context: refineResult.detected_context || {},
      };

      await supabase.from("profiles").update({
        onboarding_moment: mappedScenario,
        onboarding_segment: sector,
        onboarding_brand: brand,
      }).eq("id", user.id);

      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: `${brand} - Onboarding`,
          brand,
          keywords,
          segment: sector,
          objective: mappedScenario,
          regions: ["Brasil (Geral)"],
          audiences: ["Todos"],
          circles: [],
          period_days: periodDays,
          analysis_data: {
            onboarding: {
              strategic_kpis: strategicKpis,
              scenario,
              created_at: new Date().toISOString(),
            }
          }
        })
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Falha ao criar projeto");
      return result.data;
    } catch (error) {
      console.error("Erro ao criar projeto de onboarding:", error);
      return null;
    }
  }

  async function analyzeProject(projectId: string) {
    try {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: "POST",
      });
      if (!response.ok) {
        const result = await response.json();
        console.error("Falha ao analisar projeto:", result.error || response.statusText);
      }
    } catch (error) {
      console.error("Erro ao acionar análise do projeto:", error);
    }
  }

  async function handleRefineBriefing(text: string) {
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/v8/analytics/consultant/refine-briefing`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal_text: text, brand_name: brand, segment: sector })
      });
      
      const result = await response.json();
      if (result.status === "success" && result.suggestions?.editable_keywords) {
        setKeywordsText(result.suggestions.editable_keywords.join(", "));
      }
      return result;
    } catch (e) {
      console.error("Failed to refine briefing:", e);
      return { suggestions: { editable_keywords: [] }, next_steps: { questions: [] } };
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-950 via-violet-900 to-amber-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-violet-500 px-8 py-6 text-white text-center">
            <span className="text-xl font-extrabold block">
              Culture<span className="text-amber-300">Pulse</span> <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full font-bold">V9.5</span>
            </span>
            <h1 className="text-2xl font-bold mt-2">
              {step === 1 ? "Sincronização de Contexto" : "Formulação de Hipótese (Active Learning)"}
            </h1>
        </div>

        {step === 1 ? (
          <div className="p-8 space-y-6">
            <ScenarioSelector selectedId={scenario} onSelect={setScenario} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-black text-gray-400 uppercase">Sua Marca</label>
                <input 
                  value={brand} 
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="Ex: Natura, Nubank..."
                  className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none transition-all"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-black text-gray-400 uppercase">Setor</label>
                <select 
                  value={sector} 
                  onChange={(e) => setSector(e.target.value)}
                  className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none"
                >
                  {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>

            <BriefingInput 
              onRefine={handleRefineBriefing}
            />

            <button 
              onClick={() => setStep(2)}
              disabled={!brand || !keywordsText}
              className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white font-black py-4 rounded-xl shadow-lg shadow-violet-200 transition-all transform active:scale-95"
            >
              PRÓXIMO: DEFINIR HIPÓTESE
            </button>
          </div>
        ) : (
          <div className="p-8 space-y-6 animate-in fade-in slide-in-from-bottom-4">
            <div className="bg-amber-50 border border-amber-100 p-5 rounded-2xl mb-6">
              <p className="text-xs font-bold text-amber-700 leading-relaxed">
                🚀 <span className="uppercase">O motor IA detectou um "Fato Estranho":</span> Com base no seu cenário de {scenario}, formulamos a seguinte hipótese de trabalho. Você pode editá-la agora para treinar a IA sobre o que você quer observar.
              </p>
            </div>

            <div className="space-y-4">
              <p className="text-md text-gray-800 leading-loose italic bg-gray-50 p-6 rounded-2xl border-l-4 border-violet-500 font-medium">
                "O fenômeno <input className="bg-transparent border-b-2 border-violet-200 focus:border-violet-500 outline-none px-2 font-black text-violet-700 w-auto" value={activeHypothesis.x} onChange={e => setActiveHypothesis({...activeHypothesis, x: e.target.value})} /> observado no grupo <input className="bg-transparent border-b-2 border-violet-200 focus:border-violet-500 outline-none px-2 font-black text-violet-700" value={activeHypothesis.y} onChange={e => setActiveHypothesis({...activeHypothesis, y: e.target.value})} /> não é apenas uma excentricidade, mas uma resposta à tensão <input className="bg-transparent border-b-2 border-violet-200 focus:border-violet-500 outline-none px-2 font-black text-violet-700" value={activeHypothesis.z} onChange={e => setActiveHypothesis({...activeHypothesis, z: e.target.value})} />, e tende a se expandir conforme <input className="bg-transparent border-b-2 border-violet-200 focus:border-violet-500 outline-none px-2 font-black text-violet-700" value={activeHypothesis.condition} onChange={e => setActiveHypothesis({...activeHypothesis, condition: e.target.value})} />."
              </p>
            </div>

            <div className="flex gap-4 pt-4">
              <button 
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold py-4 rounded-xl transition-all"
              >
                VOLTAR
              </button>
              <button 
                onClick={handleStart}
                className="flex-[2] bg-emerald-600 hover:bg-emerald-700 text-white font-black py-4 rounded-xl shadow-lg shadow-emerald-200 transition-all"
              >
                VALIDAR & INICIAR DASHBOARD
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-violet-950 via-violet-900 to-amber-900 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      </div>
    }>
      <OnboardingContent />
    </Suspense>
  );
}
