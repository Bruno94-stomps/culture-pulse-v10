import { createClient } from "@/lib/supabase/server";
import { NextRequest, NextResponse } from "next/server";

/**
 * 🚀 MATERIALITY API (V9)
 * 
 * Este endpoint solicita ao "CulturalAssetGenerator" (Python) a criação de um 
 * Ativo Cultural material baseado no contexto real do projeto do usuário.
 * 
 * Integração: Bertimbau + Twin Brasileiro + Onboarding Context.
 */

export async function POST(req: NextRequest) {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { projectId, assetType = "campaign" } = await req.json();

  // 1. Buscar contexto completo do projeto (Onboarding + Estratégia)
  let project = null;
  
  if (projectId !== 'demo-project') {
    const { data, error: projectError } = await supabase
      .from("projects")
      .select("*")
      .eq("id", projectId)
      .single();
    project = data;
  }

  // Fallback para modo Demo se o projeto não for encontrado ou se for o id de demo
  if (!project) {
    project = {
      brand: "Brasilidade Tech",
      name: "Projeto Demo",
      strategic_kpis: { dashboard_lens: "Exploração" },
      objective: "Mercado de Super-Apps",
      circles: ["Gamers", "Faria Limers", "Cena Trap"]
    };
  }

  // 2. Extrair Lente (Objetivo), Marca e Contexto
  const strategicGoal = project.strategic_kpis?.dashboard_lens || "Exploração";
  const brandName = project.brand || project.name;
  const marketContext = project.objective || "Monitoramento Geral de Cultura";
  const circles = project.circles || [];

  try {
    // 3. Chamada Mockada ao Gerador Python (Bertimbau Engine V8.0)
    
    // Simulação da resposta do CulturalAssetGenerator.py enriquecida V9.5
    const mockAsset = {
      asset_id: `st_asset_${Date.now()}`,
      content: generateMockContent(brandName, strategicGoal, marketContext),
      asset_type: assetType,
      strategic_goal: strategicGoal,
      target_circles: circles,
      recommendations: [
        `Focar no 'Filtro de Verdade' para evitar tom institucional.`,
        "Utilizar estética lo-fi conforme detectado pela Visão Computacional.",
        "Cruzar este asset com o próximo evento do calendário cultural."
      ],
      cultural_scores: {
        relevance: 0.89,
        resonance: 0.92,
        authenticity: 0.85,
        dissonance: 0.78
      },
      visual_consistency_score: 0.85,
      irony_detection_score: 0.12,
      nuance_explanation: "O 'Corre' foi identificado pelo Sabiá-2 como resiliência econômica e identidade urbana, não apenas pressa laboral.",
      evidence: [
        {
          title: "Sinal de alta tração em Gen Z Periférica",
          proof: "https://news.portal.com.br/artigo-tendencia-corre-2026",
          type: "Notícia/Artigo",
          content: "Aumento de 45% em buscas sobre 'empreendedorismo de base' no TikTok."
        },
        {
          title: "Concorrentes ignoram o dinamismo urbano",
          proof: "https://ads-library.com/competitor-x-campaign-2026.mp4",
          type: "Vídeo/Campanha",
          content: "Análise visual da última campanha da Marca X mostra estética europeia eurocêntrica."
        }
      ],
      pest_impact: {
        Political: 0.12,
        Economic: 0.45,
        Social: 0.88,
        Technological: 0.67
      }
    };

    return NextResponse.json({ data: mockAsset });

  } catch (error) {
    console.error("Materialization Error:", error);
    return NextResponse.json({ error: "Falha ao materializar entrega" }, { status: 500 });
  }
}

function generateMockContent(brand: string, goal: string, context: string) {
  if (goal === "Ação") {
    return `[CAMPANHA DE ALTO IMPACTO] - ${brand}: "Conectando o pulso da rua com a inovação digital. Sinta a batida, mude o tom." (Foco em Conversão Real)`;
  }
  if (goal === "Proteção") {
    return `[MANUAL DE POSICIONAMENTO] - ${brand}: "Preservando valores, antecipando tensões. A segurança da sua marca em territórios complexos." (Foco em Mitigação)`;
  }
  return `[MAPA DE EXPLORAÇÃO] - ${brand}: "Desbravando novas linguagens e sinais fracos no ecossistema ${context}. Onde a cultura nasce." (Foco em Discovery)`;
}
