# 🚀 SPRINT 4: Context Enricher Advanced Features - ROADMAP

**Data Planejamento**: 5 de fevereiro de 2026  
**Status**: 📋 Planejado (não iniciado)  
**Tempo Estimado**: 2-3 dias  
**Prioridade**: Alta

---

## 🎯 Objetivo Geral

Completar a integração do **Context Enricher** no dashboard, transformando análises básicas em **insights contextualizados e comparáveis** entre diferentes segmentos e projetos.

**Meta**: Transformar dashboard de **single-context** para **multi-context comparison** + persistência de histórico.

---

## 📦 Componentes a Implementar

### 1️⃣ BOTÃO [COMPARAR SEGMENTOS] - Priority: 🔴 ALTA

**Arquivo a criar**: `dashboard/components/segment_comparison.py` (~300 linhas)

#### Funcionalidade:

**render_segment_comparison_modal(signal, current_segment)**:
- Modal que reabre ao clicar botão em cada Signal Card
- **Side-by-side comparison** de 2 segmentos:
  ```
  ╔══════════════════════════════════════════════════════════╗
  ║        🔄 Comparar Segmentos                             ║
  ║══════════════════════════════════════════════════════════║
  ║                                                          ║
  ║  Sinal: "Street Food Brasileiro"                        ║
  ║                                                          ║
  ║  ┌─────────────────────────┬─────────────────────────┐  ║
  ║  │  Alimentação & Bebidas  │    Entretenimento       │  ║
  ║  ├─────────────────────────┼─────────────────────────┤  ║
  ║  │  Score: 87.3            │    Score: 62.1          │  ║
  ║  │  Relevância: Alta       │    Relevância: Média    │  ║
  ║  │                         │                         │  ║
  ║  │  Narrativas:            │    Narrativas:          │  ║
  ║  │  • Inovação culinária   │    • Festival de rua    │  ║
  ║  │  • Fusão regional       │    • Evento cultural    │  ║
  ║  │  • Food trucks trend    │    • Música + gastronomia│  ║
  ║  │                         │                         │  ║
  ║  │  Círculos:              │    Círculos:            │  ║
  ║  │  🍖 Gastronomia ★★★★★   │    🎭 Arte ★★★★         │  ║
  ║  │  🌿 Regional ★★★★       │    🎵 Música ★★★        │  ║
  ║  └─────────────────────────┴─────────────────────────┘  ║
  ║                                                          ║
  ║        [✓ Aplicar Segmento]    [✕ Cancelar]            ║
  ╚══════════════════════════════════════════════════════════╝
  ```

**Lógica de re-análise**:
```python
def compare_signal_across_segments(
    signal: WeakSignal,
    segment_a: str,  # Ex: "Alimentação & Bebidas"
    segment_b: str   # Ex: "Entretenimento & Mídia"
) -> Dict[str, ContextualAnalysis]:
    """
    Re-analisa o mesmo sinal com Context Enricher configurado
    para 2 segmentos diferentes.
    
    Returns:
        {
            'segment_a': {
                'score': float,
                'narrativas': List[str],
                'circulos_relevantes': Dict[str, float],
                'territorio_cultural': str,
                'evolucao_temporal': str,
                'rede_semantica': List[tuple]
            },
            'segment_b': {...}
        }
    """
    # 1. Criar 2 perfis temporários com segmentos diferentes
    # 2. Chamar ContextualIntelligenceEngine 2x
    # 3. Comparar resultados lado a lado
    # 4. Highlight diferenças (delta scores, narrativas únicas)
```

**Integração no dashboard**:
```python
# Em render_weak_signal_card() (linha ~1500)
col_actions = st.columns([1, 1])
with col_actions[0]:
    if st.button("🌍 Ver Contexto Cultural", key=f"ctx_{i}"):
        # Existing functionality
        
with col_actions[1]:
    if st.button("🔄 Comparar Segmentos", key=f"cmp_{i}"):
        render_segment_comparison_modal(ws, current_segment)
```

