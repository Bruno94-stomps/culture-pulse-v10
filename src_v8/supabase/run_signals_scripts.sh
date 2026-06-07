#!/bin/zsh
# Script de conveniência para executar os scripts de verificação e seed no banco Supabase via Transaction Pooler.
# Uso: definir as variáveis abaixo e rodar este script. Por padrão, o pooler do projeto já está configurado.

# Configurações padrão do pooler
SUPABASE_POOLER_HOST=${SUPABASE_POOLER_HOST:-aws-1-us-east-1.pooler.supabase.com}
SUPABASE_POOLER_PORT=${SUPABASE_POOLER_PORT:-6543}
SUPABASE_DB=${SUPABASE_DB:-postgres}
SUPABASE_USER=${SUPABASE_USER:-postgres.wsizqmnnicpgblopmxyv}

if [[ -z "$SUPABASE_PWD" ]]; then
  echo "Erro: defina SUPABASE_PWD com o Service Role Key antes de rodar."
  exit 1
fi

PSQL_BIN=${PSQL_BIN:-/opt/homebrew/opt/libpq/bin/psql}

CONN_STRING="postgresql://${SUPABASE_USER}:${SUPABASE_PWD}@${SUPABASE_POOLER_HOST}:${SUPABASE_POOLER_PORT}/${SUPABASE_DB}"

echo "Executando verificação..."
"$PSQL_BIN" "$CONN_STRING" -f supabase/scripts/verify_signals.sql

echo "Inserindo dados de teste..."
"$PSQL_BIN" "$CONN_STRING" -f supabase/scripts/seed_signals.sql