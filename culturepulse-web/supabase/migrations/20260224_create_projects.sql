-- ═══════════════════════════════════════════════════════════════════
-- Culture Pulse — Projects table
-- Entidade central de negócio: cada projeto = 1 briefing de análise
-- ═══════════════════════════════════════════════════════════════════

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

-- Índices
create index if not exists idx_projects_user_id on public.projects(user_id);
create index if not exists idx_projects_status on public.projects(status);

-- RLS: users only see their own projects
alter table public.projects enable row level security;

create policy "Users can view own projects"
  on public.projects for select
  using (auth.uid() = user_id);

create policy "Users can insert own projects"
  on public.projects for insert
  with check (auth.uid() = user_id);

create policy "Users can update own projects"
  on public.projects for update
  using (auth.uid() = user_id);

create policy "Users can delete own projects"
  on public.projects for delete
  using (auth.uid() = user_id);

-- Auto-update updated_at
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists projects_updated_at on public.projects;
create trigger projects_updated_at
  before update on public.projects
  for each row execute function public.handle_updated_at();
