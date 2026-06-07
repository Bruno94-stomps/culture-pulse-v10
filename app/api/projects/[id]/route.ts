import { createClient, createServiceClient, getAuthenticatedUser, getBearerToken } from "@/lib/supabase/server";
import { getCurrentPlan } from "@/lib/plan";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";
import { fetchFastApi } from "@/lib/dashboard";
import { NextRequest, NextResponse } from "next/server";

/**
 * API Routes for single Project.
 *
 * GET    /api/projects/[id]  — get project details
 * PATCH  /api/projects/[id]  — update project
 * DELETE /api/projects/[id]  — delete project
 * POST   /api/projects/[id]  — trigger analysis (collect + analyze)
 */

type Ctx = { params: Promise<{ id: string }> };

function normalizeProjectSegment(segment?: string | null): string {
  if (!segment) return "servicos";
  const normalized = segment.toLowerCase();
  if (normalized.includes("aliment") || normalized.includes("bebid")) return "alimentacao";
  if (normalized.includes("moda") || normalized.includes("beleza")) return "moda";
  if (normalized.includes("tecnologia") || normalized.includes("apps")) return "tecnologia";
  if (normalized.includes("entretenimento") || normalized.includes("mídia") || normalized.includes("midia")) return "entretenimento";
  if (normalized.includes("saúde") || normalized.includes("saude") || normalized.includes("bem-estar") || normalized.includes("bem estar")) return "saude";
  if (normalized.includes("educa") || normalized.includes("educação")) return "educacao";
  return "servicos";
}

function normalizeProjectLocation(regions?: string[] | null): string {
  if (!regions?.length) return "São Paulo - Capital";
  const location = regions[0].toLowerCase();
  if (location.includes("são paulo") || location.includes("sp")) return "São Paulo - Capital";
  if (location.includes("rio") || location.includes("rj")) return "Rio de Janeiro - Capital";
  if (location.includes("salvador") || location.includes("ba")) return "Salvador";
  if (location.includes("fortaleza") || location.includes("ce")) return "Fortaleza";
  if (location.includes("recife") || location.includes("pe")) return "Recife";
  if (location.includes("porto alegre") || location.includes("rs")) return "Porto Alegre";
  if (location.includes("curitiba") || location.includes("pr")) return "Curitiba";
  return "São Paulo - Capital";
}

function normalizeStringArray(value?: any): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter(Boolean).map(String);
}

function buildBusinessContextPayload(project: any, user: any) {
  return {
    project_id: project.id,
    user_id: user.id,
    brand: project.brand,
    segment: normalizeProjectSegment(project.segment),
    objective: project.objective,
    keywords: normalizeStringArray(project.keywords),
    regions: normalizeStringArray(project.regions),
    audiences: normalizeStringArray(project.audiences),
    circles: normalizeStringArray(project.circles),
    period_days: project.period_days,
    business_goal: project.objective || `Entendimento cultural para ${project.brand}`,
  };
}

function normalizeBusinessInsightsResponse(insights: any, projectId: string, userId: string, modelName: string) {
  const normalized: any = {
    insights: [],
    summary: {
      total_texts: 0,
      dominant_culture: null,
      avg_confidence: 0,
      average_alignment: 0,
      average_opportunity: 0,
      average_risk: 0,
      ...(insights?.summary ?? {}),
    },
    project_id: projectId,
    user_id: userId,
    model_used: modelName,
    context_source: "business_context",
    ...insights,
  };

  if (Array.isArray(insights?.insights)) {
    normalized.insights = insights.insights;
  }

  if (!normalized.summary.total_texts && Array.isArray(normalized.insights)) {
    normalized.summary.total_texts = normalized.insights.length;
  }

  return normalized;
}

export async function GET(_req: NextRequest, ctx: Ctx) {
  const { id } = await ctx.params;
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  if (error || !data) return NextResponse.json({ error: "Project not found" }, { status: 404 });

  return NextResponse.json({ data });
}

export async function PATCH(req: NextRequest, ctx: Ctx) {
  const { id } = await ctx.params;
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await req.json();
  const allowed = ["name", "brand", "keywords", "segment", "objective", "regions", "audiences", "circles", "period_days", "status", "analysis_data", "signals_count", "last_analysis_at"];
  const updates: Record<string, any> = {};
  for (const key of allowed) {
    if (body[key] !== undefined) updates[key] = body[key];
  }

  const { data, error } = await supabase
    .from("projects")
    .update(updates)
    .eq("id", id)
    .eq("user_id", user.id)
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ data });
}

export async function DELETE(_req: NextRequest, ctx: Ctx) {
  const { id } = await ctx.params;
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { error } = await supabase
    .from("projects")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ status: "deleted" });
}

/**
 * POST /api/projects/[id] — Trigger analysis.
 * Sets status to "collecting", calls FastAPI /analysis/brand,
 * then updates status to "ready" with results.
 */
