-- Script de verificação para as tabelas e views criadas em new-migration
-- 1) Contagens básicas
SELECT
  'cultural_signals' AS tabela,
  COUNT(*) AS total_registros,
  COUNT(DISTINCT termo) AS termos_distintos
FROM public.cultural_signals;

SELECT
  'signal_embeddings' AS tabela,
  COUNT(*) AS total_registros,
  AVG(hit_count) AS hit_medio
FROM public.signal_embeddings;

-- 2) Inspeção da view pública
SELECT * FROM public.signals_public LIMIT 10;

-- 3) Conferir definição da view
SELECT viewname, definition
FROM pg_catalog.pg_views
WHERE viewname = 'signals_public';
