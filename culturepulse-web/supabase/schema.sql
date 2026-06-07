-- ============================================================
-- Supabase SQL — Culture Pulse V9.1 (4 Tiers)
-- Execute no SQL Editor do painel Supabase
-- Tiers: free / pro / executive / enterprise
-- ============================================================

-- 1. Tabela de perfis (espelha auth.users com dados extras)
CREATE TABLE IF NOT EXISTS public.profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT,
  plan        TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free','pro','executive','enterprise')),
  company     TEXT,
  api_token   TEXT UNIQUE,
  requests_today INT DEFAULT 0,
  last_request   TIMESTAMPTZ,
  analyses_this_month INT DEFAULT 0,
  analyses_reset_at   TIMESTAMPTZ DEFAULT date_trunc('month', NOW()) + INTERVAL '1 month',
  max_users   INT DEFAULT 1,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  -- V9.2: Dados de Onboarding inline para simplificação de query
  onboarding_moment  TEXT DEFAULT 'Geral',
  onboarding_segment TEXT DEFAULT 'Geral',
  onboarding_brand   TEXT DEFAULT 'Geral'
);

-- 2. Row Level Security — cada usuário vê só o próprio perfil
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuário vê só o próprio perfil"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Usuário atualiza só o próprio perfil"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- 3. Trigger: cria perfil automaticamente ao registrar usuário
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, plan)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'plan', 'free')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 4. Trigger: propaga plano para user_metadata ao atualizar
CREATE OR REPLACE FUNCTION public.sync_plan_to_metadata()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE auth.users
  SET raw_user_meta_data = raw_user_meta_data || jsonb_build_object('plan', NEW.plan)
  WHERE id = NEW.id;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_profile_plan_update ON public.profiles;
CREATE TRIGGER on_profile_plan_update
  AFTER UPDATE OF plan ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.sync_plan_to_metadata();