**Benefícios**:
- CMO vê como o mesmo sinal é percebido em segmentos diferentes
- Decisão de reposicionamento de produto
- Oportunidades cross-segment

---

### 2️⃣ PERSISTÊNCIA DE PROJETOS - Priority: 🟡 MÉDIA

**Arquivos a criar/modificar**:
- `dashboard/project_manager.py` (~400 linhas)
- `dashboard/storage/projects.json` (arquivo de dados)

#### Funcionalidade:

**ProjectManager class**:
```python
class ProjectManager:
    """Gerencia múltiplos projetos e histórico de análises"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.projects: Dict[str, Project] = {}
        self.load_projects()
    
    def create_project(self, user_profile: Dict) -> str:
        """Cria novo projeto e retorna ID"""
        project_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
        project = Project(
            id=project_id,
            profile=user_profile,
            created_at=datetime.now(),
            last_analysis=None,
            analysis_history=[]
        )
        self.projects[project_id] = project
        self.save_projects()
        return project_id
    
    def switch_project(self, project_id: str) -> bool:
        """Troca projeto ativo"""
        if project_id in self.projects:
            st.session_state.user_profile = self.projects[project_id].profile
            st.session_state.active_project_id = project_id
            return True
        return False
    
    def list_projects(self) -> List[Project]:
        """Lista todos os projetos"""
        return sorted(
            self.projects.values(),
            key=lambda p: p.last_analysis or p.created_at,
            reverse=True
        )
    
    def delete_project(self, project_id: str) -> bool:
        """Deleta projeto"""
        if project_id in self.projects:
            del self.projects[project_id]
            self.save_projects()
            return True
        return False
    
    def save_analysis(self, project_id: str, analysis_data: Dict):
        """Salva snapshot da análise atual"""
        if project_id in self.projects:
            self.projects[project_id].analysis_history.append({
                'timestamp': datetime.now().isoformat(),
                'weak_signals': analysis_data['signals'],
                'avg_score': analysis_data['avg_score'],
                'tensions': analysis_data['tensions'],
                'forecasts': analysis_data['forecasts']
            })
            self.projects[project_id].last_analysis = datetime.now()
            self.save_projects()
    
    def load_projects(self):
        """Carrega projetos do JSON"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.projects = {
                    pid: Project.from_dict(pdata)
                    for pid, pdata in data.items()
                }
    
    def save_projects(self):
        """Salva projetos no JSON"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(
                {pid: p.to_dict() for pid, p in self.projects.items()},
                f,
                indent=2,
                ensure_ascii=False
            )

@dataclass
class Project:
    """Representa um projeto de pesquisa"""
    id: str
    profile: Dict  # user_profile completo
    created_at: datetime
    last_analysis: Optional[datetime]
    analysis_history: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'profile': self.profile,
            'created_at': self.created_at.isoformat(),
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'analysis_history': self.analysis_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        return cls(
            id=data['id'],
            profile=data['profile'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_analysis=datetime.fromisoformat(data['last_analysis']) if data['last_analysis'] else None,
            analysis_history=data['analysis_history']
        )
```

