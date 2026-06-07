# 🧠 ENGINE DE LEITURA DE CONTEXTO E OBJETIVOS (V9.5)
> **Como o Culture Pulse traduz intenções de negócio em inteligência cultural.**

---

## 🔍 1. O FLUXO DE LEITURA: DO TEXTO AO VETOR ESTRATÉGICO
Diferente de sistemas de busca comuns, o Culture Pulse não trata o seu **Objetivo** e **Contexto** como palavras-chave, mas como um **DNA Dinâmico** que filtra todo o ecossistema de dados.

### Passo 1: Desconstrução do Onboarding
Ao inserir o contexto (ex: *"Explorar como a Geração Z periférica ressignifica o luxo através do 'corre' diário"*), o motor **`BusinessSynthesizer`** realiza:
- **Extração de Entidades:** Identifica *Público* (Gen Z), *Território* (Periferia), *Tema* (Luxo) e *Behavior* (Corre).
- **Injeção Semântica (BERTimbau):** O sistema expande esses termos para gírias e sinônimos culturais brasileiros que o usuário não escreveu, mas que são intrínsecos ao tema.

### Passo 2: Ativação da "Lente de Intenção" (Lenses)
O **Objetivo** (Exploração, Ação ou Proteção) funciona como um filtro de "Ganho" no sinal:
- **Lente AÇÃO:** Prioriza sinais com alta **Velocidade** e **Volume**, focando em conversão e tendências imediatas.
- **Lente PROTEÇÃO:** Prioriza sinais de **Tensão** e **Instabilidade**, focando em gestão de crise e preservação de marca.
- **Lente EXPLORAÇÃO:** Prioriza sinais de alta **Dissonância**, focando em nichos que ainda não viraram mainstream (Oceano Azul).

---

## 🕸️ 2. MAPEAMENTO DINÂMICO DE CÍRCULOS CULTURAIS
O sistema possui 16 "Círculos de Afinidade" pré-mapeados. A leitura do seu contexto ativa esses círculos através de uma **Matriz de Interseção**:

| Se o seu Contexto menciona... | O Sistema Ativa os Círculos: | Por que? (Lógica de Negócio) |
| :--- | :--- | :--- |
| "Comunidade", "Vizinhança" | `familia_comunidade` | Foco em micro-influência e confiança local. |
| "Inovação", "Tech", "Apps" | `tecnologia_acessivel` | Foco em como o digital se adapta à base da pirâmide. |
| "Alegria", "Show", "Rua" | `festa_celebracao` | Foco em momentos de alta ressonância emocional. |
| "Sustentável", "Lixo", "Futuro" | `sustentabilidade_consciente` | Foco em desdobramentos PEST (Ambiental/Social). |

### A "Alquimia" do Mapeamento
O sistema calcula um **Score de Afinidade** entre o seu texto e as `authenticity_markers` de cada círculo. Se a afinidade for > 0.75, esse círculo passa a ser o seu **"Território de Monitoramento Primário"**.

---

## ⚡ 3. O PAPEL DO RAG NA LEITURA (MEMÓRIA VIVA)
O sistema usa o seu contexto para realizar o **RAG (Retrieval-Augmented Generation)** no Supabase:
1. **Recuperação:** Busca nos últimos 30 dias de sinais reais quem está falando o que você escreveu.
2. **Aumento:** Enriquece o seu texto com as tensões detectadas nesses sinais (ex: se você escreveu sobre "Luxo", ele injeta a tensão "Luxo vs. Ostentação Periférica").
3. **Geração:** O resultado final é um insight que parece ler a sua mente, porque ele conectou a sua **Intenção** à **Realidade das Ruas**.

---

## 📦 4. MATERIALIZAÇÃO: DO CONTEXTO AO ATIVO
A predição final que você vê no Dashboard é o resultado de:
> **(Vetor do Usuário × Sinais Reais) + Lente Estratégica = Próxima Melhor Ação**

Isso garante que, se dois usuários monitorarem o mesmo tópico ("Moda"), mas um tiver o objetivo de **Ação** e o outro de **Proteção**, seus Dashboards e Assets gerados serão **completamente diferentes**, adaptados aos seus contextos de negócio únicos.

---

## 🚀 5. EXEMPLO PRÁTICO DE MATERIALIZAÇÃO (SIMULAÇÃO V9.5)
Para ilustrar como o motor conecta as pontas, veja o resultado de uma simulação real executada pelo sistema:

### **Cenário de Onboarding**
- **Marca:** `Natura`
- **Contexto do Usuário:** *"Explorar como a Geração Z periférica ressignifica o luxo através do 'corre' diário e da sustentabilidade popular."*
- **Objetivo (Lente):** `Exploração`

### **O que o motor processou:**
1. **Ativação de Círculos:** O sistema detectou afinidade com os círculos `IMPROVISO_CRIATIVIDADE` (pelo termo 'corre'), `SUSTENTABILIDADE_CONSCIENTE` (pelo termo 'sustentabilidade popular') e `IDENTIDADE_DIGITAL` (pela 'Geração Z').
2. **Aplicação da Lente:** Por ser uma lente de *Exploração*, o motor ignorou dados de volume massivo (mainstream) e priorizou sinais de **Alta Dissonância** (ruídos de nicho).
3. **Inferência Causal:** O sistema identificou que, para este público, a Sustentabilidade não é um "valor de luxo clássico", mas uma **"Inteligência de Sobrevivência"**.

### **Asset Gerado (O que o usuário recebe):**
- **Título:** *Manifesto Natura: O Novo Luxo do Corre*
- **Ação Recomendada:** *"Criar conteúdo com criadores do 'Grau' e 'Moda Circular Periférica' no Sudeste."*
- **Score de Pioneirismo:** `88% (Dissonância Narrativa Alta)`

---
*Este documento explica a arquitetura de inteligência por trás da interface do Culture Pulse V9.5.*
