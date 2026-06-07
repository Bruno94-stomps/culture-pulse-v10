# 🗺️ Planejamento Dashboard Next.js V9.7: Acurácia Cultural

Este documento detalha como a nova inteligência do `BusinessSynthesizer` e as refatorações do `DashboardDataBridge` e `EnrichedDataReader` serão traduzidas visualmente no frontend Next.js, substituindo o legado e focando em **fatos biográficos de dados**.

---

## 🎨 1. Componentes de Visualização (Core V9.7)

Estes são os 4 componentes baseados em Redux/API que substituem os gráficos estáticos do Streamlit legado:

### A. `SignalStream.tsx` (O Pulso Real)
- **O que mostra**: Feed de sinais em tempo real vindos diretamente das APIs (YouTube/Reddit/Spotify).
- **Acurácia**: Exibe o **Accuracy Score** biográfico ao lado de cada sinal.
- **Diferencial**: Animação em tempo real e filtros por **Intent** (Research vs. Campaign).

### B. `CirclesSunburst.tsx` (Navegação em Ecossistemas)
- **O que mostra**: A hierarquia dos 16 Círculos Culturais.
- **Acurácia**: Permite o drill-down para ver quais sinais específicos estão puxando um círculo para cima.
- **Diferencial**: Visualização de "Vizinhança Semântica" (onde os círculos se tocam).

### C. `CulturalRadar.tsx` (O DNA do Sinal)
- **O que mostra**: Autenticidade, Velocidade, Sentimento e Tensão.
- **Acurácia**: Não usa médias genéricas, mas sim os dados brutos validados pelo detector de improbabilidade.
- **Diferencial**: Overlay de "Oportunidade Estratégica" para marcas.

### D. `RegionalHeatmap.tsx` (GPS Cultural)
- **O que mostra**: Onde o sinal está "quente" geograficamente (Foco Brasil).
- **Acurácia**: Baseado em metadados de localização reais extraídos dos vídeos e threads.

### E. `BrazilianTwinSimulation.tsx` (Gêmeo Digital Cultural) 🧬
- **O que mostra**: Simulação de reações de personas sintéticas brasileiras a um conteúdo/tema. Por meio de cards das personas sintéticas e suas reações específicas ao tema analisado.
- **O que é**: componente de simulação que mostra o Cultural Fit Score por estado/região com a pergunta estratégica "Como o Brasil reage?" à tabela de componentes de profundidade.`BrazilianCulturalTwinV9`, que utiliza distribuição demográfica do IBGE e círculos culturais regionais.
- **Diferencial**: Exibe o "Cultural Fit Score" por estado/região e as principais "Trave Culturais" (pontos de rejeição).

---

## 🔍 2. Novas Camadas de Inteligência (Trends & Profiles)

Reflexo direto da refatoração biográfica do `DashboardDataBridge`:

### Trends (Tendências com Causa)
- **Novidade**: O gráfico de barras de momentum agora inclui um **"Verification Badge"** (para sinais `is_verified`).
- **Acurácia**: O ranking reflete a densidade de múltiplas plataformas (Confirmação Cross-Platform).
- **O "Porquê"**: Cada trend traz uma descrição sintetizada pelo `BusinessSynthesizer` explicando a causa raiz do movimento.

### Profiles (Personas Reais)
- **Novidade**: Substituição de nomes genéricos por **Identidades Comportamentais**.
- **Acurácia**: O dashboard exibirá se o perfil é **"Omnichannel"** (detectado em >1 plataforma).
- **Fidelidade**: Os atributos (Behaviors) são extraídos de metadados reais de engajamento.

---

## ⚡ 3. Gráficos de Profundidade (Novas Perguntas)

Implementação dos novos prismas de análise baseados na nossa última discussão:

| Pergunta no Dashboard | Componente Visual Sugerido | Dados Base (Propriedades do Objeto) |
| :--- | :--- | :--- |
| **Com quem ele anda?** | `SemanticGraph.tsx` (Network Graph) | `graph_analysis.neighbors` + `connected_circles` |
| **Quão rápido ele corre?** | `VelocityGauge.tsx` (Velocímetro) | `velocity_analysis.velocity` + `momentum` |
| **Quem o carrega?** | `AudienceDemographics.tsx` (Bar/Pie) | `audience_label` + `plataforma_context` |
| **Qual a briga?** | `TensionMatrix.tsx` (Heatmap 2D) | `tension_analysis.tension_score` + `sentiment` |
| **Como o Brasil reage?** | `BrazilianTwinGrid.tsx` (Cards Personas) | `twin_sim.reactions` + `persona_id` |

