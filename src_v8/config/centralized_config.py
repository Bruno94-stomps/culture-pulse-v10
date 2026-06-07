#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized Configuration - Culture Pulse V9.9
Configuração centralizada para todo o sistema

🎯 OBJETIVO:
- Centralizar todas as configurações em um só lugar
- Facilitar manutenção e consistência
- Permitir override por variáveis de ambiente
- Suportar diferentes ambientes (dev, prod, test)
- Gerenciar Biographical Veracity e Reliability Tiers
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Carregamento de variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"

@dataclass
class EnvironmentConfig:
    """Configurações de ambiente"""
    
    # Ambiente atual
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    # Versão do sistema
    VERSION: str = os.getenv('CULTURE_PULSE_VERSION', '9.9')
    
    # Biographical Veracity Configs (V9.9)
    # ------------------------------------
    # Se True, o dashboard mostra URLs de evidência visual
    SHOW_EVIDENCE_URLS: bool = os.getenv('SHOW_EVIDENCE_URLS', 'true').lower() == 'true'
    
    # Score mínimo de fidelidade para considerar um sinal como "Alto Impacto"
    RELIABILITY_THRESHOLD_HIGH: float = 0.8
    RELIABILITY_THRESHOLD_MEDIUM: float = 0.5
    
    # Lag de dados para o plano Free (em horas)
    FREE_TIER_DATA_LAG_HOURS: int = 24
    
    # Debug mode
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # Performance tracking
    PERFORMANCE_TRACKING: bool = os.getenv('PERFORMANCE_TRACKING', 'true').lower() == 'true'
    
    # Logging level
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # Corrigindo mutable default dict com field(default_factory=...)
    RELIABILITY_LABELS: Dict[str, str] = field(default_factory=lambda: {
        "ALTA": "Fonte Oficial/API Direta - Verificado",
        "MEDIA": "Agregação de Terceiros/RSS - Confiável",
        "BAIXA": "Simulação/Estimativa - Experimental"
    })

    # Pesos de Precisão (Accuracy) baseados no Reliability
    RELIABILITY_ACCURACY_SCORES: Dict[str, float] = field(default_factory=lambda: {
        "ALTA": 0.95,
        "MEDIA": 0.70,
        "BAIXA": 0.35
    })

@dataclass
class APIConfig:
    """Configurações das APIs externas (V9.9: Via SecureConfig Proxy)"""
    
    def _get_secure_key(self, api_name: str) -> str:
        try:
            from .secure_config import get_api_key
            return get_api_key(api_name) or ""
        except ImportError:
            return os.getenv(f"{api_name.upper()}_API_KEY", "")

    @property
    def YOUTUBE_API_KEY(self) -> str:
        return self._get_secure_key('youtube')
    
    @property
    def REDDIT_CLIENT_ID(self) -> str:
        try:
            from .secure_config import secure_config
            return secure_config.get_api_key('reddit', 'client_id') or ""
        except:
            return os.getenv('REDDIT_CLIENT_ID', '')

    @property
    def REDDIT_CLIENT_SECRET(self) -> str:
        try:
            from .secure_config import secure_config
            return secure_config.get_api_key('reddit', 'client_secret') or ""
        except:
            return os.getenv('REDDIT_CLIENT_SECRET', '')

    @property
    def REDDIT_USER_AGENT(self) -> str:
        return os.getenv('REDDIT_USER_AGENT', 'CulturePulse/9.9')
    
    @property
    def SPOTIFY_CLIENT_ID(self) -> str:
        try:
            from .secure_config import secure_config
            return secure_config.get_api_key('spotify', 'client_id') or ""
        except:
            return os.getenv('SPOTIFY_CLIENT_ID', '')

    @property
    def SPOTIFY_CLIENT_SECRET(self) -> str:
        try:
            from .secure_config import secure_config
            return secure_config.get_api_key('spotify', 'client_secret') or ""
        except:
            return os.getenv('SPOTIFY_CLIENT_SECRET', '')
    
    @property
    def NEWS_API_KEY(self) -> str:
        return self._get_secure_key('news')
    
    @property
    def INSTAGRAM_TOKEN(self) -> str:
        return self._get_secure_key('instagram')
    
    @property
    def MEETUP_API_KEY(self) -> str:
        return self._get_secure_key('meetup')
    
    @property
    def EVENTBRITE_API_KEY(self) -> str:
        return self._get_secure_key('eventbrite')
    
    def to_dict(self) -> Dict[str, str]:
        """Converter para dicionário (compatibilidade com código existente)"""
        return {
            'news': self.NEWS_API_KEY,
            'youtube': self.YOUTUBE_API_KEY,
            'spotify_id': self.SPOTIFY_CLIENT_ID,
            'spotify_secret': self.SPOTIFY_CLIENT_SECRET,
            'reddit_id': self.REDDIT_CLIENT_ID,
            'reddit_secret': self.REDDIT_CLIENT_SECRET,
            'reddit_user_agent': self.REDDIT_USER_AGENT,
            'meetup': self.MEETUP_API_KEY,
            'eventbrite': self.EVENTBRITE_API_KEY,
            'instagram': self.INSTAGRAM_TOKEN
        }
    
    def validate(self) -> Dict[str, bool]:
        """Validar se as APIs estão configuradas"""
        return {
            'YouTube': bool(self.YOUTUBE_API_KEY),
            'Reddit': bool(self.REDDIT_CLIENT_ID and self.REDDIT_CLIENT_SECRET),
            'Spotify': bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET),
            'NewsAPI': bool(self.NEWS_API_KEY),
            'Instagram': bool(self.INSTAGRAM_TOKEN),
            'Meetup': bool(self.MEETUP_API_KEY),
            'Eventbrite': bool(self.EVENTBRITE_API_KEY)
        }