-- 5. Tabela de sinais armazenados (histórico de streaming)
CREATE TABLE IF NOT EXISTS public.cultural_signals (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  project_id  UUID,
  tipo        TEXT,
  circulo     TEXT,
  termo       TEXT,
  score       NUMERIC(4,3),
  regiao      TEXT,
  plataforma  TEXT,
  raw_data    JSONB,
  ts          TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.cultural_signals ENABLE ROW LEVEL SECURITY;

-- Enterprise vê tudo (730d); executive 365d; pro 90d; free 30d
-- Sinais compartilhados (user_id IS NULL) visíveis a todos os planos
-- ATUALIZAÇÃO V9.9: Free Tier em D+1 (Atraso 24h) mas retém 30 dias de histórico
CREATE POLICY "Acesso a sinais por plano"
  ON public.cultural_signals FOR SELECT
  USING (
    CASE (SELECT plan FROM public.profiles WHERE id = auth.uid())
      WHEN 'enterprise' THEN
        ts > NOW() - INTERVAL '730 days'
      WHEN 'executive' THEN
        (user_id IS NULL OR user_id = auth.uid())
        AND ts > NOW() - INTERVAL '365 days'
      WHEN 'pro' THEN
        (user_id IS NULL OR user_id = auth.uid())
        AND ts > NOW() - INTERVAL '90 days'
      WHEN 'free' THEN
        (user_id IS NULL OR user_id = auth.uid())
        AND ts > NOW() - INTERVAL '30 days'
        AND ts < NOW() - INTERVAL '24 hours' -- ENFORCEMENT D+1 (Atraso de 24h)
      ELSE
        user_id IS NULL AND ts > NOW() - INTERVAL '7 days'
    END
  );

-- 6. Índices de performance
CREATE INDEX IF NOT EXISTS idx_signals_user_ts   ON public.cultural_signals (user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_project_id ON public.cultural_signals (project_id);
CREATE INDEX IF NOT EXISTS idx_signals_circulo   ON public.cultural_signals (circulo);
CREATE INDEX IF NOT EXISTS idx_signals_score     ON public.cultural_signals (score DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_plan     ON public.profiles (plan);

-- S1.1 / V9.1: UNIQUE INDEX funcional para upsert diário por (termo, plataforma, dia)
-- Evita duplicatas quando o backend faz upsert após cada ciclo de coleta.
-- Usa CREATE UNIQUE INDEX (não ADD CONSTRAINT) para suportar expressão ts::date.
CREATE UNIQUE INDEX IF NOT EXISTS cultural_signals_unique_day
  ON public.cultural_signals (termo, plataforma, (ts::date));

-- ── S1.2: Cache de embeddings BERTimbau via pgvector ──────────────────────────
-- Requer: CREATE EXTENSION IF NOT EXISTS vector;
-- Roda UMA VEZ no Supabase SQL Editor antes de aplicar este schema:
--   CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.signal_embeddings (
  id          BIGSERIAL PRIMARY KEY,
  text_key    TEXT NOT NULL UNIQUE,          -- hash/texto normalizado (chave de lookup)
  embedding   vector(768),                   -- embedding BERTimbau (768d)
  model_name  TEXT DEFAULT 'neuralmind/bert-base-portuguese-cased',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  hit_count   INT DEFAULT 1                  -- quantas vezes foi reutilizado
);

-- Índice IVFFlat para busca aproximada por vizinhança (ANN)
-- Ajustar lists conforme volume: ~sqrt(n_rows)
CREATE INDEX IF NOT EXISTS idx_signal_embeddings_ann
  ON public.signal_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_signal_embeddings_text_key
  ON public.signal_embeddings (text_key);

-- RLS: embeddings são dados de sistema, sem restrição de user
ALTER TABLE public.signal_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Embeddings — leitura pública de sistema"
  ON public.signal_embeddings FOR SELECT
  USING (true);
CREATE POLICY "Embeddings — escrita via service role"
  ON public.signal_embeddings FOR INSERT
  WITH CHECK (true);

-- FUTURE / MIGRATION NOTES:
-- As tabelas abaixo são referenciadas pelo backend Python de ML e feedback,
-- mas não estão definidas no schema Supabase atual testado.
-- Elas devem ser criadas ou o backend deve ser ajustado para alinhar com o schema:
--   brand_profiles
--   learned_weights
--   model_weights
--   analysis_performance
--   signal_feedback
--   collected_data
--   discovered_patterns
--
-- No estado atual, as fontes validadas de sinais são:
--   cultural_signals, signal_labels, signals_public, signals_pro, signals_executive

-- 7. Views por plano (colunas e retenção diferenciadas)

-- View FREE: campos básicos, últimas 24h, limit 100
CREATE OR REPLACE VIEW public.signals_public
WITH (security_invoker = true) AS
SELECT tipo, circulo, termo, score, regiao, ts
FROM public.cultural_signals
WHERE ts > NOW() - INTERVAL '24 hours'
ORDER BY ts DESC
LIMIT 100;

COMMENT ON VIEW public.signals_public IS
  'Free tier: sinais das últimas 24h, campos básicos, sem raw_data (max 100)';

-- View PRO: + regiao, plataforma (sem raw_data), 90 dias
CREATE OR REPLACE VIEW public.signals_pro
WITH (security_invoker = true) AS
SELECT id, tipo, circulo, termo, score, regiao, plataforma, ts
FROM public.cultural_signals
WHERE ts > NOW() - INTERVAL '90 days'
ORDER BY ts DESC;

COMMENT ON VIEW public.signals_pro IS
  'Pro tier: sinais dos últimos 90 dias, sem raw_data';

-- View EXECUTIVE: + raw_data parcial (sem demographics/tensions), 365 dias
CREATE OR REPLACE VIEW public.signals_executive
WITH (security_invoker = true) AS
SELECT
  id, tipo, circulo, termo, score, regiao, plataforma, ts,
  raw_data - 'demographic_data' - 'tension_indicators' - 'emerging_profile_signals'
    AS raw_data
FROM public.cultural_signals
WHERE ts > NOW() - INTERVAL '365 days'
ORDER BY ts DESC;

COMMENT ON VIEW public.signals_executive IS
  'Executive tier: sinais dos últimos 365 dias, raw_data parcial (sem demographics/tensions)';

-- Enterprise usa tabela cultural_signals diretamente (730 dias via RLS)

GRANT SELECT ON public.signals_public    TO anon, authenticated, service_role;
GRANT SELECT ON public.signals_pro       TO anon, authenticated, service_role;
GRANT SELECT ON public.signals_executive TO anon, authenticated, service_role;
