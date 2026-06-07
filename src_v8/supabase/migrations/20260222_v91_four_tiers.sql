-- ============================================================
-- Migration V9.1 — 4 Tiers + Constraint Diaria + RLS Temporal
-- Culture Pulse — 2026-02-22
-- ============================================================
-- Executar no Supabase SQL Editor (Dashboard > SQL Editor)
-- PRE-REQUISITO: tabela cultural_signals ja deve existir
-- ============================================================

-- ============================================================
-- PARTE A: Criar tabela profiles (caso nao exista)
-- ============================================================

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
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- RLS para profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Usuario ve so o proprio perfil" ON public.profiles;
CREATE POLICY "Usuario ve so o proprio perfil"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Usuario atualiza so o proprio perfil" ON public.profiles;
CREATE POLICY "Usuario atualiza so o proprio perfil"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Trigger: cria perfil automaticamente ao registrar usuario
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

-- Trigger: propaga plano para user_metadata ao atualizar
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

-- Index de performance em profiles
CREATE INDEX IF NOT EXISTS idx_profiles_plan ON public.profiles (plan);

-- ============================================================
-- PARTE B: Constraint diaria em cultural_signals
-- ============================================================

-- Remover constraint por timestamp exato (criada anteriormente, se existir)
ALTER TABLE public.cultural_signals
  DROP CONSTRAINT IF EXISTS cultural_signals_termo_plat_ts_unique;

-- Remover constraint diaria antiga (se existir)
ALTER TABLE public.cultural_signals
  DROP CONSTRAINT IF EXISTS cultural_signals_unique_day;

-- Dropar index funcional antigo (se existir)
DROP INDEX IF EXISTS cultural_signals_unique_day;

-- B.1: Limpar duplicados no mesmo dia ANTES de criar o unique index
-- Mantem o registro com menor id (mais antigo) para cada (termo, plataforma, dia)
DELETE FROM public.cultural_signals a
USING public.cultural_signals b
WHERE a.id > b.id
  AND a.termo = b.termo
  AND a.plataforma = b.plataforma
  AND (a.ts AT TIME ZONE 'UTC')::date = (b.ts AT TIME ZONE 'UTC')::date;

-- B.2: Funcao IMMUTABLE para extrair date de timestamptz (exigida para UNIQUE INDEX)
CREATE OR REPLACE FUNCTION public.ts_to_date(t TIMESTAMPTZ)
RETURNS DATE LANGUAGE SQL IMMUTABLE AS $$
  SELECT (t AT TIME ZONE 'UTC')::date;
$$;

-- B.3: Criar UNIQUE INDEX funcional em (termo, plataforma, date(ts))
CREATE UNIQUE INDEX IF NOT EXISTS cultural_signals_unique_day
  ON public.cultural_signals (termo, plataforma, public.ts_to_date(ts));

-- ============================================================
-- PARTE C: RLS em cultural_signals — retencao temporal por plano
-- ============================================================

-- Garantir que RLS esta ativo
ALTER TABLE public.cultural_signals ENABLE ROW LEVEL SECURITY;

-- Remover policies antigas (quaisquer)
DROP POLICY IF EXISTS "Acesso a sinais por plano" ON public.cultural_signals;
DROP POLICY IF EXISTS "service_role full access" ON public.cultural_signals;

-- Service role: acesso total (necessario para o backend escrever via service_role key)
CREATE POLICY "service_role full access"
  ON public.cultural_signals FOR ALL
  USING (current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role');

-- Usuarios autenticados: retencao diferenciada por plano
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
      ELSE
        user_id IS NULL
        AND ts > NOW() - INTERVAL '7 days'
    END
  );

-- ============================================================
-- PARTE D: Views por plano (colunas diferenciadas)
-- ============================================================

-- View FREE: campos basicos, ultimas 24h, limit 100
CREATE OR REPLACE VIEW public.signals_public
WITH (security_invoker = true) AS
  SELECT tipo, circulo, termo, score, regiao, ts
  FROM public.cultural_signals
  WHERE ts > NOW() - INTERVAL '24 hours'
  ORDER BY ts DESC
  LIMIT 100;

COMMENT ON VIEW public.signals_public IS
  'Free tier: sinais das ultimas 24h, campos basicos, sem raw_data (max 100)';

-- View PRO: + regiao, plataforma (sem raw_data), 90 dias
CREATE OR REPLACE VIEW public.signals_pro
WITH (security_invoker = true) AS
  SELECT id, tipo, circulo, termo, score, regiao, plataforma, ts
  FROM public.cultural_signals
  WHERE ts > NOW() - INTERVAL '90 days'
  ORDER BY ts DESC;

COMMENT ON VIEW public.signals_pro IS
  'Pro tier: sinais dos ultimos 90 dias, sem raw_data';

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
  'Executive tier: sinais dos ultimos 365 dias, raw_data parcial (sem demographics/tensions)';

ALTER VIEW public.signals_public    SET (security_invoker = true);
ALTER VIEW public.signals_pro       SET (security_invoker = true);
ALTER VIEW public.signals_executive SET (security_invoker = true);

-- Enterprise usa a tabela cultural_signals diretamente (730 dias via RLS)

-- ============================================================
-- PARTE E: Grants para as views
-- ============================================================

GRANT SELECT ON public.signals_public    TO anon, authenticated, service_role;
GRANT SELECT ON public.signals_pro       TO anon, authenticated, service_role;
GRANT SELECT ON public.signals_executive TO anon, authenticated, service_role;

-- ============================================================
-- PARTE F: Index de performance para retencao temporal
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_signals_ts_desc
  ON public.cultural_signals (ts DESC);

-- ============================================================
-- PARTE G: Funcao de reset mensal de cotas de analises
-- ============================================================

CREATE OR REPLACE FUNCTION public.reset_monthly_analyses()
RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE public.profiles
  SET analyses_this_month = 0,
      analyses_reset_at = date_trunc('month', NOW()) + INTERVAL '1 month'
  WHERE analyses_reset_at <= NOW();
END;
$$;

COMMENT ON FUNCTION public.reset_monthly_analyses IS
  'Reseta cotas de analises mensais. Chamar via pg_cron ou Supabase Edge Function.';

-- Recarregar schema cache do PostgREST
NOTIFY pgrst, 'reload schema';