**UI no dashboard** (Aba Projetos):
```python
# Em tab_projetos (linha 3146)
with tab_projetos:
    st.header("📁 Projetos de Pesquisa")
    
    # Inicializar ProjectManager
    if 'project_manager' not in st.session_state:
        storage_path = Path(__file__).parent.parent / "dashboard" / "storage" / "projects.json"
        st.session_state.project_manager = ProjectManager(storage_path)
    
    pm = st.session_state.project_manager
    
    # Projeto ativo
    active_project_id = st.session_state.get('active_project_id')
    if active_project_id:
        active_project = pm.projects[active_project_id]
        
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.subheader(f"✅ Projeto Ativo: {active_project.profile['brand_topic']}")
        with col_header2:
            if st.button("➕ Novo Projeto", type="primary"):
                show_welcome_modal()
    
    st.divider()
    
    # Lista de todos os projetos
    st.markdown("### 📋 Todos os Projetos")
    
    projects = pm.list_projects()
    if projects:
        for project in projects:
            with st.expander(
                f"{'🟢 ATIVO' if project.id == active_project_id else '⚪'} "
                f"{project.profile['brand_topic']} - {project.profile['segmento']}"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Criado", project.created_at.strftime("%d/%m/%Y"))
                    st.metric("Última Análise", 
                             project.last_analysis.strftime("%d/%m/%Y %H:%M") 
                             if project.last_analysis else "Nunca")
                
                with col2:
                    st.markdown("**Configuração:**")
                    st.markdown(f"• Segmento: {project.profile['segmento']}")
                    st.markdown(f"• Objetivo: {project.profile['objetivo']}")
                    st.markdown(f"• Audiências: {len(project.profile['audiencias'])}")
                
                with col3:
                    st.markdown("**Histórico:**")
                    st.markdown(f"• {len(project.analysis_history)} análises")
                    if project.analysis_history:
                        last_analysis = project.analysis_history[-1]
                        st.markdown(f"• Score médio: {last_analysis['avg_score']:.1f}")
                
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    if project.id != active_project_id:
                        if st.button("🔄 Ativar", key=f"activate_{project.id}"):
                            pm.switch_project(project.id)
                            st.rerun()
                
                with col_act2:
                    if st.button("✏️ Editar", key=f"edit_{project.id}"):
                        st.session_state.user_profile = project.profile
                        show_edit_profile_modal()
                
                with col_act3:
                    if st.button("🗑️ Deletar", key=f"delete_{project.id}"):
                        if project.id != active_project_id:
                            pm.delete_project(project.id)
                            st.success(f"Projeto {project.id} deletado")
                            st.rerun()
                        else:
                            st.error("Não pode deletar projeto ativo")
```

**Benefícios**:
- Gerenciar múltiplos clientes/marcas
- Histórico de análises (time series)
- Comparação entre projetos
- Não perder trabalho entre sessões

---

### 3️⃣ TEMPLATES AI DE KEYWORDS - Priority: 🟢 BAIXA

**Arquivo a modificar**: `dashboard/onboarding_manager.py`

#### Funcionalidade:

**Expandir biblioteca de templates** (linha 47):
```python
KEYWORDS_TEMPLATES = {
    "Alimentação & Bebidas": [
        "street food", "churrasco", "vegano", "delivery", "food truck",
        "gastronomia regional", "fusão culinária", "chef brasileiro"
    ],
    "Entretenimento & Mídia": [
        "streaming", "podcast", "série", "show", "festival",
        "cinema nacional", "artista independente", "viral"
    ],
    "Tecnologia & Inovação": [
        "IA", "blockchain", "startup", "app", "fintech",
        "SaaS", "deep tech", "inovação aberta"
    ],
    "Moda & Beleza": [
        "streetwear", "sustentável", "skincare", "make", "thrift",
        "moda brasileira", "upcycling", "beleza natural"
    ],
    "Educação & Cultura": [
        "edtech", "curso online", "livro", "literatura brasileira",
        "arte contemporânea", "patrimônio cultural", "museu"
    ],
    "Esportes & Fitness": [
        "crossfit", "yoga", "corrida", "futebol", "bike",
        "atleta brasileiro", "olimpíadas", "wellness"
    ],
    "Varejo & E-commerce": [
        "marketplace", "D2C", "omnichannel", "live commerce",
        "social commerce", "logística reversa", "cashback"
    ],
    "Turismo & Hospitalidade": [
        "turismo sustentável", "ecoturismo", "Airbnb", "hostel",
        "roteiro Brasil", "gastronomia local", "turismo de experiência"
    ],
    "Saúde & Bem-estar": [
        "telemedicina", "saúde mental", "fitoterapia", "medicina integrativa",
        "nutrição funcional", "autocuidado", "longevidade"
    ],
    "Finanças & Investimentos": [
        "criptomoeda", "investimento ESG", "educação financeira",
        "open banking", "PIX", "carteira digital", "crowdfunding"
    ],
    "Imóveis & Construção": [
        "construção sustentável", "retrofit", "co-living", "co-working",
        "smart city", "BIM", "certificação LEED"
    ],
    "Automotivo & Mobilidade": [
        "carro elétrico", "mobilidade urbana", "bicicleta", "patinete",
        "carsharing", "micromobilidade", "transporte público"
    ],
    "Outro": [
        "tendência", "inovação", "cultura brasileira", "comportamento",
        "consumidor", "sustentabilidade", "diversidade"
    ]
}
```