@dataclass
class SystemConfig:
    """Configurações do sistema"""
    
    # Timeouts
    API_TIMEOUT_SECONDS: int = int(os.getenv('API_TIMEOUT_SECONDS', '15'))
    CONNECTION_TIMEOUT: int = int(os.getenv('CONNECTION_TIMEOUT', '30'))
    
    # Limites de dados
    MAX_RESULTS_PER_API: int = int(os.getenv('MAX_RESULTS_PER_API', '50'))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    
    # Cache
    CACHE_TTL_MINUTES: int = int(os.getenv('CACHE_TTL_MINUTES', '60'))
    ENABLE_CACHE: bool = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///culture_pulse.db')
    DATABASE_POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', '10'))
    
    # Performance
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '100'))
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', '5'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário (compatibilidade com código existente)"""
        return {
            'api_timeout': self.API_TIMEOUT_SECONDS,
            'max_results': self.MAX_RESULTS_PER_API,
            'cache_ttl': self.CACHE_TTL_MINUTES,
            'max_workers': self.MAX_WORKERS,
            'batch_size': self.BATCH_SIZE,
            'enable_cache': self.ENABLE_CACHE
        }

class CentralizedConfig:
    """Classe principal de configuração centralizada"""
    
    def __init__(self):
        self.env = EnvironmentConfig()
        self.api = APIConfig()
        self.system = SystemConfig()
        
        # Cache interno para compatibilidade com código existente
        self._config_dict = None
    
    def __getitem__(self, key):
        """Tornar o objeto subscriptable para compatibilidade"""
        config_dict = self.get_system_config_dict()
        if key in config_dict:
            return config_dict[key]
        raise KeyError(f"Key '{key}' not found in config")
    
    def __setitem__(self, key, value):
        """Permitir definir valores (para compatibilidade)"""
        # Para manter retrocompatibilidade, permitir algumas operações
        if hasattr(self.system, key.upper()):
            setattr(self.system, key.upper(), value)
        elif hasattr(self.env, key.upper()):
            setattr(self.env, key.upper(), value)
    
    def __contains__(self, key):
        """Verificar se chave existe"""
        config_dict = self.get_system_config_dict()
        return key in config_dict
    
    def get(self, key, default=None):
        """Método get para compatibilidade com dicionários"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def keys(self):
        """Retornar chaves disponíveis"""
        return self.get_system_config_dict().keys()
    
    def values(self):
        """Retornar valores disponíveis"""
        return self.get_system_config_dict().values()
    
    def items(self):
        """Retornar items como dicionário"""
        return self.get_system_config_dict().items()
    
    @property
    def is_production(self) -> bool:
        """Verificar se está em produção"""
        return self.env.ENVIRONMENT.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Verificar se está em desenvolvimento"""
        return self.env.ENVIRONMENT.lower() == 'development'
    
    def get_api_keys_dict(self) -> Dict[str, str]:
        """Obter API keys como dicionário (compatibilidade)"""
        return self.api.to_dict()
    
    def get_system_config_dict(self) -> Dict[str, Any]:
        """Obter configurações do sistema como dicionário"""
        config = self.system.to_dict()
        config.update({
            'environment': self.env.ENVIRONMENT,
            'version': self.env.VERSION,
            'debug_mode': self.env.DEBUG_MODE,
            'performance_tracking': self.env.PERFORMANCE_TRACKING
        })
        return config
    
    def validate_apis(self) -> Dict[str, str]:
        """Validar status das APIs"""
        validation = self.api.validate()
        status = {}
        
        for api, is_configured in validation.items():
            if is_configured:
                status[api] = '✅ Configurada'
            else:
                # APIs públicas sempre funcionam
                if api in ['IBGE', 'Google Trends']:
                    status[api] = '✅ Pública'
                # APIs opcionais
                elif api in ['Meetup', 'Instagram', 'Eventbrite']:
                    status[api] = '⚪ Opcional'
                else:
                    status[api] = '❌ Não configurada'
        
        # Adicionar APIs públicas
        status['IBGE'] = '✅ Pública'
        status['Google Trends'] = '✅ Pública'
        
        return status
    
    def print_config_summary(self):
        """Imprimir resumo das configurações"""
        print("🔧 CULTURE PULSE V8.0 - CONFIGURAÇÕES")
        print("=" * 50)
        print(f"📍 Ambiente: {self.env.ENVIRONMENT}")
        print(f"🔢 Versão: {self.env.VERSION}")
        print(f"🐛 Debug: {self.env.DEBUG_MODE}")
        print(f"📊 Performance Tracking: {self.env.PERFORMANCE_TRACKING}")
        print(f"⚙️ Environment Loaded: {ENV_LOADED}")
        print()
        
        print("🔌 APIs Configuradas:")
        for api, status in self.validate_apis().items():
            print(f"  {api}: {status}")
        print()
        
        print("⚙️ Configurações do Sistema:")
        print(f"  Timeout: {self.system.API_TIMEOUT_SECONDS}s")
        print(f"  Max Results: {self.system.MAX_RESULTS_PER_API}")
        print(f"  Cache TTL: {self.system.CACHE_TTL_MINUTES}min")
        print(f"  Workers: {self.system.MAX_WORKERS}")
        print("=" * 50)

# Instância global da configuração
config = CentralizedConfig()

# Funções de conveniência para compatibilidade com código existente
def get_api_keys() -> Dict[str, str]:
    """Obter API keys (compatibilidade)"""
    return config.get_api_keys_dict()

def get_system_config() -> Dict[str, Any]:
    """Obter configurações do sistema (compatibilidade)"""
    return config.get_system_config_dict()

def validate_api_keys() -> Dict[str, str]:
    """Validar APIs (compatibilidade)"""
    return config.validate_apis()


def get_supabase_client():
    """
    Retorna um cliente Supabase inicializado com as credenciais do .env.
    Retorna None se as credenciais não estiverem disponíveis.
    """
    try:
        import os
        url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
        key = (
            os.getenv("SUPABASE_SERVICE_KEY")
            or os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        )
        if not url or not key:
            return None
        from supabase import create_client
        return create_client(url, key)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Supabase client init failed: {e}")
        return None


# Exportar as configurações mais usadas como variáveis
API_KEYS = config.get_api_keys_dict()
SYSTEM_CONFIG = config.get_system_config_dict()

if __name__ == "__main__":
    # Teste das configurações
    config.print_config_summary()