export async function POST(_req: NextRequest, ctx: Ctx) {
  const { id } = await ctx.params;
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Get project
  const { data: project, error: fetchErr } = await supabase
    .from("projects")
    .select("*")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  if (fetchErr || !project) {
    return NextResponse.json({ error: "Project not found" }, { status: 404 });
  }

  // Set status to collecting
  await supabase
    .from("projects")
    .update({ status: "collecting" })
    .eq("id", id);

  const plan = await getCurrentPlan();
  
  // V9.3 - Configuração de Data Mining por Tier
  // Outlier Mode (Descoberta de Nichos) é um recurso Premium.
  // - Free: Apenas coleta padrão (Mainstream)
  // - Pro/Executive/Enterprise: Acesso à Injeção de Outliers para sinais raros.
  const outlierMode = ["pro", "executive", "enterprise"].includes(plan);
  
  const baseUrl = FASTAPI_BASE_URL;

  const businessContextPayload = buildBusinessContextPayload(project, user);

  try {
    // 1. Trigger brand analysis via FastAPI
    await supabase.from("projects").update({ status: "analyzing" }).eq("id", id);

    const analysisRes = await fetchFastApi(`${baseUrl}/api/v8/analysis/brand`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_id: project.id,
        brand_name: project.brand,
        segment: normalizeProjectSegment(project.segment),
        location: normalizeProjectLocation(project.regions),
        demographics: {
          faixa_etaria: "16-25",
          classe_social: "B",
          genero: "Todos",
          escolaridade: "não especificado",
          renda_familiar: "média",
        },
        keywords: project.keywords ?? [],
        regions: project.regions ?? [],
        audiences: project.audiences ?? [],
        circles: project.circles ?? [],
        period_days: project.period_days,
        business_goal: project.objective || `Entendimento cultural para ${project.brand}`,
        context_text:
          project.keywords && project.keywords.length > 0
            ? project.keywords.join(", ")
            : project.objective || project.brand || "Análise de contexto",
        outlier_mode: outlierMode,
      }),
    });

    let analysisData = null;
    if (analysisRes.ok) {
      analysisData = await analysisRes.json();
    }

    const insightTexts = (project.keywords && project.keywords.length > 0)
      ? project.keywords
      : [project.objective || project.brand || "Análise de contexto"];

    let businessInsights = null;
    if (insightTexts.length > 0) {
      const insightsRes = await fetchFastApi(`${baseUrl}/api/v8/ml/analyze/business-insights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          texts: insightTexts,
          business_context: businessContextPayload,
          model_name: "cultural_demo",
        }),
      });

      if (insightsRes.ok) {
        const rawInsights = await insightsRes.json();
        businessInsights = normalizeBusinessInsightsResponse(rawInsights, project.id, user.id, "cultural_demo");
      } else {
        let insightError = `Business insights request failed with status ${insightsRes.status}`;
        try {
          const bodyText = await insightsRes.text();
          if (bodyText) insightError = bodyText;
        } catch (_) {}
        businessInsights = normalizeBusinessInsightsResponse(
          {
            error: insightError,
            insights: [],
          },
          project.id,
          user.id,
          "cultural_demo"
        );
      }
    }

    // 2. Run intelligence pipeline on project keywords
    const intelligenceResults = [];
    for (const keyword of (project.keywords as string[]).slice(0, 3)) {
      try {
        const intRes = await fetchFastApi(`${baseUrl}/api/v8/intelligence/full`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            termo: keyword,
            momentum: 50,
            sentiment: 0.5,
            volume: 100,
            plataforma: "multi",
          }),
        });
        if (intRes.ok) {
          const data = await intRes.json();
          intelligenceResults.push(data.data);
        }
      } catch { /* skip keyword */ }
    }

    // 3. Count signals matching project keywords in Supabase
    let signalsCount = 0;
    for (const kw of project.keywords as string[]) {
      const { count } = await supabase
        .from("cultural_signals")
        .select("id", { count: "exact", head: true })
        .eq("project_id", project.id)
        .ilike("termo", `%${kw}%`);
      signalsCount += count ?? 0;
    }

    // 4. Update project with results
    await supabase
      .from("projects")
      .update({
        status: "ready",
        signals_count: signalsCount,
        last_analysis_at: new Date().toISOString(),
        analysis_data: {
          brand_analysis: analysisData,
          business_context: businessContextPayload,
          business_insights: businessInsights,
          intelligence: intelligenceResults,
          keywords_analyzed: project.keywords,
          timestamp: new Date().toISOString(),
        },
      })
      .eq("id", id);

    return NextResponse.json({
      status: "success",
      signals_count: signalsCount,
      analysis_available: !!analysisData,
      intelligence_count: intelligenceResults.length,
    });
  } catch (err: any) {
    await supabase
      .from("projects")
      .update({ status: "error" })
      .eq("id", id);

    return NextResponse.json(
      { error: err.message ?? "Analysis failed" },
      { status: 500 }
    );
  }
}