**AI Keyword Suggestion** (GPT-4 API):
```python
def generate_ai_keywords(brand_topic: str, segmento: str, objetivo: str) -> List[str]:
    """
    Gera keywords automaticamente usando GPT-4.
    
    Prompt:
    "Você é um analista cultural brasileiro. Gere 8-10 keywords relevantes
    para pesquisar sinais culturais sobre '{brand_topic}' no segmento de
    '{segmento}' com objetivo de '{objetivo}'.
    
    Keywords devem ser:
    - Específicas do contexto brasileiro
    - Mix de português e inglês (quando relevante)
    - Capturam tendências emergentes
    - Incluem gírias/termos coloquiais
    
    Retorne apenas a lista, separada por vírgulas."
    
    Returns:
        List de 8-10 keywords
    """
    # Implementação com OpenAI API
    # Fallback para templates se API falhar
```

**Botão no welcome modal** (linha 180):
```python
col_ai, col_manual = st.columns([1, 3])

with col_ai:
    if st.button("🤖 Gerar com IA", help="Usa GPT-4 para sugerir keywords"):
        with st.spinner("Gerando keywords..."):
            ai_keywords = generate_ai_keywords(
                brand_topic, segmento, objetivo
            )
            st.session_state.suggested_keywords = ai_keywords
            st.success(f"✨ {len(ai_keywords)} keywords geradas!")

with col_manual:
    keywords_input = st.text_area(
        "Keywords Customizadas",
        value=", ".join(st.session_state.get('suggested_keywords', [])),
        placeholder="Ex: festa junina, axé, verão nordeste",
        height=80
    )
```

**Benefícios**:
- Keywords mais precisas (AI-generated)
- Menos trabalho manual para usuário
- Cobertura melhor dos sinais culturais

---

### 4️⃣ EXPORTAÇÃO/IMPORTAÇÃO DE PERFIL - Priority: 🟢 BAIXA

**Arquivo a modificar**: `dashboard/onboarding_manager.py`

#### Funcionalidade:

**export_profile_json(profile: Dict) -> str**:
```python
def export_profile_json(profile: Dict) -> str:
    """
    Exporta perfil como JSON string.
    
    Returns:
        JSON string pronto para download
    """
    return json.dumps(profile, indent=2, ensure_ascii=False)

def import_profile_json(json_string: str) -> Optional[Dict]:
    """
    Importa perfil de JSON string.
    
    Returns:
        Dict com perfil ou None se inválido
    """
    try:
        profile = json.loads(json_string)
        
        # Validar campos obrigatórios
        required_fields = ['brand_topic', 'segmento', 'objetivo']
        if all(field in profile for field in required_fields):
            return profile
        else:
            return None
    except json.JSONDecodeError:
        return None
```

**Botões na sidebar** (após perfil header):
```python
# Em sidebar (linha 2700)
col_export, col_import = st.columns(2)

with col_export:
    if st.button("📥 Exportar", use_container_width=True):
        profile_json = export_profile_json(st.session_state.user_profile)
        st.download_button(
            label="⬇️ Download JSON",
            data=profile_json,
            file_name=f"perfil_{st.session_state.user_profile['brand_topic']}.json",
            mime="application/json",
            use_container_width=True
        )

with col_import:
    if st.button("📤 Importar", use_container_width=True):
        show_import_profile_modal()

@st.dialog("📤 Importar Perfil")
def show_import_profile_modal():
    st.markdown("### Cole o JSON do perfil")
    
    json_input = st.text_area(
        "JSON do Perfil",
        height=300,
        placeholder='{"brand_topic": "...", "segmento": "...", ...}'
    )
    
    if st.button("✅ Importar", type="primary"):
        profile = import_profile_json(json_input)
        if profile:
            st.session_state.user_profile = profile
            st.success("Perfil importado com sucesso!")
            st.rerun()
        else:
            st.error("JSON inválido. Verifique o formato.")
```