---

## � 4. Políticas de Planos & Transparência (V9.9)

Atualização das labels de features para refletir as janelas temporais por Tier (SaaS-Aware):

- **Plano FREE**:
    - Label: `Histórico D+1` (Atraso de 24h obrigatório).
    - Janela: Máximo 30 dias de histórico.
    - Limite: 10 sinais por termo.
- **Plano PRO**:
    - Label: `Histórico 7 Dias` (D+1 removido).
    - Janela: 7 dias de retenção.
- **Plano EXECUTIVE**:
    - Label: `Histórico 30 Dias`.
    - Janela: 30 dias de retenção.
- **Plano ENTERPRISE**:
    - Label: `Real-time & Full History`.
    - Janela: Retenção customizada (90+ dias).

---

## �🛠️ Próximos Passos Técnicos

1. **API Integration**: O `EnrichedDataReader` já serve esse `user_id` e `intent` personalizados via FastAPI.
2. **Frontend Mapping**: Mapear os campos `is_verified`, `quality_score` e `insight_summary` no JSON do Next.js.
3. **Shadow Update**: Substituir os componentes de "Placeholders/Mock" do Next.js pelos arquivos reais da pasta `culturepulse-web/components/charts/`.

---

Ativação do Scheduler: Ligar o motor que coleta dados 24h por dia para construir o histórico estratégico das marcas (cold start).
Integração de UI Conversacional: Criar o componente no Next.js que "escuta" as dúvidas do backend e pergunta ao analista.
Loop de Malha Fechada: Validar que, quando você responde no Chat, o sistema realmente ajusta os pesos no Supabase imediatamente.

## 🧠 Intelligent Feedback & Learning System
Este módulo é o coração do aprendizado H.I.T.L. (Human-in-the-Loop) do Pulse. Ele conecta os motores de aprendizado do backend com a interface do usuário.

- `ConversationalPrompt.tsx`: Componente que exibe perguntas geradas pelo `ActiveLearning` (ex: "Notei o termo X emergindo, ele faz sentido?").
- `LearningBadge.tsx`: Exibe o progresso do aprendizado (`FeedbackEngine` stats) nas telas de sinais.
- `IndustryWeightsForm.tsx`: Permite que o usuário visualize e ajuste os pesos aprendidos pelo `AutomatedLearningEngine`.

#### API endpoints necessários (V8/V9 logic):
- `GET /api/v8/active-learning/uncertain`: Busca termos com alta incerteza para o Chat.
- `POST /api/v8/active-learning/feedback`: Envia a resposta do usuário (Relevante/Irrelevante).
- `GET /api/v8/automated-learning/weights`: Retorna os pesos aprendidos no Supabase.

---

## 🕐 Active Scheduler Deployment
- [ ] Configurar Worker de Coleta 24/7.
- [ ] Integrar `AutomatedLearningEngine.start_scheduler()` no script de inicialização do backend.

---
*Documento gerado para a V9.7 em 24/03/2026*

# Atualizações do Planejamento V9.7

- [x] UI: Dashboard Lineage & Veracity (V9.9)
    - Criar o componente VeracityLineage no Next.js para mostrar o lineage do sinal e a prova real (thumbnail + badges).
- [ ] Refactor API Endpoints (V9.9)
  - Migrar chamadas de `/api/v8/` para `/api/v1/` no Frontend conforme padrão modular.
- [ ] UI: Reliability Visual Feedback (V9.9)
  - Adicionar feedback visual (cores/bordas) para clusters ou sinais marcados como `[EXPERIMENTAL]` ou `BAIXA` confiabilidade.
- [ ] UI: Emerging Profiles Scatter Plot (V9.9)
  - Implementar gráfico de dispersão (Scatter Plot) na página de perfis-emergentes (X: Tamanho do Cluster, Y: Score de Emergência, Cor: Veracidade).
