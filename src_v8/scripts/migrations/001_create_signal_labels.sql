-- ============================================================
-- MIGRATION: criar tabela signal_labels
-- Culture Pulse V9 — S2.1 Snorkel Labeling Functions
-- ============================================================
-- COMO USAR:
--   1. Acesse o Supabase Dashboard: https://supabase.com/dashboard
--   2. Selecione o projeto wsizqmnnicpgblopmxyv
--   3. Vá em SQL Editor → New Query
--   4. Cole este arquivo e clique em Run
-- ============================================================

CREATE TABLE IF NOT EXISTS public.signal_labels (
    id           BIGSERIAL PRIMARY KEY,
    signal_id    BIGINT NOT NULL,
    label        TEXT NOT NULL,
    confidence   FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    lf_applied   TEXT[] NOT NULL DEFAULT '{}',
    lf_votes     JSONB NOT NULL DEFAULT '{}',
    abstain_rate FLOAT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para queries frequentes
CREATE INDEX IF NOT EXISTS idx_signal_labels_signal_id  ON public.signal_labels(signal_id);
CREATE INDEX IF NOT EXISTS idx_signal_labels_label      ON public.signal_labels(label);
CREATE INDEX IF NOT EXISTS idx_signal_labels_confidence ON public.signal_labels(confidence DESC);

-- Upsert idempotente por signal_id
CREATE UNIQUE INDEX IF NOT EXISTS uniq_signal_labels_signal_id ON public.signal_labels(signal_id);

-- Comentário de documentação
COMMENT ON TABLE public.signal_labels IS
  'Pseudo-labels gerados por Snorkel LabelModel/MajorityVote — S2.1 Culture Pulse V9';
COMMENT ON COLUMN public.signal_labels.signal_id    IS 'FK para cultural_signals.id';
COMMENT ON COLUMN public.signal_labels.label        IS 'Classe predita (ex: MUSICA, GASTRONOMIA)';
COMMENT ON COLUMN public.signal_labels.confidence   IS 'Confiança do LabelModel [0,1]';
COMMENT ON COLUMN public.signal_labels.lf_applied   IS 'Lista de LFs que votaram (não ABSTAIN)';
COMMENT ON COLUMN public.signal_labels.lf_votes     IS 'Votos individuais de cada LF: {lf_name: label}';
COMMENT ON COLUMN public.signal_labels.abstain_rate IS 'Fração de LFs que abstiveram';

-- Habilitar Row Level Security (recomendado)
ALTER TABLE public.signal_labels ENABLE ROW LEVEL SECURITY;

-- Policy: service role tem acesso total
CREATE POLICY IF NOT EXISTS "service_role_all" ON public.signal_labels
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Policy: acesso público de leitura (opcional — remova se quiser restringir)
CREATE POLICY IF NOT EXISTS "read_public" ON public.signal_labels
    FOR SELECT TO anon, authenticated USING (true);
