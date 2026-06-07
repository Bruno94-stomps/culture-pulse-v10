# 📋 Plano de Diagnóstico: Frontend Next.js vs API Culture Pulse V9.0

Este documento detalha os pontos críticos de integração entre o novo frontend Next.js e o ecossistema de APIs Python.

## 1. Status da Integração (Checklist)
- [ ] **CORS Settings:** Validar `api/main.py`. Origens `localhost:3000` e domínios Vercel permitidos.
- [ ] **Auth Tiering:** Garantir que o frontend envia os tokens corretos (`free`, `pro`, `enterprise`).
- [ ] **Endpoint Insights:** Validar se `/api/v8/dashboard/insights` retorna dados reais de `core/enriched_reader.py`.
- [ ] **Streaming Status:** Verificar estabilidade do WebSocket para sinais em tempo real.
- [ ] **Supabase Sync:** Confirmar que sinais coletados estão acessíveis via API para o Next.js.

## 2. Ações de Diagnóstico Automático
1. Executar testes de conectividade da API.
2. Monitorar latência de endpoints críticos (P95 < 5s).
3. Verificar logs de erro (500) nos roteadores da API.
4. Validar schemas Pydantic vs Interfaces TypeScript.

## 3. Logs de Execução (Sessão Atual)
- [Ativo] Validação de CORS em `api/main.py`.
- [Ativo] Verificação de integridade dos endpoints em `api/endpoints/dashboard_insights.py`.
- [Pendente] Teste de carga simulada para rate limiting.

## 4. Auditoria de Supabase & Cache Local (15/03/2026)
- [x] **Conexão Supabase:** Confirmada usando `SUPABASE_SERVICE_KEY`.
- [x] **Volume de Dados:** 220 sinais culturais encontrados na tabela `cultural_signals`.
- [!] **Recência dos Dados:** O sinal mais recente é de **22/02/2026**. Há um gap de ~21 dias sem novos sinais no banco.
- [ ] **Cache Local vs Real:** O frontend Next.js está recebendo listas vazias porque o `enriched_reader.py` tem filtros de data que excluem sinais antigos.
- [ ] **Ação Corretiva:** Rodar o `orchestrator_v8.py` para coletar dados de Março/2026.

---
*Gerado automaticamente pelo GitHub Copilot - 15 de Março de 2026*
