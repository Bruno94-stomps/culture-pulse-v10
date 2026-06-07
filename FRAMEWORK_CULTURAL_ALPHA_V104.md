# 🧶 Storytelling Estratégico & Framework Cultural Alpha (V10.4)

Este documento define a camada de tradução entre o **Cérebro (BusinessSynthesizer)** e o **Front-end (Dashboard Next.js)**, utilizando os fundamentos dos papers acadêmicos e a lógica de objetivos do Onboarding.

---

## 🚀 1. O Conceito de Cultural Alpha (ROI Cultural)

O **Cultural Alpha** é a métrica proprietária do PULSO que quantifica a vantagem competitiva obtida através da antecipação de sinais fracos.

> **Formula:** `Cultural Alpha = (Marca no Pulso) - (Média de Mercado)`

### Como calculamos o Benchmark de Mercado?
Para evitar "achismo", o sistema utiliza:
1.  **Dados Históricos de Clichês**: A média de engajamento em termos de alta similaridade (ex: posts sobre Samba/Carnaval) serve como linha de base (Market Average).
2.  **Sinais de Controle**: O sistema monitora 3-5 marcas líderes do segmento que NÃO usam o Pulso e mede a latência delas para adotar uma tendência (ex: "Levam 45 dias para falar de K-pop Periférico").
3.  **Baseline de Sentimento**: Medimos a média de rejeição (tension) de campanhas genéricas no setor.

---

## 🧠 2. Seletor de Dashboard: O Logic Selector de Storytelling

Dependendo do objetivo no Onboarding, o Dashboard redireciona a hierarquia visual:

| Objetivo (Onboarding) | Lente de Storytelling | Gráfico Primário (Hero) | KPI de Sucesso (Paper Ref) |
| :--- | :--- | :--- | :--- |
| **Pesquisa de Mercado** | "Onde estão os Gaps?" | `CirclesSunburst.tsx` | **Foresight Effectiveness** (Yield > 25%) |
| **Lançamento / Campanha** | "Qual sinal acelerar?" | `CulturalRadar.tsx` | **Impact on Momentum** (+12% speed) |
| **Crise de Reputação** | "Qual o tamanho do risco?" | `TensionMatrix.tsx` | **Tension Mitigation** (Delta Tensão) |
| **Tracking de Marca** | "Estamos sendo autênticos?" | `SignalStream.tsx` | **Authenticity Depth** (P75 Gutsche) |

---

## 📊 3. Dicionário de Output: `strategic_kpis`

O `BusinessSynthesizer` passará para o Next.js o seguinte objeto para alimentar os cases:

```json
"strategic_kpis": {
    "primary_metric": "Discovery Yield / Tension Mitigation",
    "target_value": "Score > 0.85 ou Delta < 0.2",
    "business_impact_estimated": "Redução de CAC via orgânico ou Velocidade de Reação",
    "cultural_alpha": "+15% vs Competidor A"
}
```

---

## 🚀 4. Proposta de Evolução V10.4: Storytelling Lenses (UI Dinâmica)

O Dashboard deixa de ser estático para se tornar um **Seletor de Contexto**. O componente `DashboardSelector` (ou similar) interceptará o `scenario_type` do contexto para alternar entre as views:

### ⚡ Lógica de Destaque por Objetivo (Onboarding):
1.  **View de Exploração (Research)**: Foco em **Discovery Yield (Gaps)**.
    *   **Destaque**: Prioriza o pilar de **Clustering & Grafos** e o **Grafo de Conexões Culturais** (Onde a concorrência não está).
2.  **View de Ação (Launch)**: Foco em **Impact on Momentum (Aceleração)**.
    *   **Destaque**: O card de **Sinais & Estabilidade** é promovido a Hero, exibindo o **Velocímetro de Momentum** e mudando a paleta para cores de aceleração (Verde/Amarelo).
3.  **View de Proteção (Crisis)**: Foco em **Tension Mitigation (Proteção)**.
    *   **Destaque**: Prioriza a **Matriz de Tensão** e o Heatmap de risco cultural para mitigação imediata.

### 📊 Resumo de Cultural Alpha
Injeção de um badge de resumo no topo do dashboard:
> "Seu Cultural Alpha atual é de **+15%** em relação à média do setor (Foresight Effectiveness)."

---

## 🎨 5. Guia para Figma MCP (Design System)
// ...existing code...

Para o **Figma Make**, utilizaremos os seguintes prompts de design baseados no Storytelling:

### A. View de Exploração (Pesquisa)
- **Vibe**: Antropológica, tons de azul e roxo profundo.
- **Destaque**: Grafo de conexões (`Com quem ele anda?`).
- **Narrativa**: "Sinais que sua concorrência ainda não ouviu".

### B. View de Ação (Lançamento)
- **Vibe**: Energética, verde "Go" e amarelo de atenção.
- **Destaque**: Velocímetro de Momentum (`Quão rápido ele corre?`).
- **Narrativa**: "A Janela de Oportunidade é AGORA".

### C. View de Proteção (Crise)
- **Vibe**: Alerta, tons de vermelho suave e cinza escuro.
- **Destaque**: Heatmap de Tensão (`Qual a briga?`).
- **Narrativa**: "Ponte Cultural de Reparação Necessária".

---

## 🛠️ Próximos Passos (Ação do Agente)
1.  [x] **Injetar o `strategic_kpis`** no pipeline de saída do `BusinessSynthesizer.py`.
2.  [ ] **Criar a estrutura visual no Figma** via MCP para representar essas 3 lentes.
3.  [ ] **Mapear no Next.js** o seletor de rotas que carrega os componentes baseados na `intent` do `BusinessContext`.
4.  [ ] **UI Dinâmica**: Atualizar o `app/dashboard/page.tsx` para ler o `intent` do usuário e reordenar dinamicamente os pilares de navegação.
5.  [ ] **Badge de Cultural Alpha**: Adicionar o componente visual de Resumo de Performance Cultural (Marca vs. Mercado) no topo do Dashboard.

---
*Assimetria de Informação Cultural: O PULSO vê o futuro 3 meses antes.*
