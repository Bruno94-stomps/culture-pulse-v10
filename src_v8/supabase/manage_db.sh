#!/bin/zsh
# ============================================================
# manage_db.sh — Execução de SQL via Supabase Management API
# ============================================================
# Pré-requisitos:
#   export SUPABASE_ACCESS_TOKEN="sbp_..."   # de https://supabase.com/dashboard/account/tokens
#   export PROJECT_REF="wsizqmnnicpgblopmxyv" # já configurado abaixo como padrão
# Uso:
#   ./supabase/manage_db.sh verify   → roda verify_signals.sql
#   ./supabase/manage_db.sh seed     → roda seed_signals.sql
#   ./supabase/manage_db.sh query "SELECT COUNT(*) FROM cultural_signals"
# ============================================================

PROJECT_REF="${PROJECT_REF:-wsizqmnnicpgblopmxyv}"
API_URL="https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query"

if [[ -z "$SUPABASE_ACCESS_TOKEN" ]]; then
  echo "❌ Erro: defina SUPABASE_ACCESS_TOKEN antes de rodar."
  echo "   Gere em: https://supabase.com/dashboard/account/tokens"
  exit 1
fi

run_sql() {
  local sql="$1"
  local label="${2:-query}"
  echo "▶ Executando: $label"
  local response
  response=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg q "$sql" '{"query": $q}')")
  
  # Verifica se houve erro
  if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
    echo "❌ Erro na query:"
    echo "$response" | jq '.error'
  else
    echo "✅ Resultado:"
    echo "$response" | jq '.'
  fi
  echo ""
}

run_sql_file() {
  local file="$1"
  local label="$2"
  if [[ ! -f "$file" ]]; then
    echo "❌ Arquivo não encontrado: $file"
    exit 1
  fi
  # Lê o arquivo e divide por ; para executar statement por statement
  local sql
  sql=$(cat "$file")
  run_sql "$sql" "$label"
}

# ---- Comandos disponíveis ----
case "${1:-help}" in
  verify)
    run_sql_file "supabase/scripts/verify_signals.sql" "verify_signals.sql"
    ;;
  seed)
    run_sql_file "supabase/scripts/seed_signals.sql" "seed_signals.sql"
    ;;
  query)
    if [[ -z "$2" ]]; then
      echo "❌ Forneça a query como segundo argumento."
      exit 1
    fi
    run_sql "$2" "inline query"
    ;;
  network-get)
    echo "▶ Consultando restrições de rede..."
    curl -s -X GET "https://api.supabase.com/v1/projects/${PROJECT_REF}/network-restrictions" \
      -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" | jq '.'
    ;;
  network-set)
    echo "▶ Abrindo rede para IPs públicos (0.0.0.0/0)..."
    curl -s -X POST "https://api.supabase.com/v1/projects/${PROJECT_REF}/network-restrictions/apply" \
      -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"db_allowed_cidrs": ["0.0.0.0/0"]}' | jq '.'
    ;;
  help|*)
    echo "Uso: ./supabase/manage_db.sh <comando>"
    echo ""
    echo "Comandos:"
    echo "  verify        → executa supabase/scripts/verify_signals.sql"
    echo "  seed          → executa supabase/scripts/seed_signals.sql"
    echo "  query <sql>   → executa SQL inline"
    echo "  network-get   → consulta restrições de rede atuais"
    echo "  network-set   → abre rede para 0.0.0.0/0 (todos os IPs)"
    ;;
esac