**Compartilhamento entre usuários**:
```python
# Gerar link de compartilhamento (Base64 encoded)
def generate_share_link(profile: Dict) -> str:
    """
    Gera link de compartilhamento do perfil.
    
    Ex: https://futuruma.app?profile=eyJicmFuZF90b3BpYyI6...
    """
    profile_json = json.dumps(profile)
    profile_b64 = base64.b64encode(profile_json.encode()).decode()
    return f"https://futuruma.app?profile={profile_b64}"

# No main() do dashboard
def load_profile_from_url():
    """Carrega perfil do URL parameter"""
    query_params = st.query_params
    if 'profile' in query_params:
        try:
            profile_b64 = query_params['profile']
            profile_json = base64.b64decode(profile_b64).decode()
            profile = json.loads(profile_json)
            st.session_state.user_profile = profile
            st.success("Perfil carregado do link!")
        except:
            st.error("Link inválido")
```

**Benefícios**:
- Backup de configurações
- Replicar análise para outro usuário
- Templates pré-configurados para a equipe

---

### 5️⃣ ANÁLISE MULTI-PROJETO - Priority: 🔵 OPCIONAL

**Arquivo a criar**: `dashboard/multi_project_analysis.py` (~500 linhas)

#### Funcionalidade:

**Comparação side-by-side** de 2+ projetos:
```python
def render_multi_project_comparison(project_ids: List[str]):
    """
    Compara KPIs e sinais entre múltiplos projetos.
    
    Layout:
    ┌─────────────────────────────────────────────────────┐
    │  📊 Comparação Multi-Projeto                        │
    ├─────────────────────────────────────────────────────┤
    │  Projeto A        │  Projeto B        │  Projeto C  │
    │  Guaraná          │  Havaianas        │  Anitta     │
    │                   │                   │             │
    │  Score: 87.3      │  Score: 72.1      │  Score: 91.5│
    │  Sinais: 23       │  Sinais: 18       │  Sinais: 31 │
    │  Crescimento: +15%│  Crescimento: +8% │  Crescim: +22%│
    │                   │                   │             │
    │  Top Signal:      │  Top Signal:      │  Top Signal:│
    │  "Street Food"    │  "Chinelo Viral"  │  "Grammy"   │
    └─────────────────────────────────────────────────────┘
    
    Chart: Line chart com evolução de cada projeto (últimas 4 análises)
    """
    
    pm = st.session_state.project_manager
    
    # Coletar dados de cada projeto
    comparison_data = []
    for pid in project_ids:
        project = pm.projects[pid]
        
        # Última análise
        if project.analysis_history:
            last = project.analysis_history[-1]
            comparison_data.append({
                'id': pid,
                'brand': project.profile['brand_topic'],
                'segmento': project.profile['segmento'],
                'avg_score': last['avg_score'],
                'num_signals': len(last['weak_signals']),
                'top_signal': last['weak_signals'][0]['termo'] if last['weak_signals'] else "N/A",
                'growth': calculate_growth(project.analysis_history)
            })
    
    # Renderizar comparação
    cols = st.columns(len(comparison_data))
    for i, data in enumerate(comparison_data):
        with cols[i]:
            st.markdown(f"### {data['brand']}")
            st.metric("Score Médio", f"{data['avg_score']:.1f}")
            st.metric("Sinais Detectados", data['num_signals'])
            st.metric("Crescimento", f"+{data['growth']}%")
            st.markdown(f"**Top Signal:** {data['top_signal']}")
    
    # Chart de evolução
    st.markdown("### 📈 Evolução Comparativa")
    fig = go.Figure()
    for data in comparison_data:
        project = pm.projects[data['id']]
        history = project.analysis_history[-10:]  # Últimas 10 análises
        
        fig.add_trace(go.Scatter(
            x=[h['timestamp'] for h in history],
            y=[h['avg_score'] for h in history],
            mode='lines+markers',
            name=data['brand']
        ))
    
    st.plotly_chart(fig, use_container_width=True)
```

