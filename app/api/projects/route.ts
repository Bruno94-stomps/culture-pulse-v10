import { createClient, createServiceClient, getAuthenticatedUser, getBearerToken } from "@/lib/supabase/server";
import { getCurrentPlan } from "@/lib/plan";
import { NextRequest, NextResponse } from "next/server";

/**
 * API Routes for Projects CRUD.
 *
 * GET  /api/projects         — list user's projects
 * POST /api/projects         — create new project
 */

export async function GET() {
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("projects")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) {
    // Table might not exist yet
    if (error.message.includes("Could not find")) {
      return NextResponse.json({ data: [], _migration_needed: true });
    }
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ data });
}

export async function POST(req: NextRequest) {
  const accessToken = getBearerToken();
  const supabase = accessToken ? createServiceClient() : createClient();
  const user = await getAuthenticatedUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await req.json();

  // Validate required fields
  const { name, brand, keywords, segment, objective, regions, audiences, circles, period_days } = body;
  if (!name || !brand || !keywords?.length) {
    return NextResponse.json(
      { error: "name, brand e keywords são obrigatórios" },
      { status: 400 }
    );
  }

  // Check project limits by backend-resolved plan
  const plan = await getCurrentPlan();
  const limits: Record<string, number> = { free: 1, pro: 5, executive: 20, enterprise: 999 };
  const maxProjects = limits[plan] ?? 1;

  const { count } = await supabase
    .from("projects")
    .select("id", { count: "exact", head: true })
    .eq("user_id", user.id);

  if ((count ?? 0) >= maxProjects) {
    return NextResponse.json(
      { error: `Limite de ${maxProjects} projetos atingido para o plano ${plan}. Faça upgrade.` },
      { status: 403 }
    );
  }

  const { data, error } = await supabase
    .from("projects")
    .insert({
      user_id: user.id,
      name,
      brand,
      keywords: keywords ?? [],
      segment: segment ?? "geral",
      objective: objective ?? "",
      regions: regions ?? ["Brasil (Geral)"],
      audiences: audiences ?? ["Todos"],
      circles: circles ?? [],
      period_days: period_days ?? 30,
      status: "draft",
    })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ data }, { status: 201 });
}
