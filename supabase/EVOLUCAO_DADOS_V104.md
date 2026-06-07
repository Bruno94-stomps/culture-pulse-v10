# 🏛️ Guia de Evolução de Dados (Supabase/V10.4)

Este documento mapeia as alterações necessárias na estrutura do Supabase para suportar os Dashboards Dinâmicos e o cálculo do **Cultural Alpha**.

---

## 1. Tabela `projects` (Extensões)
Para suportar o **Benchmark Dinâmico** e as **Storytelling Lenses**, o objeto `projects` deve conter:

- `segment`: (Text) - O setor principal (ex: "Beleza", "Finanças"). Alimenta o `MarketGapChart`.
- `brand_name`: (Text) - Nome da marca para saudações personalizadas.
- `initial_strategic_lens`: (Text) - A lente escolhida no onboarding (`Ação`, `Exploração`, `Proteção`).
- `strategic_kpis`: (JSONB) - Objeto contendo:
    - `cultural_alpha`: (Float) - Valor calculado pelo BusinessSynthesizer.
    - `momentum_score`: (Float) - Score médio de validação.
    - `market_entropy`: (Float) - Índice de clichês do setor detectados.
- `scenario`: (Text) - Descrição curta do objetivo (ex: "Lançamento de Produto").

## 2. Tabela `cultural_signals` (Inputs de Momentum)
Certifique-se de que os sinais possuem os campos que alimentam o `IntelligenceStatusBar`:

- `score`: (Float) - O score de ressonância/momentum.
- `status`: (Text) - `verified`, `unidentified` (Gaps de Cultura), `obsolete`.
- `metadata`: (JSONB) - Deve conter tags do setor para o cálculo do centroide.

## 3. Lógica de Cálculo do Cultural Alpha (Técnico)
O cálculo é processado no `src_v8/core/intelligence/business_synthesizer.py`:
1.  **Filtro:** `SELECT * FROM cultural_signals WHERE sector = project.segment AND volume > high_threshold`.
2.  **V_Centroid:** Média dos embeddings destes sinais.
3.  **V_Project:** Embedding do briefing do projeto.
4.  **Calculus:** `1 - cosine_similarity(V_Project, V_Centroid)`.

---
*Documento criado para manter a paridade entre o Onboarding e a Visualização.*
