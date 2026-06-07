#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do Sistema de Alertas - Culture Pulse V9.0
Configurações centralizadas para todo o sistema de alertas

🎯 FUNCIONALIDADES:
- Configurações de thresholds
- Configurações de notificações
- Configurações de canais
- Environment variables
- Configurações de produção/desenvolvimento
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class Environment(Enum):
    """Ambientes de execução"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class NotificationConfig:
    """Configurações de notificação"""
    enabled: bool = True
    email_enabled: bool = False
    slack_enabled: bool = False
    webhook_enabled: bool = False
    dashboard_enabled: bool = True  # Adicionado campo ausente
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""  # Adicionado campo ausente
    default_recipients: List[str] = field(default_factory=list)
    
    # Slack settings
    slack_webhook_url: str = ""
    slack_channel: str = "#alerts"
    slack_username: str = "Culture Pulse Bot"
    
    # Webhook settings
    webhook_urls: List[str] = field(default_factory=list)
    webhook_timeout: int = 30
    
    def __post_init__(self):
        """Carregar configurações do ambiente"""
        self.smtp_username = os.getenv('ALERT_SMTP_USERNAME', self.smtp_username)
        self.smtp_password = os.getenv('ALERT_SMTP_PASSWORD', self.smtp_password)
        self.slack_webhook_url = os.getenv('ALERT_SLACK_WEBHOOK', self.slack_webhook_url)
        
        # Habilitar baseado em configurações disponíveis
        self.email_enabled = bool(self.smtp_username and self.smtp_password)
        self.slack_enabled = bool(self.slack_webhook_url)

@dataclass
class AlertThresholds:
    """Thresholds padrão para alertas"""
    high_momentum: float = 80.0
    low_momentum: float = 20.0
    positive_sentiment: float = 0.7
    negative_sentiment: float = -0.5
    volume_spike: int = 100
    volume_drop: int = 10
    consensus_high: float = 75.0
    consensus_low: float = 30.0
    
    # Thresholds de sistema
    api_response_time: float = 2.0  # segundos
    memory_usage: float = 0.8  # 80%
    cpu_usage: float = 0.9  # 90%
    error_rate: float = 0.05  # 5%
    
    def get_threshold(self, alert_type: str) -> float:
        """Obter threshold para tipo específico"""
        return getattr(self, alert_type, 0.0)
    
    def set_threshold(self, alert_type: str, value: float):
        """Definir threshold para tipo específico"""
        if hasattr(self, alert_type):
            setattr(self, alert_type, value)

@dataclass
class CacheConfig:
    """Configurações de cache"""
    enabled: bool = True
    redis_enabled: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 2
    redis_password: Optional[str] = None
    local_cache_size: int = 1000
    alert_cache_ttl: int = 3600
    statistics_cache_ttl: int = 1800

@dataclass
class APIConfig:
    """Configurações da API"""
    enabled: bool = True
    prefix: str = "/api/v1/alerts"
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = True
    requests_per_minute: int = 60
    websocket_enabled: bool = True

@dataclass
class StorageConfig:
    """Configurações de armazenamento"""
    file_storage_enabled: bool = True
    storage_directory: str = "data/alerts"
    max_file_size_mb: int = 100
    rotate_daily: bool = True
    keep_days: int = 30

@dataclass
class AlertConfig:
    """Configuração principal do sistema de alertas"""
    
    # Ambiente
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: str = "INFO"
    
    # Configurações gerais
    enabled: bool = True
    max_alerts_per_minute: int = 10
    alert_history_limit: int = 1000
    alert_cooldown_seconds: int = 60
    
    # Processamento
    async_processing: bool = True
    batch_size: int = 100
    worker_threads: int = 4
    queue_max_size: int = 1000
    
    # Thresholds
    thresholds: AlertThresholds = field(default_factory=AlertThresholds)
    
    # Notificações
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    
    # Cache
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # API
    api: APIConfig = field(default_factory=APIConfig)
    
    # Storage
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Recursos avançados
    enable_metrics: bool = True
    enable_ml_predictions: bool = False
    enable_trend_analysis: bool = True
    enable_anomaly_detection: bool = True
    
    # Tipos de alerta habilitados
    enabled_alert_types: List[str] = field(default_factory=lambda: [
        'high_momentum',
        'negative_sentiment',
        'volume_spike',
        'api_health',
        'system_performance'
    ])
    
    # Níveis de alerta habilitados
    enabled_alert_levels: List[str] = field(default_factory=lambda: [
        'info',
        'warning',
        'error',
        'critical'
    ])
    
    def validate(self) -> List[str]:
        """Validar configuração e retornar lista de erros"""
        errors = []
        
        # Validar notificações
        if self.notifications.email_enabled:
            if not self.notifications.smtp_username:
                errors.append("SMTP username required for email notifications")
            if not self.notifications.email_from:
                errors.append("Email from address required")
            if not self.notifications.default_recipients:
                errors.append("Email recipients required")
        
        if self.notifications.slack_enabled:
            if not self.notifications.slack_webhook_url:
                errors.append("Slack webhook URL required")
        
        # Validar cache
        if self.cache.redis_enabled:
            if not self.cache.redis_host:
                errors.append("Redis host required")
        
        # Validar limites
        if self.max_alerts_per_minute <= 0:
            errors.append("Max alerts per minute must be positive")
        
        return errors

    def __post_init__(self):
        """Configuração pós-inicialização"""
        # Detectar ambiente
        env_name = os.getenv('ENVIRONMENT', 'development').lower()
        self.environment = Environment(env_name)
        
        # Configurações baseadas no ambiente
        if self.environment == Environment.PRODUCTION:
            self.debug = False
            self.max_alerts_per_minute = 20
            self.alert_cooldown_seconds = 30
        elif self.environment == Environment.STAGING:
            self.debug = True
            self.max_alerts_per_minute = 15
        
        # Override com variáveis de ambiente
        self.enabled = os.getenv('ALERTS_ENABLED', 'true').lower() == 'true'
        self.max_alerts_per_minute = int(os.getenv('ALERTS_MAX_PER_MINUTE', str(self.max_alerts_per_minute)))
    
    def is_alert_type_enabled(self, alert_type: str) -> bool:
        """Verificar se tipo de alerta está habilitado"""
        return alert_type in self.enabled_alert_types
    
    def is_alert_level_enabled(self, alert_level: str) -> bool:
        """Verificar se nível de alerta está habilitado"""
        return alert_level in self.enabled_alert_levels
    
    def get_threshold(self, alert_type: str) -> float:
        """Obter threshold para tipo de alerta"""
        return self.thresholds.get_threshold(alert_type)
    
    def set_threshold(self, alert_type: str, value: float):
        """Definir threshold para tipo de alerta"""
        self.thresholds.set_threshold(alert_type, value)

# Configurações específicas por ambiente
ENVIRONMENT_CONFIGS = {
    Environment.DEVELOPMENT: {
        'debug': True,
        'max_alerts_per_minute': 5,
        'alert_cooldown_seconds': 10,
        'enabled_alert_types': [
            'high_momentum',
            'negative_sentiment',
            'volume_spike'
        ]
    },
    
    Environment.STAGING: {
        'debug': True,
        'max_alerts_per_minute': 15,
        'alert_cooldown_seconds': 30,
        'enabled_alert_types': [
            'high_momentum',
            'negative_sentiment',
            'volume_spike',
            'api_health'
        ]
    },
    
    Environment.PRODUCTION: {
        'debug': False,
        'max_alerts_per_minute': 20,
        'alert_cooldown_seconds': 60,
        'enabled_alert_types': [
            'high_momentum',
            'negative_sentiment',
            'volume_spike',
            'api_health',
            'system_performance',
            'data_anomaly'
        ]
    }
}

def get_default_config(environment: Environment = None) -> AlertConfig:
    """
    Obter configuração padrão para ambiente específico
    
    Args:
        environment: Ambiente alvo ou None para auto-detectar
    
    Returns:
        AlertConfig configurado para o ambiente
    """
    if environment is None:
        env_name = os.getenv('ENVIRONMENT', 'development').lower()
        environment = Environment(env_name)
    
    # Configuração base
    config = AlertConfig()
    config.environment = environment
    
    # Aplicar configurações específicas do ambiente
    env_config = ENVIRONMENT_CONFIGS.get(environment, {})
    for key, value in env_config.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config

def load_config_from_file(file_path: str) -> AlertConfig:
    """
    Carregar configuração de arquivo JSON
    
    Args:
        file_path: Caminho para arquivo de configuração
    
    Returns:
        AlertConfig carregado do arquivo
    """
    import json
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Converter para AlertConfig
        config = AlertConfig()
        
        # Aplicar configurações do arquivo
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
        
    except Exception as e:
        print(f"Erro ao carregar configuração de {file_path}: {e}")
        return get_default_config()

# Configuração global padrão
DEFAULT_ALERT_CONFIG = get_default_config()
