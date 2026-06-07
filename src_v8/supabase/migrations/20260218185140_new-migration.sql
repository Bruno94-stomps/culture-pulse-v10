-- Migração new-migration (S1.1 + S1.2)
-- Cria tabelas cultural_signals e signal_embeddings alinhadas ao schema compartilhado.

-- Habilita a extensão vector caso ainda não exista (necessária para pgvector).
CREATE EXTENSION IF NOT EXISTS vector;

-- ===============================
-- Tabela cultural_signals
-- ===============================
CREATE TABLE IF NOT EXISTS public.cultural_signals (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID,  -- FK para profiles omitida intencionalmente (tabela pode não existir no projeto)
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

-- Política básica (service_role vê tudo, usuários autenticados veem seus próprios sinais)
CREATE POLICY IF NOT EXISTS "Acesso a sinais por plano"
  ON public.cultural_signals FOR SELECT
  USING (
    auth.uid() = user_id OR user_id IS NULL
  );

CREATE INDEX IF NOT EXISTS idx_signals_user_ts   ON public.cultural_signals (user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_project_id ON public.cultural_signals (project_id);
CREATE INDEX IF NOT EXISTS idx_signals_circulo   ON public.cultural_signals (circulo);
CREATE INDEX IF NOT EXISTS idx_signals_score     ON public.cultural_signals (score DESC);
ALTER TABLE public.cultural_signals
  ADD CONSTRAINT IF NOT EXISTS cultural_signals_unique_day
  UNIQUE (termo, plataforma, (ts::date));

CREATE OR REPLACE VIEW public.signals_public AS
  SELECT tipo, circulo, termo, score, regiao, ts
  FROM public.cultural_signals
  WHERE ts > NOW() - INTERVAL '24 hours'
  ORDER BY ts DESC
  LIMIT 100;

COMMENT ON VIEW public.signals_public IS
  'Sinais culturais das últimas 24h sem dados de usuário — free tier';

-- ===============================
-- Tabela signal_embeddings (pgvector cache)
-- ===============================
CREATE TABLE IF NOT EXISTS public.signal_embeddings (
  id          BIGSERIAL PRIMARY KEY,
  text_key    TEXT NOT NULL UNIQUE,
  embedding   vector(768),
  model_name  TEXT DEFAULT 'neuralmind/bert-base-portuguese-cased',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  hit_count   INT DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_signal_embeddings_ann
  ON public.signal_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_signal_embeddings_text_key
  ON public.signal_embeddings (text_key);

ALTER TABLE public.signal_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Embeddings — leitura pública de sistema"
  ON public.signal_embeddings FOR SELECT USING (true);

CREATE POLICY IF NOT EXISTS "Embeddings — escrita via service role"
  ON public.signal_embeddings FOR INSERT WITH CHECK (true);

-- ===============================
-- GRANTs para PostgREST / REST API
-- ===============================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

GRANT ALL    ON public.cultural_signals   TO service_role;
GRANT SELECT ON public.cultural_signals   TO anon, authenticated;

GRANT ALL    ON public.signal_embeddings  TO service_role;
GRANT SELECT ON public.signal_embeddings  TO anon, authenticated;

GRANT SELECT ON public.signals_public     TO anon, authenticated, service_role;

GRANT USAGE, SELECT ON SEQUENCE public.cultural_signals_id_seq  TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.signal_embeddings_id_seq TO service_role;

-- Notifica PostgREST para recarregar o schema cache
NOTIFY pgrst, 'reload schema';