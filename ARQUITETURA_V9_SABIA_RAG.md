# 🏗️ ARQUITETURA V9.5: CÉREBRO CULTURAL HÍBRIDO (SABIÁ-2 + RAG + OLLAMA)
> **Integrando Inteligência Antropológica Fixa com Semântica Dinâmica Brasileira**

---

## 🛰️ 1. O FLUXO DE DADOS: DO ONBOARDING AO INSIGHT
O sistema opera em cinco camadas principais, integrando APIs externas, Modelos de Linguagem (LLMs/SLMs) e Algoritmos de Machine Learning proprietários.

### Camada 1: Entrada & Onboarding (User Intent)
- **Inputs:** Nome da Marca, Setor, Objetivo de Negócio e **Lente Estratégica** (Proteção, Ação ou Exploração).
- **Extração de Entidades:** O sistema identifica termos-chave como "Corre", "Geração Z", "Periferia".

### Camada 2: Inteligência Geocultural (SABIÁ-2 / Maritaca AI)
- **Função:** Expansão Semântica Brasileira.
- **Camada de Explicação:** Para cada termo expandido, o Sabiá-2 define:
  - **O QUE É:** A definição antropológica profunda.
  - **COMO ATIVAR:** Recomendações táticas para execução de marca.

### Camada 3: Camada RAG & Evidence (Retrieval-Augmented Generation)
- **Fontes de Dados:** Supabase, APIs de Sinais, Ads Library.
- **Factualidade (Provas):** Cada insight recuperado deve conter uma **URL de Verificação** (Notícia, Campanha, Vídeo) para validar a afirmação estratégica. Ex: *"A Marca X falhou no cluster periférico"* → Link para análise de sentimento da campanha X.

### Camada 4: Motor de Síntese & Hidden Layers (Machine Learning Interno)
Aqui residem as camadas que operam "sob o capô":
- **Stability Engine (`stability.py`):** Calcula se um grupo cultural é estável ou está se fragmentando (ARI).
- **Cross-Impact Matrix (`cross_impact.py`):** Avalia como o sinal "Corre" afeta outras dimensões (PEST).
- **Inteligência Multimodal (Transformers & Visão):** 
  - **Transformers (BERTimbau):** NLP de alta precisão para capturar ironia, gírias e sentimentos profundos que modelos genéricos ignoram.
  - **Computer Vision (Visual Scraping):** Analisa criativos (imagens/vídeos) para detectar dissonâncias estéticas entre a marca e o território.
- **Sentiment & Authenticity Classifiers:** NLP baseado em BERTimbau para validar se o sinal é "Genuíno" ou "Superficial".

### Camada 5: Geração de Ativos (OLLAMA / Llama-3)
- **Entrega Final:** Manifestos, Blueprints, Roteiros Criativos.
- **Prompt Enriquecido:** O Ollama não recebe "Escreva sobre X". Ele recebe: *"Escreva sobre X, considerando a nuance cultural Y trazida pelo Sabiá-2, sob a ótica da marca Z e com foco na oportunidade de mercado identificada no RAG"*.

---

## ⚙️ 2. MAPA TECNOLÓGICO (TECH STACK)

| Componente | Tecnologia | Camada Oculta / Papel |
| :--- | :--- | :--- |
| **Estabilidade** | `clustering/stability.py` | Mede a saúde do território cultural (ARI). |
| **Causalidade** | `intelligence/cross_impact.py` | Simula efeitos dominó (Se cair a economia, o 'Corre' aumenta?). |
| **Transformers** | BERTimbau (via HuggingFace) | O "corretor de gírias" e sentimentos nativos. |
| **Visão Comp.** | OpenCV / PyTorch (VScraping) | Capturar a estética de campanhas concorrentes. |
| **Expansão BR** | Sabiá-2 (Maritaca) | O tradutor de nuances e "gírias" nativas. |
| **Fatos e Provas** | RAG Engine (Vector DB) | Garante que o insight não é uma alucinação da IA. |
| **Execução Local** | Ollama | Rapidez e privacidade no processamento final. |

---

## 📈 3. O RESULTADO: O PRONTUÁRIO ESTRATÉGICO
O usuário não recebe apenas um texto, mas um **Prontuário** que contém:
1. **Definição Cultural:** Explicação de cada conceito ativado.
2. **Guia de Execução:** Como a marca deve agir (Do's and Don'ts).
3. **Pilar de Verdade:** Links e evidências visuais/noticiosas que sustentam a estratégia.

---
*Este documento define o padrão de integração para a V9.5 no Culture Pulse.*
