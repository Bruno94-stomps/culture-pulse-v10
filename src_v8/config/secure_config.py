#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Segura de APIs - Culture Pulse V9.0
Sistema de gerenciamento seguro de chaves de API sem fallbacks hardcoded

🔐 FUNCIONALIDADES:
- Validação obrigatória de variáveis de ambiente
- Rotação automática de chaves
- Rate limiting por API
- Monitoramento de uso
- Configuração por ambiente (dev/prod)

🚀 MELHORIAS V9.0:
- Zero keys hardcoded
- Sistema de rotação inteligente
- Métricas de latência detalhadas
- Indicadores visuais de fonte
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

# Carregar variáveis do arquivo .env
try:
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Caminho explícito para .env (no diretório raiz do projeto)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(str(env_path))
        ENV_LOADED = True
    else:
        # Tentar no diretório atual (fallback)
        load_dotenv()
        ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

logger = logging.getLogger(__name__)


@dataclass
class APIKeyConfig:
    """Configuração de uma chave de API"""
    key: str
    daily_limit: int
    minute_limit: int
    calls_made_today: int = 0
    calls_made_minute: int = 0
    last_reset_time: float = 0
    is_exhausted: bool = False
    last_error_time: Optional[float] = None


class SecureConfig:
    """Configuração segura sem fallbacks hardcoded"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.api_keys = {}
        self.rate_limiters = {}
        self._load_api_keys()
        self._setup_rate_limits()
        
        logger.info(f"🔐 SecureConfig inicializado - Ambiente: {self.environment}")
    
    @staticmethod
    def get_required_env(key: str, description: str = None) -> str:
        """Obter variável de ambiente obrigatória"""
        value = os.getenv(key)
        if not value:
            error_msg = f"❌ Variável de ambiente '{key}' não configurada"
            if description:
                error_msg += f" - {description}"
            logger.error(error_msg)
            raise EnvironmentError(error_msg)
        return value
    
    @staticmethod
    def get_optional_env(key: str, description: str = None) -> str:
        """Obter variável de ambiente opcional (sem erro no log)"""
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(f"Optional env var not found: {key}")
        return value
    
    def _load_api_keys(self):
        """Carregar todas as chaves de API obrigatórias"""
        try:
            # YouTube API Keys (rotação)
            youtube_keys = []
            
            # Chave principal (obrigatória)
            main_key = self.get_required_env('YOUTUBE_API_KEY', "YouTube API Key")
            youtube_keys.append(APIKeyConfig(
                key=main_key,
                daily_limit=10000,
                minute_limit=100
            ))
            
            # Chaves adicionais (opcionais) - apenas se configuradas
            for i in range(2, 4):  # YOUTUBE_API_KEY_2, YOUTUBE_API_KEY_3
                key_name = f'YOUTUBE_API_KEY_{i}'
                try:
                    key = self.get_optional_env(key_name, f"YouTube API Key #{i}")
                    youtube_keys.append(APIKeyConfig(
                        key=key,
                        daily_limit=10000,
                        minute_limit=100
                    ))
                except EnvironmentError:
                    # Chave opcional não encontrada - tudo bem
                    break
            
            self.api_keys['youtube'] = youtube_keys
            
            # Reddit API
            self.api_keys['reddit'] = {
                'client_id': self.get_required_env('REDDIT_CLIENT_ID', "Reddit Client ID"),
                'client_secret': self.get_required_env('REDDIT_CLIENT_SECRET', "Reddit Client Secret"),
                'user_agent': os.getenv('REDDIT_USER_AGENT', 'CulturePulse V9.0')
            }
            
            # Spotify API
            self.api_keys['spotify'] = {
                'client_id': self.get_required_env('SPOTIFY_CLIENT_ID', "Spotify Client ID"),
                'client_secret': self.get_required_env('SPOTIFY_CLIENT_SECRET', "Spotify Client Secret")
            }
            
            # News API
            news_keys = []
            
            # Chave principal (obrigatória)
            main_key = self.get_required_env('NEWS_API_KEY', "News API Key")
            news_keys.append(APIKeyConfig(
                key=main_key,
                daily_limit=1000,
                minute_limit=5
            ))
            
            # Chave adicional (opcional) - apenas se configurada
            try:
                backup_key = self.get_optional_env('NEWS_API_KEY_2', "News API Key #2")
                news_keys.append(APIKeyConfig(
                    key=backup_key,
                    daily_limit=1000,
                    minute_limit=5
                ))
            except EnvironmentError:
                # Chave opcional não encontrada - tudo bem
                pass
            
            self.api_keys['news'] = news_keys
            
            # APIs opcionais (Real)
            instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
            if instagram_token:
                self.api_keys['instagram'] = {
                    'access_token': instagram_token,
                    'type': 'REAL'
                }
                logger.info("📷 Instagram API Real configurada")
            else:
                self.api_keys['instagram'] = {'type': 'OFFLINE'}
                logger.warning("📷 Instagram desativado (Token ausente)")
            
            meetup_key = os.getenv('MEETUP_API_KEY')
            if meetup_key:
                self.api_keys['meetup'] = {
                    'api_key': meetup_key,
                    'type': 'REAL'
                }
                logger.info("🤝 Meetup API Real configurada")
            else:
                self.api_keys['meetup'] = {'type': 'OFFLINE'}
                logger.warning("🤝 Meetup desativado (Chave ausente)")
            
            logger.info("✅ Todas as chaves de API carregadas com sucesso")
            
            # Propriedade para compatibilidade
            self.api_configs = self.api_keys
            
        except EnvironmentError as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            raise
    
    def _setup_rate_limits(self):
        """Configurar limitadores de taxa"""
        self.rate_limiters = {
            'youtube': {'calls_per_minute': 100, 'calls_per_day': 10000},
            'reddit': {'calls_per_minute': 60, 'calls_per_day': 1000},
            'spotify': {'calls_per_second': 1, 'calls_per_minute': 60},
            'news': {'calls_per_minute': 5, 'calls_per_day': 1000},
            'instagram': {'calls_per_hour': 200, 'calls_per_day': 4800},
            'meetup': {'calls_per_hour': 200, 'calls_per_day': 10000}
        }
        
        logger.info("⚡ Rate limiters configurados")
    
    def get_api_key(self, api_name: str, key_type: str = 'key') -> Optional[str]:
        """Obter chave de API"""
        if api_name not in self.api_keys:
            logger.warning(f"API {api_name} não configurada")
            return None
        
        api_config = self.api_keys[api_name]
        
        # Para APIs com estrutura de dicionário (como spotify)
        if isinstance(api_config, dict) and key_type in api_config:
            return api_config[key_type]
        
        # Para APIs com lista de chaves (como youtube, news)
        if isinstance(api_config, list) and api_config:
            return api_config[0].key
        
        # Para chaves simples
        if isinstance(api_config, str):
            return api_config
        
        return None
    
    def get_rate_limiter(self, api_name: str) -> Optional[Dict]:
        """Obter configuração de rate limiting"""
        return self.rate_limiters.get(api_name)


class APIKeyRotation:
    """Sistema de rotação automática de chaves"""
    
    def __init__(self, secure_config: SecureConfig):
        self.config = secure_config
        self.current_indices = {}
        self.usage_counters = {}
        self.last_rotation = {}
        
        # Inicializar índices para APIs com rotação
        for api_name in ['youtube', 'news']:
            if api_name in self.config.api_keys and isinstance(self.config.api_keys[api_name], list):
                self.current_indices[api_name] = 0
                self.usage_counters[api_name] = {}
        
        logger.info("🔄 Sistema de rotação de chaves inicializado")
    
    def get_active_key(self, api_name: str) -> Optional[str]:
        """Obter chave ativa para uma API"""
        if api_name not in self.config.api_keys:
            logger.error(f"API {api_name} não configurada")
            return None
        
        api_config = self.config.api_keys[api_name]
        
        # APIs com rotação (lista de keys)
        if isinstance(api_config, list):
            if api_name not in self.current_indices:
                self.current_indices[api_name] = 0
            
            current_index = self.current_indices[api_name]
            if current_index < len(api_config):
                key_config = api_config[current_index]
                
                # Verificar se a key não está esgotada
                if not key_config.is_exhausted:
                    return key_config.key
                else:
                    # Tentar próxima key
                    return self._rotate_to_next_key(api_name)
            
            return None
        
        # APIs simples (dict)
        elif isinstance(api_config, dict):
            if 'key' in api_config:
                return api_config['key']
            elif api_name == 'reddit':
                return api_config  # Retorna dict completo para Reddit
            elif api_name in ['spotify', 'instagram', 'meetup']:
                return api_config  # Retorna dict completo
        
        return None
    
    def _rotate_to_next_key(self, api_name: str) -> Optional[str]:
        """Rotacionar para próxima chave disponível"""
        if api_name not in self.config.api_keys:
            return None
        
        api_keys = self.config.api_keys[api_name]
        if not isinstance(api_keys, list):
            return None
        
        current_index = self.current_indices.get(api_name, 0)
        
        # Tentar todas as keys disponíveis
        for i in range(len(api_keys)):
            next_index = (current_index + i + 1) % len(api_keys)
            key_config = api_keys[next_index]
            
            if not key_config.is_exhausted:
                self.current_indices[api_name] = next_index
                self.last_rotation[api_name] = time.time()
                
                logger.info(f"🔄 Rotação {api_name}: key #{next_index + 1}")
                return key_config.key
        
        logger.error(f"❌ Todas as keys de {api_name} esgotadas")
        return None
    
    def mark_key_exhausted(self, api_name: str, error_type: str = 'rate_limit'):
        """Marcar chave atual como esgotada"""
        if api_name not in self.config.api_keys:
            return
        
        api_keys = self.config.api_keys[api_name]
        if isinstance(api_keys, list):
            current_index = self.current_indices.get(api_name, 0)
            if current_index < len(api_keys):
                api_keys[current_index].is_exhausted = True
                api_keys[current_index].last_error_time = time.time()
                
                logger.warning(f"⚠️ Key {api_name} #{current_index + 1} marcada como esgotada: {error_type}")
                
                # Tentar rotacionar
                self._rotate_to_next_key(api_name)
    
    def reset_exhausted_keys(self):
        """Resetar keys que podem ter recuperado quota"""
        current_time = time.time()
        
        for api_name, api_keys in self.config.api_keys.items():
            if isinstance(api_keys, list):
                for key_config in api_keys:
                    if key_config.is_exhausted and key_config.last_error_time:
                        # Resetar após 1 hora
                        if current_time - key_config.last_error_time > 3600:
                            key_config.is_exhausted = False
                            key_config.calls_made_today = 0
                            key_config.calls_made_minute = 0
                            logger.info(f"🔄 Key {api_name} resetada após cooldown")


class APIRateLimiter:
    """Limitador de taxa avançado por API"""
    
    def __init__(self, secure_config: SecureConfig):
        self.config = secure_config
        self.call_history = {}
        self.last_call_times = {}
        
        logger.info("⚡ Rate limiter avançado inicializado")
    
    async def check_rate_limit(self, api_name: str) -> bool:
        """Verificar se API pode ser chamada agora"""
        if api_name not in self.config.rate_limiters:
            return True  # Sem limitação configurada
        
        limits = self.config.rate_limiters[api_name]
        current_time = time.time()
        
        # Inicializar histórico se necessário
        if api_name not in self.call_history:
            self.call_history[api_name] = []
        
        # Limpar calls antigos
        self._cleanup_old_calls(api_name, current_time)
        
        # Verificar limite por segundo
        if 'calls_per_second' in limits:
            last_call = self.last_call_times.get(api_name, 0)
            if current_time - last_call < 1.0:
                return False
        
        # Verificar limite por minuto
        if 'calls_per_minute' in limits:
            minute_calls = len([
                call_time for call_time in self.call_history[api_name]
                if current_time - call_time < 60
            ])
            if minute_calls >= limits['calls_per_minute']:
                return False
        
        # Verificar limite por hora
        if 'calls_per_hour' in limits:
            hour_calls = len([
                call_time for call_time in self.call_history[api_name]
                if current_time - call_time < 3600
            ])
            if hour_calls >= limits['calls_per_hour']:
                return False
        
        # Verificar limite diário
        if 'calls_per_day' in limits:
            day_calls = len([
                call_time for call_time in self.call_history[api_name]
                if current_time - call_time < 86400
            ])
            if day_calls >= limits['calls_per_day']:
                return False
        
        return True
    
    async def wait_if_needed(self, api_name: str) -> float:
        """Aguardar se necessário e retornar tempo de espera"""
        if await self.check_rate_limit(api_name):
            return 0.0
        
        limits = self.config.rate_limiters.get(api_name, {})
        current_time = time.time()
        
        # Calcular tempo de espera baseado no limite mais restritivo
        wait_time = 0.0
        
        # Espera por limite de segundo
        if 'calls_per_second' in limits:
            last_call = self.last_call_times.get(api_name, 0)
            wait_time = max(wait_time, 1.0 - (current_time - last_call))
        
        # Espera por limite de minuto
        if 'calls_per_minute' in limits:
            minute_calls = [
                call_time for call_time in self.call_history.get(api_name, [])
                if current_time - call_time < 60
            ]
            if len(minute_calls) >= limits['calls_per_minute']:
                oldest_call = min(minute_calls)
                wait_time = max(wait_time, 60 - (current_time - oldest_call))
        
        if wait_time > 0:
            logger.info(f"⏳ Aguardando {wait_time:.1f}s para rate limit de {api_name}")
            await asyncio.sleep(wait_time)
        
        return wait_time
    
    def record_api_call(self, api_name: str):
        """Registrar chamada da API"""
        current_time = time.time()
        
        if api_name not in self.call_history:
            self.call_history[api_name] = []
        
        self.call_history[api_name].append(current_time)
        self.last_call_times[api_name] = current_time
        
        # Limitar tamanho do histórico
        if len(self.call_history[api_name]) > 1000:
            self.call_history[api_name] = self.call_history[api_name][-500:]
    
    def _cleanup_old_calls(self, api_name: str, current_time: float):
        """Limpar chamadas antigas do histórico"""
        if api_name in self.call_history:
            # Manter apenas calls das últimas 24h
            self.call_history[api_name] = [
                call_time for call_time in self.call_history[api_name]
                if current_time - call_time < 86400
            ]
    
    def get_usage_stats(self, api_name: str) -> Dict[str, Any]:
        """Obter estatísticas de uso"""
        if api_name not in self.call_history:
            return {'calls_today': 0, 'calls_hour': 0, 'calls_minute': 0}
        
        current_time = time.time()
        calls = self.call_history[api_name]
        
        return {
            'calls_today': len([c for c in calls if current_time - c < 86400]),
            'calls_hour': len([c for c in calls if current_time - c < 3600]),
            'calls_minute': len([c for c in calls if current_time - c < 60]),
            'last_call': max(calls) if calls else None
        }


# Instância global
secure_config = SecureConfig()
key_rotation = APIKeyRotation(secure_config)
rate_limiter = APIRateLimiter(secure_config)


# Funções de conveniência
def get_api_key(api_name: str):
    """Obter chave de API com rotação automática"""
    return key_rotation.get_active_key(api_name)


async def check_api_rate_limit(api_name: str) -> bool:
    """Verificar se API pode ser chamada"""
    return await rate_limiter.check_rate_limit(api_name)


async def wait_for_api_rate_limit(api_name: str) -> float:
    """Aguardar rate limit se necessário"""
    return await rate_limiter.wait_if_needed(api_name)


def record_api_usage(api_name: str):
    """Registrar uso da API"""
    rate_limiter.record_api_call(api_name)


def mark_api_exhausted(api_name: str, error_type: str = 'rate_limit', key: str = None):
    """
    Marcar API como esgotada. Se key for fornecida, marca a configuração específica.
    """
    if key and api_name in secure_config.api_keys:
        configs = secure_config.api_keys[api_name]
        if isinstance(configs, list):
            for cfg in configs:
                if cfg.key == key:
                    cfg.is_exhausted = True
                    cfg.last_error_time = time.time()
                    logger.warning(f"🚨 Chave específica de {api_name} marcada como esgotada.")
    
    key_rotation.mark_key_exhausted(api_name, error_type)


if __name__ == "__main__":
    # Teste da configuração
    try:
        print("🧪 Testando SecureConfig V9.0")
        print("=" * 50)
        
        config = SecureConfig()
        
        print(f"📊 Ambiente: {config.environment}")
        print(f"🔑 APIs configuradas: {list(config.api_keys.keys())}")
        
        # Testar rotação
        rotation = APIKeyRotation(config)
        
        for api_name in ['youtube', 'news']:
            if api_name in config.api_keys:
                key = rotation.get_active_key(api_name)
                print(f"🔄 {api_name}: {'✅ Configurado' if key else '❌ Erro'}")
        
        # Testar rate limiter
        limiter = APIRateLimiter(config)
        
        async def test_rate_limit():
            for api_name in config.rate_limiters.keys():
                can_call = await limiter.check_rate_limit(api_name)
                print(f"⚡ Rate limit {api_name}: {'✅ OK' if can_call else '❌ Limitado'}")
        
        import asyncio
        asyncio.run(test_rate_limit())
        
        print("\n✅ Configuração segura funcionando!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
