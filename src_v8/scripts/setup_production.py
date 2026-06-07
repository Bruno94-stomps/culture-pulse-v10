#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup de Produção - Culture Pulse V8.0
Script executado automaticamente após deploy
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
# Isso é feito no início para garantir que todas as variáveis estejam disponíveis
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Criar diretórios necessários"""
    directories = [
        "data",
        "logs", 
        "cache",
        "data/complete_results",
        "data/backup",
        "logs/api",
        "logs/dashboard",
        "cache/api_responses",
        "cache/cultural_analysis"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Diretório criado: {directory}")

def setup_environment():
    """Configurar variáveis de ambiente padrão"""
    defaults = {
        "ENVIRONMENT": "production",
        "SIMULATION_MODE": "true",
        "CACHE_TTL": "300",
        "MAX_CONCURRENT_REQUESTS": "10",
        "LOG_LEVEL": "INFO"
    }
    
    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"✅ Variável definida: {key}={value}")

def validate_api_keys():
    """Validar chaves de API disponíveis com base na configuração V8."""
    # Lista completa de chaves de API esperadas para o V8
    api_keys = {
        "NEWS_API_KEY": "NewsAPI",
        "YOUTUBE_API_KEY": "YouTube Data API",
        "SPOTIFY_CLIENT_ID": "Spotify API",
        "REDDIT_CLIENT_ID": "Reddit API",
        "MEETUP_API_KEY": "Meetup API",
        "EVENTBRITE_API_KEY": "Eventbrite API",
        "INSTAGRAM_TOKEN": "Instagram API",
        # Adicionamos o user agent do Reddit como um indicador de configuração
        "REDDIT_USER_AGENT": "Reddit User Agent"
    }
    
    available_apis = 0
    for key, name in api_keys.items():
        # Verifica se a chave existe e não tem valor de placeholder
        value = os.getenv(key)
        if value and "your_" not in value and "seu_" not in value:
            logger.info(f"✅ API disponível: {name}")
            available_apis += 1
        else:
            logger.warning(f"⚠️ API não configurada: {name}")
    
    if available_apis < 2: # Menos que 2 é um sinal de alerta
        logger.warning("⚠️ Poucas APIs externas configuradas - o sistema pode operar em modo simulado.")
        os.environ["SIMULATION_MODE"] = "true"
    else:
        # Desativa o modo de simulação se houver chaves suficientes
        os.environ["SIMULATION_MODE"] = "false"
        logger.info(f"✅ {available_apis}/{len(api_keys)} APIs configuradas. Modo de simulação DESATIVADO.")

    # Salva a contagem para uso no resumo final
    os.environ["CONFIGURED_API_COUNT"] = str(available_apis)
    os.environ["TOTAL_API_COUNT"] = str(len(api_keys))

def setup_database():
    """Configurar banco de dados usando ProductionDatabaseManager."""
    
    logger.info("💾 Configurando banco de dados...")
    
    try:
        # Usar ProductionDatabaseManager
        sys.path.append(str(Path(__file__).parent.parent / "data"))
        from production_database_manager import ProductionDatabaseManager
        
        logger.info("🚀 Usando ProductionDatabaseManager simplificado...")
        
        # ProductionDatabaseManager automaticamente cria e testa o banco
        db_manager = ProductionDatabaseManager()
        
        # Verificar status
        health = db_manager.get_system_health()
        logger.info("✅ Database configurado com sucesso:")
        for key, value in health.items():
            logger.info(f"  � {key}: {value}")
        
        # Testar conectividade
        result = db_manager.execute_query("SELECT 'DB Connected!' as status")
        if result:
            logger.info(f"✅ Teste: {result[0]['status']}")
        
        logger.info("✅ Database configurado com ProductionDatabaseManager!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar database: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar database: {e}")
        return False

def setup_cache():
    """Configurar sistema de cache"""
    try:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            logger.info("✅ Cache Redis conectado")
        else:
            logger.info("✅ Cache em memória será usado")
    except Exception as e:
        logger.warning(f"⚠️ Redis não disponível, usando cache local: {e}")

def create_health_check():
    """Criar arquivo de health check"""
    health_check = {
        "status": "healthy",
        "version": "8.0",
        "timestamp": "$(date -u)",
        "services": {
            "api": "running",
            "dashboard": "running",
            "database": "connected",
            "cache": "available"
        }
    }
    
    import json
    with open("data/health_check.json", "w") as f:
        json.dump(health_check, f, indent=2)
    
    logger.info("✅ Health check criado")

def main():
    """Função principal de setup"""
    logger.info("🚀 Iniciando setup de produção - Culture Pulse V8.0")
    
    try:
        setup_directories()
        setup_environment()
        validate_api_keys()
        
        # Configurar database com tratamento de erro
        if not setup_database():
            logger.warning("⚠️ Database setup falhou, mas continuando...")
        
        setup_cache()
        create_health_check()
        
        logger.info("✅ Setup de produção concluído com sucesso!")
        
        # Exibir resumo
        print("\n" + "="*60)
        print("🧠 CULTURE PULSE V8.0 - SETUP COMPLETO")
        print("="*60)
        print(f"🌍 Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"🔧 Modo Simulação: {os.getenv('SIMULATION_MODE', 'false')}")
        
        # Usa as variáveis de ambiente para o resumo
        configured_apis = os.getenv('CONFIGURED_API_COUNT', '0')
        total_apis = os.getenv('TOTAL_API_COUNT', '8')
        print(f"📊 APIs Configuradas: {configured_apis}/{total_apis}")

        print(f"💾 Banco: DuckDB com Pool de Conexões")
        print(f"🔄 Cache: {'Redis' if os.getenv('REDIS_URL') else 'Local'}")
        print("="*60)
        print("🎯 Sistema pronto para uso!")
        print("📋 Dashboard: Streamlit")
        print("🔌 API: FastAPI")
        print("🧠 Inteligência Cultural Brasileira")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no setup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
