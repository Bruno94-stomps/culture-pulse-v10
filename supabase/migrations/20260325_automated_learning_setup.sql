-- 🎓 Migration Script: Automated Learning Engine V9.7
-- Purpose: Setup tables for online learning metrics, learned weights, and discovered patterns.

-- 1. Table: collected_data
-- Stores raw historical snapshots for trend prediction without requiring local DBs.
CREATE TABLE IF NOT EXISTS public.collected_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    brand TEXT NOT NULL,
    industry TEXT NOT NULL,
    territory TEXT DEFAULT 'BR',
    source TEXT NOT NULL, -- youtube, reddit, google_trends, etc.
    metric_type TEXT NOT NULL, -- engagement, volume, sentiment, etc.
    metric_value FLOAT DEFAULT 0.0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing for fast historical lookup during online learning cycles
CREATE INDEX IF NOT EXISTS idx_collected_data_brand_industry ON public.collected_data(brand, industry);
CREATE INDEX IF NOT EXISTS idx_collected_data_timestamp ON public.collected_data(timestamp DESC);

-- 2. Table: learned_weights
-- Stores the dynamically adjusted weights learned via SGDRegressor for each context.
CREATE TABLE IF NOT EXISTS public.learned_weights (
    id BIGSERIAL PRIMARY KEY,
    context TEXT NOT NULL, -- e.g., "Nike_fashion"
    industry TEXT NOT NULL,
    metric_name TEXT NOT NULL DEFAULT 'momentum',
    weight_velocity FLOAT NOT NULL DEFAULT 0.25,
    weight_acceleration FLOAT NOT NULL DEFAULT 0.15,
    weight_cii FLOAT NOT NULL DEFAULT 0.30, -- Cross-Circle Isolation
    weight_geo_spread FLOAT NOT NULL DEFAULT 0.15,
    weight_resonance FLOAT NOT NULL DEFAULT 0.15,
    n_samples INTEGER DEFAULT 0,
    performance_score FLOAT DEFAULT 0.0, -- Proxy for accuracy of these weights
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing for quick retrieval of the latest learned state
CREATE INDEX IF NOT EXISTS idx_learned_weights_industry ON public.learned_weights(industry);
CREATE INDEX IF NOT EXISTS idx_learned_weights_context ON public.learned_weights(context);

-- 3. Table: discovered_patterns
-- Stores output from MiniBatchKMeans for recurring behavioral cohorts.
CREATE TABLE IF NOT EXISTS public.discovered_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type TEXT NOT NULL, -- behavior, group_shift, niche_emergence
    cluster_id INTEGER,
    characteristics JSONB DEFAULT '{}'::jsonb,
    frequency INTEGER DEFAULT 1,
    territories JSONB DEFAULT '[]'::jsonb,
    discovered_at TIMESTAMPTZ DEFAULT NOW()
);

-- 🚀 Enable Row Level Security (RLS) - Recommended for Supabase
ALTER TABLE public.collected_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learned_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.discovered_patterns ENABLE ROW LEVEL SECURITY;

-- Default Policies (adjust based on your auth requirements)
-- Example: Allow service_role to do everything
CREATE POLICY "Allow all to service_role" ON public.collected_data FOR ALL TO service_role USING (true);
CREATE POLICY "Allow all to service_role" ON public.learned_weights FOR ALL TO service_role USING (true);
CREATE POLICY "Allow all to service_role" ON public.discovered_patterns FOR ALL TO service_role USING (true);

-- Usage Comment
COMMENT ON TABLE public.collected_data IS 'Base de dados biográfica para o Automated Learning Engine.';
COMMENT ON TABLE public.learned_weights IS 'Pesos adaptativos aprendidos pela IA para cada território cultural.';
