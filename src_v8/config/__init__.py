#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Package - Culture Pulse V8.0
Pacote centralizado de configurações do sistema

🎯 EXPORTS PRINCIPAIS:
- config: Instância da configuração centralizada
- API_KEYS: Dicionário com chaves das APIs
- SYSTEM_CONFIG: Configurações do sistema
- validate_api_keys: Função de validação

🔧 USO:
    from config import config, API_KEYS, SYSTEM_CONFIG
    from config import validate_api_keys
    
🏗️ ESTRUTURA:
- centralized_config.py: Configuração principal V8.0
- settings.py: Configurações V7.0 (compatibilidade)
- config_manager.py: Gerenciador avançado
- constants.py: Constantes do sistema
"""

# Importações principais do pacote
try:
    # Configuração segura V9.0 (PRINCIPAL)
    from .secure_config import (
        SecureConfig,
        APIKeyRotation,
        APIRateLimiter,
        secure_config,
        key_rotation,
        rate_limiter,
        get_api_key,
        check_api_rate_limit,
        wait_for_api_rate_limit,
        record_api_usage,
        mark_api_exhausted
    )
    
    # Configuração V8.0 (COMPATIBILIDADE)
    from .centralized_config import (
        config,
        API_KEYS,
        SYSTEM_CONFIG,
        validate_api_keys,
        get_api_keys,
        get_system_config,
        CentralizedConfig,
        APIConfig,
        SystemConfig,
        EnvironmentConfig
    )
    
    # Flag de sucesso
    CONFIG_V9_LOADED = True
    CONFIG_V8_LOADED = True
    
except ImportError as e:
    # Fallback para configuração V7.0 se V8.0 falhar
    try:
        from .settings import (
            config_manager as config,
            API_CONFIGS as API_KEYS,
            get_api_config,
            is_api_enabled,
            get_enabled_apis
        )
        
        # Criar SYSTEM_CONFIG compatível
        SYSTEM_CONFIG = {
            'environment': 'development',
            'version': '7.0',
            'api_timeout': 15,
            'max_results': 50,
            'cache_ttl': 60,
            'debug_mode': False,
            'performance_tracking': True
        }
        
        def validate_api_keys():
            """Função de validação para compatibilidade V7.0"""
            enabled_apis = get_enabled_apis()
            status = {}
            for api in ['youtube', 'news', 'spotify', 'reddit', 'ibge', 'instagram', 'meetup']:
                if api in enabled_apis:
                    status[api.title()] = '✅ Configurada'
                else:
                    status[api.title()] = '❌ Não configurada'
            return status
        
        CONFIG_V8_LOADED = False
        
    except ImportError:
        # Configuração mínima de emergência
        import os
        
        API_KEYS = {
            'news': os.getenv('NEWS_API_KEY'),
            'youtube': os.getenv('YOUTUBE_API_KEY'),
            'spotify_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'spotify_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
            'reddit_id': os.getenv('REDDIT_CLIENT_ID'),
            'reddit_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'reddit_user_agent': os.getenv('REDDIT_USER_AGENT'),
            'meetup': os.getenv('MEETUP_API_KEY'),
            'eventbrite': os.getenv('EVENTBRITE_API_KEY'),
            'instagram': os.getenv('INSTAGRAM_TOKEN')
        }
        
        SYSTEM_CONFIG = {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'version': os.getenv('CULTURE_PULSE_VERSION', '8.0'),
            'api_timeout': int(os.getenv('API_TIMEOUT_SECONDS', '15')),
            'max_results': int(os.getenv('MAX_RESULTS_PER_API', '50')),
            'cache_ttl': int(os.getenv('CACHE_TTL_MINUTES', '60')),
            'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'performance_tracking': os.getenv('PERFORMANCE_TRACKING', 'true').lower() == 'true'
        }
        
        class EmergencyConfig:
            """Configuração mínima de emergência"""
            def __init__(self):
                self.api = type('APIConfig', (), API_KEYS)()
                self.system = type('SystemConfig', (), SYSTEM_CONFIG)()
            
            def validate_apis(self):
                status = {}
                for key, value in API_KEYS.items():
                    api_name = key.replace('_', ' ').title()
                    if value:
                        status[api_name] = '✅ Configurada'
                    else:
                        status[api_name] = '❌ Não configurada'
                return status
        
        config = EmergencyConfig()
        
        def validate_api_keys():
            return config.validate_apis()
        
        CONFIG_V8_LOADED = False

# Versão do pacote de configuração
__version__ = "8.0.0"
__author__ = "Culture Pulse Team"

# Exports públicos do pacote
__all__ = [
    # Principais V9.0 (SecureConfig)
    'SecureConfig',
    'secure_config',
    'get_api_key',
    'check_api_rate_limit',
    'wait_for_api_rate_limit',
    'record_api_usage',
    'mark_api_exhausted',
    
    # Classes V9.0
    'APIKeyRotation',
    'APIRateLimiter',
    'key_rotation',
    'rate_limiter',
    
    # Compatibilidade V8.0
    'config',
    'API_KEYS', 
    'SYSTEM_CONFIG',
    'validate_api_keys',
    
    # Funções auxiliares
    'get_api_keys',
    'get_system_config',
    
    # Classes V8.0 (se disponíveis)
    'CentralizedConfig',
    'APIConfig',
    'SystemConfig',
    'EnvironmentConfig',
    
    # Status
    'CONFIG_V9_LOADED',
    'CONFIG_V8_LOADED',
    '__version__'
]

def print_config_status():
    """Imprimir status da configuração carregada"""
    print("🔧 CULTURE PULSE - CONFIG PACKAGE")
    print("=" * 40)
    print(f"📦 Versão: {__version__}")
    print(f"⚙️ V8.0 Carregado: {CONFIG_V8_LOADED}")
    
    if hasattr(config, 'print_config_summary'):
        config.print_config_summary()
    else:
        print("📊 Configuração básica carregada")
        print(f"🔑 APIs: {len(API_KEYS)} configuradas")
        print(f"⚙️ Sistema: {len(SYSTEM_CONFIG)} parâmetros")

# Função de conveniência para debug
def debug_imports():
    """Debug das importações do pacote"""
    print("🐛 DEBUG - CONFIG IMPORTS")
    print("=" * 30)
    
    available_modules = []
    
    try:
        from . import centralized_config
        available_modules.append("✅ centralized_config")
    except ImportError as e:
        available_modules.append(f"❌ centralized_config: {e}")
    
    try:
        from . import settings
        available_modules.append("✅ settings")
    except ImportError as e:
        available_modules.append(f"❌ settings: {e}")
    
    try:
        from . import config_manager
        available_modules.append("✅ config_manager")
    except ImportError as e:
        available_modules.append(f"❌ config_manager: {e}")
    
    # constants.py depreciado na V9.9
    
    for module in available_modules:
        print(f"  {module}")
    
    return available_modules

if __name__ == "__main__":
    # Teste do pacote quando executado diretamente
    print_config_status()
    print()
    debug_imports()
