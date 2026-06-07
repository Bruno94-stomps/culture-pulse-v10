# Real Data Source Map - Culture Pulse V8

## Fontes de dados reais do projeto

### 1. YouTube
- Coletor: `YouTubeCollectorV8`
- API: YouTube Data API
- Configuração: `YOUTUBE_API_KEY`
- Uso: vídeos, estatísticas, comentários e sinais culturais de alto volume
- Status: real/produtivo quando configurado

### 2. Reddit
- Coletor: `RedditCollectorV8`
- API: Reddit API
- Configuração: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
- Uso: posts e comentários de subreddits brasileiros para detectar tendências e sentimentos
- Status: real/produtivo quando configurado

### 3. Spotify
- Coletor: `SpotifyCollectorV8`
- API: Spotify Web API
- Configuração: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`
- Uso: dados musicais, artistas, playlists e tendências de áudio cultural
- Status: real/produtivo quando configurado

### 4. NewsAPI
- Coletor: `NewsAPICollectorV8`
- API: NewsAPI
- Configuração: `NEWS_API_KEY`
- Uso: notícias culturais de fontes nacionais para sinalização de tendências e eventos
- Status: real/produtivo quando configurado

### 5. IBGE
- Coletor: `IBGECollectorV8`
- API: IBGE APIs públicas
- Configuração: sem chave obrigatória
- Uso: indicadores demográficos, dados regionais e pesquisas governamentais
- Status: real/produtivo

### 6. Google Trends
- Coletor: `GoogleTrendsCollectorV8`
- API: Google Trends (real, se disponível)
- Uso: sinais de busca e tendências de interesse ao longo do tempo
- Status: real/produtivo quando integrado

### 7. RSS Cultural
- Coletor: `RSSCollectorV8`
- Integração: `collectors.rss_cultural_collector.RSSCulturalCollector`
- Uso: fontes RSS brasileiras confiáveis (Agência Brasil, G1, Folha, etc.)
- Status: real quando o motor nativo está disponível, com fallback simulado apenas em ambiente de desenvolvimento

### 8. Persistência e contexto do projeto
- Banco de dados primário: Supabase via `collectors.supabase_writer`
- Fallback local: DuckDB via `core.models.production_database_manager` (quando disponível)
- Dados de produção: sinais culturais ingestados, contexto de `project_id`, `user_id`, histórico de projeto e metadata de onboarding
- Uso: garantir rastreabilidade e histórico de sinais reais

## Fontes de demonstração ou protótipo

### Instagram / Threads
- Coletor: `InstagramThreadsCollectorV8`
- Status: simulado por padrão quando `INSTAGRAM_ACCESS_TOKEN` não está configurado
- Uso: apenas para demonstrações, protótipos e análise de fluxo visual
- Produção: desabilitado por padrão via `ALLOW_DEMO_COLLECTION=false`

### Meetup
- Coletor: `MeetupCollectorV8`
- Status: simulado
- Uso: eventos comunitários e sinais presenciais fictícios
- Produção: desabilitado por padrão via `ALLOW_DEMO_COLLECTION=false`

## Gatekeeping de produção
- A partir desta implementação, em `ENVIRONMENT=production` o pipeline de coleta agora:
  - usa apenas `REAL_DATA_SOURCES` por padrão
  - rejeita solicitações customizadas com `instagram` ou `meetup` se `ALLOW_DEMO_COLLECTION` não estiver habilitado
  - força o endpoint `/collect/quick` a usar apenas fontes reais em produção
- Essa mudança garante que os fluxos de produção não dependam de protótipos ou mocks invisíveis.

## Recomendações de implantação
- Definir `ENVIRONMENT=production` no ambiente de produção
- Configurar todas as chaves reais necessárias (`YOUTUBE_API_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `NEWS_API_KEY`)
- Habilitar `ALLOW_DEMO_COLLECTION=true` apenas para testes ou demonstrações controladas
- Verificar o status de coletores via `/api/v8/collect/status` para confirmar fontes reais e configuração de demo
- Consultar as fontes completas via `/api/v8/collect/sources` para ver quais coletoras estão ativas e quais são demo-only
