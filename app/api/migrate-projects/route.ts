import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/**
 * One-time migration: creates the `projects` table.
 * Run via: GET /api/migrate-projects
 * Uses service_role key so it bypasses RLS.
 */
export async function GET() {
  const supabaseAdmin = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { persistSession: false } }
  );

  // Use rpc to execute raw SQL (we create the function first, then call it)
  const createFn = await supabaseAdmin.rpc("exec_raw_sql", {
    sql_text: "SELECT 1",
  });

  // If rpc doesn't exist, fall back to creating table via REST
  // We'll create the table by inserting into it — but first check if it exists
  const { error: checkError } = await supabaseAdmin
    .from("projects")
    .select("id")
    .limit(1);

  if (checkError && checkError.message.includes("Could not find")) {
    // Table doesn't exist — we need to create it via SQL
    // Since we can't run raw SQL via REST, output the SQL for manual execution
    return NextResponse.json({
      status: "migration_needed",
      message: "Table 'projects' does not exist. Please run the following SQL in the Supabase SQL Editor:",
      sql: `
create table if not exists public.projects (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  name          text not null,
  brand         text not null,
  keywords      text[] not null default '{}',
  segment       text not null default 'geral',
  objective     text not null default '',
  regions       text[] not null default '{"Brasil (Geral)"}',
  audiences     text[] not null default '{"Todos"}',
  circles       text[] not null default '{}',
  period_days   int not null default 30,
  status        text not null default 'draft' check (status in ('draft','collecting','analyzing','ready','error')),
  signals_count int not null default 0,
  last_analysis_at timestamptz,
  analysis_data  jsonb,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists idx_projects_user_id on public.projects(user_id);
create index if not exists idx_projects_status on public.projects(status);
alter table public.projects enable row level security;
create policy "Users can view own projects" on public.projects for select using (auth.uid() = user_id);
create policy "Users can insert own projects" on public.projects for insert with check (auth.uid() = user_id);
create policy "Users can update own projects" on public.projects for update using (auth.uid() = user_id);
create policy "Users can delete own projects" on public.projects for delete using (auth.uid() = user_id);
      `.trim(),
    });
  }

  return NextResponse.json({
    status: "ok",
    message: "Table 'projects' already exists.",
  });
}
