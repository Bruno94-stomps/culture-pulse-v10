# 🌱 Signal Nature Classification - Sistema de Detecção de Nuances Culturais

**Versão:** V9.1  
**Data:** 09/02/2026  
**Status:** ✅ 100% Implementado

---

## 🎯 Visão Geral

O **Signal Nature Classifier** é um sistema avançado que **detecta nuances culturais profundas** em sinais fracos, indo muito além de palavras-chave. O sistema identifica **códigos linguísticos**, **tensões culturais reais**, **origem geográfica/social**, **crossovers autênticos** e **crescimento orgânico**.

### Por Que Nuances Culturais?

Culture Pulse não captura apenas termos que o usuário pesquisa, mas sim **o que está acontecendo DENTRO daquele segmento**:
- Movimentos e códigos culturais emergentes
- Regionalismos autênticos vs simulados
- Tendências bottom-up (periferia → mainstream)
- Dores e tensões culturais latentes
- Crossovers genuínos entre círculos culturais

---

## 📊 5 Categorias de Natureza Cultural

### 1. 🌱 **ORGÂNICO** 
Movimento cultural autêntico com códigos próprios da comunidade

**Características:**
- Gírias/regionalismos nativos (ex: "rolê aleatório" - periferia SP)
- Tensões culturais reais (ex: classe vs ostentação)
- Origem concentrada em círculo específico (>70% uma região)
- Crescimento gradual (velocity < 3.0)
- Volume típico de weak signal (<1000 menções)

**Exemplos:**
- "Rolê aleatório" - gíria periferia SP viraliza naturalmente
- "Tech fleece roubado" - tensão periferias x marcas
- "Havaianas é luxo na gringa" - tensão classe/brasilidade

**Prioridade:** Se bot_risk=LOW → **✅ AUTÊNTICO (PRIORIDADE MÁXIMA)**

---

### 2. 🔊 **RESONÂNCIA**
Movimento autêntico que ganhou amplificação mas **manteve códigos culturais**

**Características:**
- Códigos autênticos preservados (score_organico > 40)
- Amplificação comercial moderada (20 < score_comercial < 50)
- Influencers da própria cultura amplificando
- Amplificação respeitosa (não descaracteriza)
- Regionalismos mantidos intactos

**Exemplos:**
- Funk carioca viral com DJ local impulsionando
- Havaianas + memes orgânicos amplificados
- Artista periférico com parceria marca (mantém códigos)

**Prioridade:** Se bot_risk=LOW → **🟢 LEGÍTIMO**

---

### 3. 💼 **COMERCIAL TRANSPARENTE**
Campanha comercial clara, não tenta simular cultura

