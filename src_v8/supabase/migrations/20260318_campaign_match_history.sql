-- Migration V91_MATCH_PERSISTENCE (20260318)
-- Objetivo: Criar tabela para histórico de Match de Campanhas

CREATE TABLE IF NOT EXISTS public.campaign_match_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    segment TEXT NOT NULL,
    campaign_text TEXT NOT NULL,
    match_score NUMERIC(5,4) NOT NULL,
    authenticity_score NUMERIC(5,4) NOT NULL,
    sentiment_alignment NUMERIC(5,4) NOT NULL,
    risks JSONB DEFAULT '[]'::jsonb,
    strengths JSONB DEFAULT '[]'::jsonb,
    suggestions JSONB DEFAULT '[]'::jsonb,
    detected_circles JSONB DEFAULT '[]'::jsonb,
    geographic_spread JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexação para busca rápida por cliente/marca
CREATE INDEX IF NOT EXISTS idx_campaign_match_client ON public.campaign_match_history(client_id);
CREATE INDEX IF NOT EXISTS idx_campaign_match_brand ON public.campaign_match_history(brand_name);

-- Comentários da tabela
COMMENT ON TABLE public.campaign_match_history IS 'Histórico de análises de match de campanhas e autenticidade cultural';