**UI na aba Projetos**:
```python
# Nova seção na aba Projetos
st.divider()
st.markdown("### 📊 Análise Multi-Projeto")

selected_projects = st.multiselect(
    "Selecione projetos para comparar (2-4)",
    options=[p.id for p in pm.list_projects()],
    format_func=lambda pid: f"{pm.projects[pid].profile['brand_topic']}"
)

if len(selected_projects) >= 2:
    if st.button("🔍 Comparar Projetos", type="primary"):
        render_multi_project_comparison(selected_projects)
else:
    st.info("Selecione pelo menos 2 projetos para comparar")
```

**Benefícios**:
- Portfolio view para agências
- Identificar padrões cross-projects
- Benchmarking entre clientes

---

## 📊 Impacto Esperado

| Funcionalidade | Impacto no Usuário | Complexidade | Tempo |
|----------------|-------------------|--------------|-------|
| **Comparar Segmentos** | Alto - Decisões estratégicas | Média | 1 dia |
| **Persistência Projetos** | Alto - Não perder trabalho | Alta | 1.5 dias |
| **Templates AI Keywords** | Médio - Facilita onboarding | Baixa | 0.5 dia |
| **Export/Import Perfil** | Baixo - Backup/Share | Baixa | 0.5 dia |
| **Multi-Projeto** | Médio - Portfolio view | Alta | 1 dia |

**Total estimado**: 4.5 dias (arredondado para 1 semana)

---

## 🔄 Ordem de Implementação Recomendada

### FASE 1 (1-2 dias): Core Features
1. ✅ **Comparar Segmentos** (1 dia)
   - Maior impacto para CMO
   - Usa Context Enricher já existente
   - Workflow: Modal → Re-análise → Side-by-side

2. ✅ **Persistência de Projetos** (1.5 dias)
   - Base para multi-projeto
   - JSON storage simples (sem DB)
   - UI de gerenciamento completo

### FASE 2 (0.5-1 dia): UX Enhancements
3. ✅ **Export/Import Perfil** (0.5 dia)
   - Quick win
   - Usa JSON já implementado
   - Botões + download/upload

4. ✅ **Templates AI Keywords** (0.5 dia)
   - Melhora onboarding
   - GPT-4 API (opcional)
   - Fallback para templates

### FASE 3 (1 dia): Advanced Analytics
5. ⚠️ **Multi-Projeto** (1 dia)
   - Depende de #2 (Persistência)
   - Complexo mas alto valor para agências
   - Pode ser adiado para v10

---

## 🧪 Critérios de Sucesso

**Comparar Segmentos**:
- [ ] Modal abre ao clicar botão no Signal Card
- [ ] 2 colunas side-by-side (segmento A vs B)
- [ ] Re-análise com Context Enricher funciona
- [ ] Diferenças destacadas (delta scores, narrativas únicas)
- [ ] Tempo de resposta <5s

**Persistência Projetos**:
- [ ] JSON storage funcional
- [ ] CRUD completo (Create, Read, Update, Delete)
- [ ] Switch entre projetos sem perder dados
- [ ] Histórico de análises salvo (timestamp + dados)
- [ ] Lista projetos com preview

**Export/Import**:
- [ ] Download JSON funciona
- [ ] Upload JSON valida e importa
- [ ] Link de compartilhamento (Base64) funciona

**Templates AI**:
- [ ] 13 segmentos com keywords
- [ ] Botão "Gerar com IA" funciona (se GPT-4 disponível)
- [ ] Fallback para templates offline

**Multi-Projeto**:
- [ ] Comparação 2-4 projetos
- [ ] KPIs side-by-side
- [ ] Chart de evolução temporal
- [ ] Insights cross-project

---

## 🚀 Quick Start para Implementação

