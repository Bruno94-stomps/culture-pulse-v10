# 🗺️ Fluxo de Experiência do Usuário (UX Journey V10.4)

Este documento detalha o "Golden Path" do usuário no PULSO, desde o primeiro acesso até a entrega do **Cultural Alpha**, conectando as páginas existentes ao novo cérebro de inteligência.

---

## 🌐 Fase 0: A Estrutura de Portais (Futurumã CC + Next.js Cloudflare Pages/PULSO)

Como você já tem o site institucional na Hostinger, o fluxo será um **Ecossistema de Domínios .cc**:

1.  **Site Institucional (Hostinger)**: `futuruma.cc`
    -   **O que é**: Vitrine estratégica, explicação da metodologia "Alma do Brasileiro".
    -   **CTAs**: Botões "Login" e "Começar Grátis".
2.  **App de Inteligência (Next.js)**: `app.futuruma.cc`
    -   **Fluxo "Começar Grátis"**: Envia o usuário diretamente para o **Onboarding Real** no Plano Free (com limitações de histórico e volume de sinais).
    -   **Fluxo "Login"**: 
        -   Se **Primeiro Acesso (Sem projetos)**: Direciona para o `app.futuruma.cc/onboarding`.
        -   Se **Usuário Ativo (Com projetos)**: Direciona para o `app.futuruma.cc/dashboard` do projeto mais recente.

---

## 🚦 Fase 1: Ativação (O Portal de Entrada `app.futuruma.cc`)

### A. Roteamento Inteligente (Smart Redirect)
O sistema verifica o estado do usuário no Supabase logo após a autenticação:

| Estado do Usuário | Destino Imediato | Lógica de Storytelling |
| :--- | :--- | :--- |
| **Novo / Sem Projetos** | `/onboarding/goal` | "Bem-vindo ao Futurumã. Qual seu primeiro desafio?" |
| **Com Projetos Ativos** | `/dashboard?project_id=last` | "Bom rever você. Aqui está o pulso do seu último projeto." |

---

## 🧠 Fase 2: Onboarding de Contexto (A Coleta do Briefing Real)

O usuário não entra em um dashboard vazio; ele define a sua "Lente" e Briefing em uma única experiência fluida no Next.js.

1.  **Experiência Unificada (`/onboarding`)**:
    -   **O Seletor de Cenário**: Integrado na mesma tela, o usuário escolhe entre *Lançamento*, *Reposicionamento* ou *Rejuvenescimento Urbano*.
    -   **O Briefing Inteligente**: Campo onde o usuário descreve o setor (ex: "Moda & Beleza") e a marca.
    -   **O Refino Dinâmico (V10.4)**: Ao digitar o briefing, o `handleRefineBriefing` consulta o backend e já sugere as **Keywords Estratégicas** que alimentam os Círculos Culturais.

2.  **Processamento em Tempo Real**:
    -   O frontend envia esse texto para o `BusinessSynthesizer`.
    -   O sistema identifica os **Círculos Culturais**, calcula o **Cultural Alpha** inicial e gera os `strategic_kpis`.
    -   **Persistência**: Os dados são salvos nas tabelas `profiles` e `projects` do Supabase para personalizar a experiência futura.

---

## 📊 Fase 3: Dashboard Dinâmico (Storytelling Contextual)

O sistema redireciona para `/dashboard` injetando a **Lente** correspondente:

### A. Se a escolha foi "Lançamento" (View de Ação)
- **Hero**: `VelocityGauge.tsx` (Velocímetro de Momentum).
- **Narrativa**: "Sua janela de oportunidade para o termo X fecha em 15 dias."
- **KPI**: Delta de Velocidade (Impact on Momentum).

### B. Se a escolha foi "Pesquisa" (View de Exploração)
- **Hero**: `CirclesSunburst.tsx` + `SemanticGraph.ts` (Grafo).
- **Narrativa**: "Existem 3 nichos de 'K-pop Periférico' que sua concorrência ignora."
- **KPI**: Discovery Yield (Gaps Culturais).

---

## 📈 Fase 4: O Loop de Alpha (Performance)

1.  **Monitoramento 24/7**: O usuário recebe alertas de "Desvio de Padrão".
2.  **Relatório de Cultural Alpha**: 
    - "Sua estratégia baseada no sinal X gerou +15% de engajamento orgânico do que a média do mercado."
3.  **H.I.T.L. (Human-in-the-Loop)**:
    - O sistema pergunta: "Este sinal foi útil?". 
    - A resposta alimenta o `ActiveLearning` no Supabase e ajusta os pesos do `AutomatedLearningEngine`.

---

## 🛠️ Próximo Passo Técnico
- [ ] Transformar o `app/page.tsx` na porta de entrada estratégica.
- [ ] Criar o componente `GoalSelector.tsx` para o Onboarding.
- [ ] Mapear o redirecionamento `/onboarding -> /dashboard?lens=...`
