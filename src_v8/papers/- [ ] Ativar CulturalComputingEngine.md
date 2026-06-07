- [ ] Ativar CulturalComputingEngine
  - [ ] Análise de polaridade cultural/comercial (Fase 3.6)
  - [ ] Adicionar campo `cultural_polarity` ao `WeakSignal`
  - [ ] Regional embeddings para difusão geográfica
  - [ ] Adicionar campo `regional_context` ao `WeakSignal`
  - [ ] Dashboard: Mapa de calor regional

- [ ] Filtro de Qualidade
  - [ ] Configuração: `MIN_AUTHENTICITY_SCORE = 0.6`
  - [ ] Apenas alertar sinais "VIRAL" se authenticity > 0.6
  - [ ] Separar seção "Movimentos Culturais" vs "Campanhas Comerciais"

- [ ] Treinamento e Validação
- [ ] Ativar `AuthenticityAnalyzer` para análise de autenticidade
- [ ] Treinar modelo XGBoost com dados históricos
- [ ] Implementar clustering HDBSCAN para padrões


- [ ] Testes de Validação
  - [ ] Teste Nike x Maduro (deve detectar baixa autenticidade)
  - [ ] Teste Copa 2026 (deve detectar alta autenticidade)
  - [ ] Teste Açaí em SP (deve detectar difusão Norte→Sudeste)