### Passo 1: Criar arquivos base
```bash
# Criar estrutura
mkdir -p dashboard/components
mkdir -p dashboard/storage

touch dashboard/components/segment_comparison.py
touch dashboard/project_manager.py
touch dashboard/multi_project_analysis.py
```

### Passo 2: Implementar feature por feature
```python
# Ordem recomendada:
1. segment_comparison.py (compare_signal_across_segments)
2. project_manager.py (ProjectManager class)
3. Integrar em futuruma_dashboard.py (botões + UI)
4. Testar fluxo completo
5. Export/Import (quick win)
6. Multi-projeto (opcional)
```

### Passo 3: Testar
```bash
cd products
python futuruma_dashboard.py

# Checklist:
# ✓ Botão "Comparar Segmentos" aparece
# ✓ Modal abre e re-analisa
# ✓ Criar projeto → salva em JSON
# ✓ Switch projeto → carrega perfil
# ✓ Export/Import funciona
```

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Context Enricher lento na re-análise | Média | Alto | Cache de resultados, async loading |
| JSON storage corrompe | Baixa | Alto | Backup automático, validação de schema |
| GPT-4 API quota excedida | Média | Baixo | Fallback para templates offline |
| Multi-projeto sobrecarrega UI | Média | Médio | Limitar a 4 projetos, virtualização |

---

## 📚 Dependências

**Já implementado**:
- ✅ Context Enricher (contextual_intelligence_engine.py)
- ✅ User Profile (st.session_state.user_profile)
- ✅ Welcome Modal (onboarding_manager.py)

**A implementar**:
- ❌ ProjectManager class
- ❌ JSON storage layer
- ❌ Segment comparison logic
- ❌ Multi-project aggregation

**Bibliotecas necessárias**:
- `openai` (para AI keywords - opcional)
- Todas as outras já instaladas

---

## 🎉 Resultado Final Esperado

Após SPRINT 4, o dashboard terá:

1. **Context-aware analysis** com comparação entre segmentos
2. **Project management** completo (CRUD + histórico)
3. **Portability** (export/import perfis)
4. **AI-assisted** onboarding (keywords automáticas)
5. **Multi-project** analytics (portfolio view)

**Time-to-value total**: <5min (welcome 2min + análise 3min)  
**Personalização**: 100% (perfil + segmento + comparação)  
**Persistência**: 100% (projetos + histórico salvos)

---

## 📝 Checklist de Implementação

### SPRINT 4 - FASE 1 (Core)
- [ ] Criar `segment_comparison.py`
- [ ] Implementar `compare_signal_across_segments()`
- [ ] Adicionar botão [Comparar Segmentos] nos Signal Cards
- [ ] Testar modal side-by-side
- [ ] Criar `project_manager.py`
- [ ] Implementar `ProjectManager` class
- [ ] Criar JSON storage (`projects.json`)
- [ ] Atualizar aba Projetos com lista/CRUD
- [ ] Testar switch entre projetos

### SPRINT 4 - FASE 2 (UX)
- [ ] Adicionar `export_profile_json()`
- [ ] Adicionar `import_profile_json()`
- [ ] Botões Export/Import na sidebar
- [ ] Testar download/upload
- [ ] Expandir `KEYWORDS_TEMPLATES` (13 segmentos)
- [ ] Implementar `generate_ai_keywords()` (GPT-4)
- [ ] Botão "Gerar com IA" no welcome modal
- [ ] Testar geração automática

### SPRINT 4 - FASE 3 (Advanced)
- [ ] Criar `multi_project_analysis.py`
- [ ] Implementar `render_multi_project_comparison()`
- [ ] Seção Multi-Projeto na aba Projetos
- [ ] Chart de evolução comparativa
- [ ] Testar com 2-4 projetos

### Documentação
- [x] Criar `SPRINT4_ROADMAP.md` (este arquivo)
- [ ] Criar `SPRINT4_SUMMARY.md` (após implementação)
- [ ] Atualizar `README.md` com novas features

---

**Status**: 📋 Planejado e pronto para implementação!
