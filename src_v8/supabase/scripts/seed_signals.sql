-- Script de dados de teste para cultural_signals + signal_embeddings
INSERT INTO public.cultural_signals (user_id, tipo, circulo, termo, score, regiao, plataforma, raw_data, ts)
VALUES
  (NULL, 'Teste API', 'musica_ritmo', 'samba', 0.85, 'Sudeste', 'YouTube', jsonb_build_object('test', TRUE), NOW()),
  (NULL, 'Simulação', 'gastronomia_sabor', 'feijoada', 0.65, 'Nordeste', 'Spotify', jsonb_build_object('batch', 'seed'), NOW());

INSERT INTO public.signal_embeddings (text_key, embedding, model_name)
VALUES
  ('samba-musica', array_fill(0.5, ARRAY[768])::vector, 'neuralmind/bert-base-portuguese-cased'),
  ('feijoada-gastronomia', array_fill(0.2, ARRAY[768])::vector, 'neuralmind/bert-base-portuguese-cased');
