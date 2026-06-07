-- 🎓 Migration Script: Active Learning (Human-in-the-Loop) V9.7
-- Purpose: Setup tables for tracking analyst feedback and hierarchical query rankings.

-- 1. Table: query_feedback
-- Stores individual human or auto-imported feedback points for specific search terms.
CREATE TABLE IF NOT EXISTS public.query_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    relevant BOOLEAN NOT NULL DEFAULT true,
    confidence FLOAT NOT NULL DEFAULT 1.0, -- Confidence score (0-1)
    source TEXT NOT NULL DEFAULT 'analyst', -- analyst, auto, system
    notes TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing for fast retrieval of specific query histories
CREATE INDEX IF NOT EXISTS idx_query_feedback_query ON public.query_feedback(query);
CREATE INDEX IF NOT EXISTS idx_query_feedback_timestamp ON public.query_feedback(timestamp DESC);

-- 2. Table: query_rankings_historical
-- Stores snapshots of computed rankings to monitor how a term's relevance evolves over time.
CREATE TABLE IF NOT EXISTS public.query_rankings_historical (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    relevance_score FLOAT NOT NULL DEFAULT 0.5, -- Wilson Lower Bound
    uncertainty FLOAT NOT NULL DEFAULT 1.0, -- Binary Entropy
    priority FLOAT NOT NULL DEFAULT 0.5, -- Combined metric
    total_feedback INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,
    avg_confidence FLOAT DEFAULT 0.0,
    status TEXT DEFAULT 'needs_review', -- needs_review, validated, rejected, uncertain
    last_feedback_at TIMESTAMPTZ,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexing for fast ranking lookups by status (e.g., query all 'uncertain' terms for the dashboard)
CREATE INDEX IF NOT EXISTS idx_query_rankings_query ON public.query_rankings_historical(query);
CREATE INDEX IF NOT EXISTS idx_query_rankings_status ON public.query_rankings_historical(status);
CREATE INDEX IF NOT EXISTS idx_query_rankings_priority ON public.query_rankings_historical(priority DESC);

-- 🚀 Enable Row Level Security (RLS)
ALTER TABLE public.query_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.query_rankings_historical ENABLE ROW LEVEL SECURITY;

-- Default Policies (adjust based on your auth requirements)
CREATE POLICY "Allow all for service_role" ON public.query_feedback FOR ALL TO service_role USING (true);
CREATE POLICY "Allow all for service_role" ON public.query_rankings_historical FOR ALL TO service_role USING (true);

-- Usage Comment
COMMENT ON TABLE public.query_feedback IS 'Logs de feedbacks humanos e automáticos para refinamento de queries.';
COMMENT ON TABLE public.query_rankings_historical IS 'Snapshot histórico do ranking e relevância de cada termo de busca.';
