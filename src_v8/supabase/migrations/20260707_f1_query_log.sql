-- ============================================================
-- Migration F-1 — Query Log (FASE 1: Fundação)
-- Culture Pulse V9.1 — 2026-07-07
-- ============================================================
-- Tracks every analysis/query for history, learning, and auditing.
-- PRE-REQUISITO: supabase-py + tables from prior migrations.
-- ============================================================

-- ============================================================
-- TABELA: query_log
-- ============================================================
CREATE TABLE IF NOT EXISTS public.query_log (
  id           BIGSERIAL PRIMARY KEY,
  user_id      UUID,                         -- FK auth.users (NULL for service)
  plan         TEXT DEFAULT 'free',           -- free/pro/executive/enterprise
  query_type   TEXT NOT NULL,                 -- 'brand_analysis', 'circle_analysis',
                                             -- 'tfidf_search', 'trend_query',
                                             -- 'dashboard_collect', 'api_endpoint'
  query_input  JSONB NOT NULL DEFAULT '{}',  -- {keywords, brand_name, filters...}
  result_summary JSONB DEFAULT '{}',         -- {signals_count, top_circle, score...}
  source       TEXT DEFAULT 'dashboard',     -- 'dashboard', 'api', 'batch', 'worker'
  enriched     BOOLEAN DEFAULT FALSE,        -- whether enriched pipeline was used
  duration_ms  INT,                          -- query execution time in ms
  status       TEXT DEFAULT 'success',       -- 'success', 'error', 'timeout', 'partial'
  error_detail TEXT,                         -- error message if status != 'success'
  ts           TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_query_log_user_ts
  ON public.query_log (user_id, ts DESC);

CREATE INDEX IF NOT EXISTS idx_query_log_type
  ON public.query_log (query_type);

CREATE INDEX IF NOT EXISTS idx_query_log_plan
  ON public.query_log (plan);

CREATE INDEX IF NOT EXISTS idx_query_log_ts
  ON public.query_log (ts DESC);

-- GIN index for JSONB search on query_input
CREATE INDEX IF NOT EXISTS idx_query_log_input_gin
  ON public.query_log USING gin (query_input);

-- ============================================================
-- RLS
-- ============================================================
ALTER TABLE public.query_log ENABLE ROW LEVEL SECURITY;

-- Service role (used by backend) sees everything
-- Users can only see their own queries
CREATE POLICY "Usuario ve so suas queries"
  ON public.query_log FOR SELECT
  USING (auth.uid() = user_id OR user_id IS NULL);

-- Only service role can INSERT (backend writes)
CREATE POLICY "Service insere queries"
  ON public.query_log FOR INSERT
  WITH CHECK (TRUE);

-- ============================================================
-- VIEW: recent queries (last 24h, aggregated)
-- ============================================================
CREATE OR REPLACE VIEW public.query_stats_24h AS
  SELECT
    query_type,
    plan,
    COUNT(*) AS total_queries,
    AVG(duration_ms)::INT AS avg_duration_ms,
    COUNT(*) FILTER (WHERE status = 'success') AS success_count,
    COUNT(*) FILTER (WHERE status != 'success') AS error_count,
    MAX(ts) AS last_query
  FROM public.query_log
  WHERE ts > NOW() - INTERVAL '24 hours'
  GROUP BY query_type, plan
  ORDER BY total_queries DESC;

COMMENT ON TABLE public.query_log IS
  'F-1: Tracks all queries/analyses for history, learning, and auditing. FASE 1 Fundação.';

COMMENT ON VIEW public.query_stats_24h IS
  'Aggregated query statistics for the last 24 hours.';
