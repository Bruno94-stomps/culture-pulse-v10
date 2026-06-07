# 🧠 Storytelling Estratégico & Visual: Futurama Dashboard (V9.9)

Este documento define a narrativa de produto e a jornada do usuário para o Dashboard do Futurama, conectando os componentes técnicos ao valor de negócio.

---

## 🧭 1. A Jornada do Onboarding (O "Aha! Moment")

O objetivo é transformar dados frios em **Inteligência de Antecipação** desde o primeiro segundo.

### O Gancho (A Pergunta Certa)
Em vez de um dashboard genérico, iniciamos com a provocação central:
> **"Qual é o seu momento cultural hoje?"**
Isso tira o usuário da passividade e o coloca no modo "Investigador/Tomador de Decisão".

### Fluxo de Onboarding Sugerido:
1. **Empty State Educativo:** Se o banco de dados estiver vazio, não mostramos "0 dados", mostramos: *"O Radar está em silêncio... Conecte uma fonte de dados (TikTok, Reddit, YT) para começar a ouvir a Alma Brasileira."*
2. **Setup do Gêmeo Digital:** Peça ao usuário para definir seu contexto (Ex: "Mercado de Luxo", "Geração Z", "Política"). Isso calibra os radares.
3. **Primeiro Sinal:** Destaque imediatamente o sinal mais "quente" (Spike) para mostrar o poder do tempo real.

---

## 📊 2. Storytelling por Camadas de Gráficos

Cada gráfico no código deve responder a uma pergunta dramática do negócio:

| Componente | Pergunta Dramática (Storytelling) | Lógica Visual (Cyber-Anthropology) |
| :--- | :--- | :--- |
| **`SignalStream.tsx`** | *"O que o Brasil está sentindo agora?"* | Fluxo constante de cards com badges de **Spike** e **Sentimento**. |
| **`CulturalRadar.tsx`** | *"Como está o DNA da Alma Brasileira?"* | Radar de 6 dimensões (DNA Digital) com estética de *blueprint* neon. |
| **`StabilityRiskMatrix.tsx`** | *"Devo agir agora ou esperar?"* | Mapa tático 5x5: Verdes (Oportunidade) vs. Vermelhos (Risco de Cancelamento). |
| **`CausalGraph.tsx`** | *"De onde veio essa ideia?"* | Grafo de conexões mostrando a origem (Ex: Como um meme do Reddit virou tendência no YT). |

---

## 💡 3. Inteligência de Decisão (A Conexão Narrativa)

O valor real do Futurama está na **conexão entre os gráficos**:

- **Ação e Reação:** Se a `StabilityMatrix` mostra um sinal em **APROPRIAÇÃO**, o `CulturalRadar` deve mostrar queda em **AUTENTICIDADE**.
- **Radar de Tensão:** Se o `SentimentShift` for brusco, o dashboard deve emitir um alerta narrativo: *"Atenção: A narrativa 'X' está mudando de tom. Resiliência cultural em declínio."*

## 🔄 3.1 Conexão entre os Gráficos (O "Pulo do Gato" UX)
Para que o dashboard seja matador, os gráficos não devem ser estáticos, mas **conectados narrativamente**:
- **Drill-down de Causa:** Clique em uma célula "CRÍTICO" na Matriz para que o Radar se transforme, mostrando quais traços da 'Alma' estão em desequilíbrio para aquele sinal específico.
- **DNA Dinâmico:** Se a Matriz de Estabilidade detecta uma **'Apropriação Cultural'**, o Radar de Autenticidade (`CulturalRadar`) deve sofrer uma retração visual em tempo real, indicando perda de confiança do público.

---

## 🎨 4. Prompt para Figma Make (Direcional de Interface)

Use este prompt para gerar o design que suporte este storytelling:

```markdown
Role: Expert SaaS UI/UX Designer
Context: 'Futurama - Cultural AI Intelligence' Dashboard.

Architecture:
1. Header: Conversational search bar + 3 High-level KPIs (Momentum, Acceleration, Risk).
2. Central Visualization: Tactical 5x5 Heatmap (StabilityRiskMatrix) with glowing hover states that trigger "Actionable Intelligence" tooltips.
3. Sidebar: 'Brazilian Soul DNA' (CulturalRadar) with a digital blueprint look, using neon violet lines over a subtle dark grid.
4. Bottom Panel: 'Evidence Stream' (SignalsTable) with video thumbnails, platform icons, and 'Visual Proof' badges.

Aesthetic: Cyber-Anthropology. Dark Mode. 
Palete: Emerald (Opportunity), Amber (Monitoring), Crimson (Crisis), and Violet (Insight).
Typography: Inter or SF Pro (Clean & Professional).
Effect: Glassmorphism, subtle glowing edges. Interactive components that change visual weight based on 'Cultural Gravity'.
```

---

## 🚀 5. Checklist de Lançamento (Story-Ready)

- [ ] **Badges de Status:** Garantir que "Veracidade", "Aceleração" e "Risco" estão visíveis na tabela de sinais.
- [ ] **Tooltips Narrativos:** Em vez de "Score: 0.8", usar "Confiança de Tendência: Alta".
- [ ] **Empty States:** Garantir que o Dashboard "fale" com o usuário mesmo quando não há dados.
- [ ] **Cross-Chart Logic:** Clicar em uma célula da Matriz de Risco deve filtrar os sinais da tabela abaixo.

---
*Documento gerado para a V9.9 do ecossistema Futurama/Cultural Pulse.*
