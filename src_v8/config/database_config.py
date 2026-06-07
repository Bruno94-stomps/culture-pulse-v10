"""
Database Configuration V8.0
Configurações centralizadas do banco de dados de produção
"""

# Configurações básicas de conexão
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "culture_pulse_v8",
    "user": "culture_pulse_user",
    "password": "your_secure_password_here"  # Usar variável de ambiente em produção
}

# Configurações do pool de conexões
POOL_CONFIG = {
    "min_size": 5,
    "max_size": 20,
    "max_queries": 50000,
    "max_inactive_connection_lifetime": 300.0,
    "command_timeout": 60.0,
    "server_settings": {
        "application_name": "CulturePulse V8",
        "client_min_messages": "notice"
    }
}

# Timeouts e limites
QUERY_TIMEOUT = 30.0  # segundos
TRANSACTION_TIMEOUT = 60.0  # segundos
STATEMENT_TIMEOUT = 30000  # milissegundos
IDLE_IN_TRANSACTION_TIMEOUT = 60000  # milissegundos
MAX_RETRIES = 3

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(message)s",
    "handlers": ["console", "file"]
}

# Estruturas das tabelas
TABLE_SCHEMAS = {
    "analysis_results": """
        CREATE TABLE IF NOT EXISTS analysis_results (
            analysis_id VARCHAR(50) PRIMARY KEY,
            results JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "analysis_status": """
        CREATE TABLE IF NOT EXISTS analysis_status (
            analysis_id VARCHAR(50) PRIMARY KEY,
            status VARCHAR(20) NOT NULL,
            metadata JSONB,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "error_logs": """
        CREATE TABLE IF NOT EXISTS error_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            error_type VARCHAR(100) NOT NULL,
            error_message TEXT NOT NULL,
            component VARCHAR(100),
            metadata JSONB
        )
    """
}

# Índices
INDEX_DEFINITIONS = {
    "analysis_results_created_idx": """
        CREATE INDEX IF NOT EXISTS analysis_results_created_idx 
        ON analysis_results (created_at)
    """,
    
    "analysis_status_updated_idx": """
        CREATE INDEX IF NOT EXISTS analysis_status_updated_idx 
        ON analysis_status (updated_at)
    """,
    
    "error_logs_timestamp_idx": """
        CREATE INDEX IF NOT EXISTS error_logs_timestamp_idx 
        ON error_logs (timestamp)
    """
}

# Configurações de backup
BACKUP_CONFIG = {
    "backup_path": "/backups/culture_pulse",
    "retention_days": 30,
    "compression": True,
    "schedule": {
        "full": "0 0 * * 0",  # Todo domingo à meia-noite
        "incremental": "0 0 * * 1-6"  # Segunda a sábado à meia-noite
    }
}

# Configurações de monitoramento
MONITORING_CONFIG = {
    "enable_pg_stat_statements": True,
    "log_min_duration_statement": 1000,  # ms
    "log_checkpoints": True,
    "log_connections": True,
    "log_disconnections": True,
    "log_lock_waits": True
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "work_mem": "64MB",
    "maintenance_work_mem": "256MB",
    "effective_cache_size": "4GB",
    "random_page_cost": 1.1,  # Otimizado para SSDs
    "effective_io_concurrency": 200
}

# Configurações de segurança
SECURITY_CONFIG = {
    "ssl_enabled": True,
    "ssl_cert_file": "/etc/postgresql/certs/server.crt",
    "ssl_key_file": "/etc/postgresql/certs/server.key",
    "ssl_ca_file": "/etc/postgresql/certs/ca.crt",
    "password_encryption": "scram-sha-256"
}

# Funções auxiliares
def get_connection_url():
    """Retorna URL de conexão formatada"""
    return (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

def get_pool_settings():
    """Retorna configurações do pool formatadas"""
    return {
        **POOL_CONFIG,
        "database": DB_CONFIG["database"],
        "user": DB_CONFIG["user"],
        "password": DB_CONFIG["password"],
        "host": DB_CONFIG["host"],
        "port": DB_CONFIG["port"]
    }

# Validação básica de configuração
def validate_config():
    """Valida configurações básicas do banco"""
    required_fields = ["host", "port", "database", "user", "password"]
    
    for field in required_fields:
        if field not in DB_CONFIG:
            raise ValueError(f"Campo obrigatório ausente na configuração: {field}")
            
    if not isinstance(POOL_CONFIG["min_size"], int) or POOL_CONFIG["min_size"] < 1:
        raise ValueError("min_size deve ser um inteiro positivo")
        
    if POOL_CONFIG["max_size"] < POOL_CONFIG["min_size"]:
        raise ValueError("max_size deve ser maior que min_size")
        
    return True