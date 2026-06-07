# Metodologia Cultural Alpha (V10.4)
## Base Teórica: Market Entropy & P75 Threshold (Gutsche, 2018)

O **Cultural Alpha (α)** é a medida de desvio estratégico de uma marca em relação à "Inércia Narrativa" do seu setor.

### 1. O Problema: O Eco dos Clichês
A maioria das ferramentas de monitoramento foca em *Volume*. No entanto, alto volume geralmente indica **Clichês Consolidados**. 
- Se todos estão falando de "Sustentabilidade" da mesma forma, a eficácia marginal de uma nova campanha sobre o tema é próxima de zero. Isso chamamos de **Entropia Máxima**.

### 2. A Solução: Sinais Fracos (Weak Signals)
O Pulso utiliza o modelo de clusters para encontrar sinais com as seguintes características:
- **Baixa Frequência:** Pouca gente fala ainda.
- **Alta Coerência:** Quem fala, fala com profundidade e conexão emocional.
- **Vetor de Deslocamento:** O sinal está se movendo de um nicho específico para o comportamento de massa.

### 3. O Cálculo do Benchmark
O benchmark que aparece no Dashboard não é uma "média de likes", mas sim uma comparação de **Clusters de Significado**:
- **Baseline (Média):** Padrão de 70-80% do conteúdo do setor que ressoa apenas com o "óbvio".
- **Alpha Forecast:** A capacidade da sua marca (via briefing de onboarding) de se conectar com os 5% de sinais que definirão os próximos 90 dias do mercado.

### 4. Exposição Técnica: O Algoritmo do Alpha
O `BusinessSynthesizer` calcula o desvio estratégico utilizando a geometria do espaço vetorial do **BERTimbau**:

1.  **V_Centroid (O Clichê / Mainstream Twin):** Representa o "buraco negro" da categoria. É a média vetorial de todos os sinais de alto volume e baixa raridade do setor.
2.  **V_Project (O DNA da Marca):** É o embedding gerado a partir do seu briefing e das seleções de sinais "Ativos".
3.  **Digital Twin B (O Target Visionário):** Cluster de sinais de nicho com alta coerência, representando o "futuro antecipado".
4.  **Cálculo da Similaridade de Cosseno Inversa:**
    O **Cultural Alpha (α)** é a medida de o quanto seu projeto "escapa" da gravidade do clichê:
    $$α = 1 - \frac{A \cdot B}{\|A\| \|B\|}$$

Onde:
- **A** é o vetor do seu projeto ($V_{Project}$).
- **B** é o vetor do centro gravitacional do mercado ($V_{Centroid}$).

**Interpretação Estratégica:**
- **$α \to 0$ (Inércia):** Sua marca fala o que todos já sabem. Investimento com baixo retorno de atenção.
- **$α \to 1$ (Disrupção Coerente):** Sua marca ocupa um território que o mercado só descobrirá em 90 dias (D+90). Alto retorno de descoberta.

### 5. O Índice de Potencial Cultural (IPC) - V10.4
O **Índice de Potencial Cultural (IPC)** é o multiplicador que transforma o desvio geométrico (Alpha) em uma métrica de execução. Ele é calculado a partir dos sinais "Ativados" pelo usuário:

$$IPC = α \times \left( \frac{R_c + T_r + P_a}{3} \right)$$

Onde:
- **$R_c$ (Recorrência):** Persistência do sinal no tempo (volume histórico).
- **$T_r$ (Taxa de Reação):** Nível de resposta emocional/engajamento capturado nos Digital Twins.
- **$P_a$ (Predição):** Probabilidade de o sinal furar a bolha em D+90.

**Interpretação:**
- **IPC Baixo:** Sinal inovador, mas sem tração ou "fogo" para escala.
- **IPC Alto:** O "Sweet Spot". Alta disrupção estratégica com validação social comprovada.

> **Analogia Prática (The Great Leap):**
> Imagine que o **Alpha (α)** é o *tamanho do salto* que sua marca deu para fora do clichê. Já o **Ganhos de Sinais (IPC)** é a *potência desse salto* (se ele vai ter fôlego para durar 90 dias ou se vai morrer na praia).
> 
> - O gráfico do **Benchmark** mostra **onde** você está no espaço cultural.
> - O **Intelligence Bar** mostra o **potencial de ganho** se você seguir aquela narrativa específica.

### 6. O Loop de Feedback (RLHF - Ativo, Declinado, Monitorando)
As ações do usuário no dashboard impactam diretamente a inteligência:
- **Ativar Sinal:** O sinal vira um "Nó de Gravidade". A próxima atualização prioritiza sinais no mesmo quadrante semântico.
- **Declinar Sinal:** Cria uma "Zona de Exclusão". Reduz o ruído de clichês que o modelo confundiu com inovação.
- **Monitorando:** Define um "Watchdog". Alerta o usuário se a *Velocity* do sinal ultrapassar o limiar de mercado (D+90).

---
*Documento gerado automaticamente pelo Futuruma Pulse Engine v10.4*

*Base teórica: Grieves, M. (2014). Digital Twin: Manufacturing Excellence through Virtual Factory Replication.*