**Características:**
- Hashtag oficial visível (#NikeAirMax)
- Marca assume autoria ("patrocinado" declarado)
- Não finge ser grassroots (não simula códigos)
- Score comercial alto (>50) + simulação baixa (<20)
- Links comerciais (www.marca.com)

**Exemplos:**
- #NikeAirMax lançamento oficial
- Campanha Coca-Cola festivais (assume ser patrocínio)
- Influencer com "publi" declarado

**Prioridade:** **🟢 NORMAL (catalogar, sem revisão necessária)**

---

### 4. 🎭 **SIMULAÇÃO CULTURAL** (Astroturfing)
Marketing que **simula** códigos culturais sem vivência real

**Características:**
- Gírias forçadas/deslocadas ("mano" + "premium")
- "Coolhunting" superficial (marca usa tendência sem entender)
- Mistura artificial PT-EN ("oi people, very bem")
- Tensões fabricadas (marca cria polêmica artificial)
- Origem difusa (surge em 5 cidades simultaneamente)

**Exemplos:**
- Marca gringa usando gíria de periferia errado
- Empresa finge "movimento espontâneo" fake
- Campanha usa "favela" + "luxo" sem contexto

**Prioridade:** Se bot_risk=HIGH → **🔴 CRÍTICO (fake grassroots + bots)**

---

### 5. ⚠️ **APROPRIAÇÃO**
Uso descontextualizado de símbolos/códigos culturais que gera tensão

**Características:**
- Símbolos sagrados (cocar, orixás, mandalas)
- Símbolos políticos usados comercialmente
- Regionalismo usado errado/fora de contexto
- Apagamento de origem cultural
- Score apropriação alto (>50)

**Exemplos:**
- Gringo usando cocar indígena em festa
- Marca usando símbolo religioso afro em produto
- "Tribal" / "exótico" / "primitivo" (estereótipos)

**Prioridade:** **🔴 CRÍTICO (revisar imediatamente)**

---

## 🎨 Matriz de Priorização Bot Risk × Natureza

| Bot Risk | ORGÂNICO | RESONÂNCIA | COMERCIAL | SIMULAÇÃO | APROPRIAÇÃO |
|----------|----------|-----------|-----------|-----------|-------------|
| **HIGH** | 🟡 Validar<br>(Bot ou código real?) | 🟡 Suspeito<br>(Bots pagos?) | 🟢 Normal<br>(Campanha c/ bots) | 🔴 **CRÍTICO**<br>(Fake culture + bots) | 🔴 **CRÍTICO**<br>(Apropriação massiva) |
| **MEDIUM** | 🟢 Provável Real<br>(Comunidade específica) | 🟢 Comum<br>(Amplif. natural) | 🟢 Normal<br>(Campanha mista) | 🟡 Investigar<br>(Simula nuance?) | 🟡 Atenção<br>(Apropriação sutil?) |
| **LOW** | ✅ **WEAK SIGNAL PURO**<br>(Nuance cultural real) | 🟢 Legítimo<br>(Amplif. orgânica) | 🟢 Transparente<br>(Não tenta enganar) | 🟡 Atenção<br>(Simula mas sutil) | 🟡 Validar<br>(É apropriação?) |

### Legenda de Prioridade:
- 🔴 **CRÍTICO**: Revisar imediatamente e considerar alerta automático
- 🟡 **INVESTIGAR**: Agendar revisão manual nas próximas 24h
- 🟢 **NORMAL**: Monitorar evolução, revisar se escalar
- ✅ **AUTÊNTICO**: PRIORIZAR para análise! Verdadeiro weak signal cultural

---

## 🔍 Como Detectamos Nuances Culturais (Heurísticas)

### 1. **Códigos Linguísticos**

**ORGÂNICO:**
```python
# Gírias/regionalismos nativos detectados:
- SP Periferia: "rolê", "quebrada", "corre", "mano", "truta"
- Rio Favela: "bonde", "papo reto", "suave", "responsa"
- Nordeste: "oxente", "vixe", "massa", "arretado", "cabra"
- Sul: "tchê", "bah", "guri", "prenda"
- Nacional: "cara", "tipo assim", "né", "cê é loko"

# Score: +10 pontos por código autêntico encontrado
```

**SIMULAÇÃO:**
```python
# Gírias forçadas/deslocadas:
- "people" + "very bem" (mistura artificial EN-PT)
- "mano" + "premium" (gíria + contexto elite deslocado)
- "autêntico" + "campanha" (auto-declaração suspeita)

# Score: +20 pontos simulação por padrão detectado
```

---

### 2. **Tensões Culturais**

**REAL (orgânico):**
```python
# Tensões latentes que explodem organicamente:
- "Havaianas é luxo na gringa" → Tensão classe/brasilidade
- "Tech fleece roubado" → Tensão periferias/marcas
- "Ostentação" + "desigualdade" → Tensão classe social

# Score: +20 × intensidade por tensão real detectada
```

**FABRICADA (simulação):**
```python
# "Tensão" criada por marketing:
- Marca cria polêmica artificial para gerar buzz
- Uso forçado de temas sociopolíticos em campanha
- Tensão sem lastro em comunidade real

# Score: +15 simulação se tensão sem origem clara
```

---

### 3. **Origem Geográfica/Social**

**CONCENTRADA (orgânico):**
```python
# >70% de uma região específica:
- TikTok periferia SP (85%) → Gíria nova
- Reddit r/brasil → Meme político local
- Instagram Nordeste (78%) → Regionalismo

# Score: +25 organico se concentração >70%
# Evidência: "Origem concentrada: Sudeste (85%)"
```

**DIFUSA (simulação):**
```python
# Termo surge em 5 cidades simultaneamente:
- Sem rastro em comunidades específicas
- Distribuição artificial (uniforme em todo Brasil)
- Concentração <30% em qualquer região

# Score: +15 simulação por origem difusa
# Flag: "Origem difusa/fabricada (sem concentração regional)"
```

---

### 4. **Crossovers Culturais (Dissonância)**

**GENUÍNO (orgânico):**
```python
# Contextos diferentes se encontram organicamente:
- "Maduro captura" (político) + "Nike roubada" (moda)
  → Humor brasileiro reagindo a evento real
- "Havaianas" (moda popular) + "gringa" (internacional)
  → Tensão classe/brasilidade espontânea

# Score: +20 organico se ≥2 contextos únicos
# Evidência: "Crossover cultural: político, moda"
```

**FORÇADO (simulação):**
```python
# Marca junta temas sem contexto:
- "Favela" + "luxo" sem vivência real
- "Sustentabilidade" + produto poluente (greenwashing)

# Detectado via apropriação ou simulação scores altos
```

---

### 5. **Crescimento Temporal**

**GRADUAL (orgânico):**
```python
# Crescimento orgânico comunitário:
Semana 1: 50 menções (comunidade origem)
Semana 2: 200 menções (círculo amplia)
Semana 3: 800 menções (crossover mainstream)

# Velocity < 3.0 + Volume < 1000
# Score: +20 organico + +15 growth
# Evidência: "Crescimento orgânico (velocity: 2.3)"
```

**SPIKE ARTIFICIAL (simulação):**
```python
# Campanha paga imediata:
Dia 1: 0 menções
Dia 2: 5000 menções (lançamento pago)

# Velocity > 8.0
# Score: +20 simulação
# Flag: "Spike suspeito (velocity: 10.5)"
```

---

### 6. **Marcadores Comerciais**

```python
# Regex patterns detectam:
- r'#\w+Oficial'  # Hashtag oficial
- r'(patrocinado|publi|publicidade|ad)'
- r'(lançamento|nova coleção|disponível)'
- r'(compre|adquira|garanta|aproveite)'
- r'www\.\w+\.com'  # Links comerciais
- r'(desconto|promoção|oferta)'

# Score: +15 comercial por match
# Se >50 comercial + <20 simulação = COMERCIAL TRANSPARENTE
```

---

### 7. **Apropriação Cultural**

```python
# Símbolos sagrados/políticos:
- 'cocar', 'orixá', 'mandala', 'cruz', 'estrela de davi'
- Religiosos afro: 'candomblé', 'umbanda', 'axé'
- Indígenas: 'tribal', 'primitivo', 'selvagem', 'exótico'
- Estereótipos: 'sambista', 'malandro', 'sensual', 'tropical paradise'

# Score: +15 apropriação por termo encontrado
# Se uso em contexto comercial: +30 adicional
# Flag: "ALERTA: Símbolos culturais em contexto comercial"
```

---

## 🧮 Lógica de Classificação Final

### Prioridade de Categorização:

1. **APROPRIAÇÃO** (se `score_apropriacao > 50`) → Confiança até 95%
   - Crítico, sempre priorizar

2. **SIMULAÇÃO** (se `score_simulacao > 40`) → Confiança até 90%
   - Astroturfing identificado

3. **COMERCIAL** (se `score_comercial > 50` AND `score_simulacao < 20`) → Confiança até 85%
   - Campanha transparente, não tenta enganar

4. **RESONÂNCIA** (se `score_organico > 40` AND `20 < score_comercial < 50`) → Confiança até 80%
   - Autêntico + amplificação que preserva códigos

5. **ORGÂNICO** (se `score_organico > 40`) → Confiança até 90%
   - Padrão para weak signals culturais reais

6. **AMBÍGUO** (demais casos) → Confiança ≤60%
   - Usar score dominante mas sinalizar baixa confiança

---

## 📊 Output do Classificador

### SignalNatureResult

```python
{
    'categoria': 'ORGÂNICO',  # ou RESONÂNCIA/COMERCIAL/SIMULAÇÃO/APROPRIAÇÃO
    'confianca': 0.87,  # 0-1
    'score_organico': 75.0,  # 0-100
    'score_comercial': 15.0,  # 0-100
    'score_apropriacao': 0.0,  # 0-100
    'evidencias': [
        'Códigos autênticos sp_periferia: rolê, mano, quebrada',
        'Origem concentrada: Sudeste (85%)',
        'Tensão cultural real: classe vs ostentação (70%)',
        'Crossover cultural: político, moda',
        'Crescimento orgânico (velocity: 2.3)'
    ],
    'flags': [
        # Vazio se tudo OK, ou:
        'Simulação detectada: mistura artificial',
        'Apropriação simbolos_sagrados: cocar, orixá'
    ],
    'nuances_detectadas': {
        'codigos_autenticidade': ['rolê', 'mano', 'quebrada'],
        'tensoes_reais': 2,  # Número de tensões com intensity >0.5
        'origem_especifica': True,  # Origem concentrada
        'crossover_detectado': True,  # ≥2 contextos
        'crescimento_organico': True,  # Velocity <3.0 + Volume <1000
        'plataformas_autenticidade': 25,  # Score de plataformas
        'scores': {
            'organico': 75.0,
            'comercial': 15.0,
            'apropriacao': 0.0,
            'simulacao': 10.0
        }
    }
}
```

---

## 🎯 Integração no Pipeline

### Sequência de Execução:

```
1. COLETA (data_collectors.py)
   ↓ CulturalSignals

2. BOT DETECTION (WeakSignalDetector._apply_confidence_factors)
   ↓ bot_score, bot_risk_level, confidence_factor

3. ANÁLISE WEAK SIGNALS (WeakSignalDetector._analyze_term_signals)
   ↓ weak_signal_score, contextos, tensoes, plataformas

4. ★ NATURE CLASSIFICATION (SignalNatureClassifier.classify) ★
   ↓ signal_nature, nature_confidence, cultural_nuances
   
5. RECOMENDAÇÃO MATRIZ (SignalNatureClassifier.get_recommendation)
   ↓ priority_level, review_recommendation

6. DASHBOARD (futuruma_dashboard.render_weak_signal_card)
   ↓ Visualização completa Bot × Nature
```

### Campos Adicionados ao WeakSignal:

```python
@dataclass
class WeakSignal:
    # ... campos existentes ...
    
    # NOVO V9.1: Signal Nature Classification
    signal_nature: str = "ORGÂNICO"
    nature_confidence: float = 0.0
    nature_scores: Dict[str, float] = field(default_factory=dict)
    cultural_nuances: Dict[str, Any] = field(default_factory=dict)
    nature_evidences: List[str] = field(default_factory=list)
    nature_flags: List[str] = field(default_factory=list)
    priority_level: str = "MÉDIA"
    review_recommendation: str = ""
```

---

## 📱 Visualização no Dashboard

### 1. Card Individual (render_weak_signal_card)

**Exibe:**
- Badge colorido por categoria (🌱/🔊/💼/🎭/⚠️)
- Prioridade combinada Bot × Nature
- Confiança da classificação
- Evidências culturais detectadas (expander)
- Flags de atenção (expander)
- Recomendação de revisão

**Exemplo:**
```
✅ 🌱 ORGÂNICO + Bot LOW = WEAK SIGNAL PURO! | Confiança: 87%

🔍 Evidências de Natureza Cultural:
- Códigos autênticos sp_periferia: rolê, mano
- Origem concentrada: Sudeste (85%)
- Tensão cultural real: classe vs ostentação (70%)

📋 Recomendação: PRIORIZAR para análise de weak signal! 
Nuances culturais genuínas detectadas
```

---

### 2. Resumo Global (antes dos cards)

**Métricas:**
- 5 colunas: Count por categoria
- Help text explicando cada categoria

**Matriz 3×5:**
- Tabela Bot Risk (rows) × Nature (cols)
- Cores: 🔴 ALTO (≥5) | 🟡 MÉDIO (3-4) | 🔵 BAIXO (1-2) | 🟢 NENHUM (0)
- Identifica visualmente combinações CRÍTICAS

---

## 🧪 Casos de Teste

### Caso 1: ORGÂNICO (Ideal Weak Signal)
```python
Termo: "rolê aleatório"
Menções: ["os cria tão fazendo rolê aleatório na quebrada", "rolê aleatório virou moda"]
Contextos: ['comportamento', 'periferia']
Plataformas: ['tiktok', 'instagram']
Tensões: [{'type': 'classe vs centro', 'intensity': 0.75}]
Velocity: 2.1
Volume: 350
Sentiment: 0.65

→ RESULTADO: ORGÂNICO (conf: 0.89)
   Evidências: Códigos sp_periferia, origem concentrada, tensão real
   Priority: AUTÊNTICO (se bot=LOW)
```

---

### Caso 2: COMERCIAL TRANSPARENTE
```python
Termo: "Nike Air Max lançamento"
Menções: ["#NikeAirMaxOficial disponível agora", "compre no site nike.com"]
Contextos: ['moda', 'tecnologia']
Plataformas: ['youtube', 'instagram', 'facebook']
Tensões: []
Velocity: 8.5
Volume: 5200
Sentiment: 0.45

→ RESULTADO: COMERCIAL (conf: 0.82)
   Evidências: Hashtag oficial, links comerciais, lançamento
   Priority: NORMAL (catalogar)
```

---

### Caso 3: SIMULAÇÃO CULTURAL (Astroturfing)
```python
Termo: "movimento orgânico favela chic"
Menções: ["autêntica expressão do povo", "movimento genuíno das comunidades"]
Contextos: ['moda', 'social']
Plataformas: ['instagram', 'facebook', 'youtube']
Tensões: []  # Nenhuma tensão real detectada
Velocity: 12.0  # Spike artificial
Volume: 8000  # Muito alto para weak signal
Sentiment: 0.55
Origem: Difusa (30% cada região - artificial)

→ RESULTADO: SIMULAÇÃO (conf: 0.85)
   Flags: Auto-declaração "genuíno", origem difusa, spike suspeito
   Priority: CRÍTICO (se bot=HIGH)
```

---

### Caso 4: APROPRIAÇÃO CULTURAL
```python
Termo: "cocar fashion trend"
Menções: ["tribal vibes", "exotic accessories", "primitive style"]
Contextos: ['moda', 'internacional']
Plataformas: ['instagram', 'pinterest']
Tensões: []
Comercial: Sim (links de venda)
Símbolos: ['cocar', 'tribal', 'primitive', 'exotic']

→ RESULTADO: APROPRIAÇÃO (conf: 0.92)
   Flags: Símbolos indígenas em contexto comercial, estereótipos
   Priority: CRÍTICO
```

---

### Caso 5: RESONÂNCIA (Autêntico + Amplificação)
```python
Termo: "funk carioca internacional"
Menções: ["DJ favela levando funk pro mundo", "cultura da Rocinha"]
Contextos: ['musica', 'brasilidade']
Plataformas: ['spotify', 'youtube', 'instagram']
Tensões: [{'type': 'local vs global', 'intensity': 0.60}]
Velocity: 4.2
Volume: 1800
Comercial: Parceria marca (30 score)
Códigos autênticos: ['bonde', 'responsa', 'favela']

→ RESULTADO: RESONÂNCIA (conf: 0.78)
   Evidências: Códigos autênticos preservados, amplificação respeitosa
   Priority: LEGÍTIMO
```

---

## 📚 Referências no Código

- **Classificador:** `core/signal_nature_classifier.py`
- **Integração:** `products/weak_signal_detector.py` (linhas 850-920)
- **Dashboard:** `products/futuruma_dashboard.py` (linhas 620-670, 3418-3480)
- **Dataclass:** `products/weak_signal_detector.py` (linhas 185-195)

---

## 🔄 Roadmap Futuro

### Fase 2 (1-2 meses): Ground Truth Collection
- [ ] Criar CLI `collect_nature_ground_truth.py`
- [ ] Coletar 200+ exemplos rotulados manualmente
- [ ] Validar acurácia das heurísticas atuais

### Fase 3 (3-4 meses): Modelo Supervisionado
- [ ] Treinar XGBoost com ground truth coletado
- [ ] Usar heurísticas como features + labels manuais
- [ ] Híbrido: 70% modelo + 30% heurísticas

### Fase 4 (6+ meses): Deep Learning
- [ ] Fine-tune BERTimbau para nuances culturais
- [ ] Modelo end-to-end: texto → natureza
- [ ] Detecção automática de novos códigos linguísticos

---

**Última atualização:** 09/02/2026  
**Responsável:** Culture Pulse V9.1 Team  
**Status:** ✅ Sistema completo implementado e funcional
