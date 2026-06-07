#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Unificado - Culture Pulse V9.0
Exports principais do módulo de alertas

🎯 CONSOLIDAÇÃO V9.0:
- AlertManager: Core business logic
- AlertType/AlertLevel: Tipos e níveis
- NotificationChannel: Canais de notificação
- AlertConfig: Configurações centralizadas
"""

from .alert_manager import AlertManager, get_alert_manager
from .alert_rules import AlertType, AlertLevel, Alert, AlertRule, AlertFactory, RuleFactory
from .notification_channels import NotificationChannel, NotificationConfig, NotificationManager
from .alert_config import AlertConfig, AlertThresholds, get_default_config
from .api_endpoints import alerts_router
from .cultural_alerts_engine import CulturalAlertsEngine, get_alerts_engine

__version__ = "9.9.0"
__author__ = "Culture Pulse Team"

__all__ = [
    # Core
    'AlertManager',
    'get_alert_manager',
    'CulturalAlertsEngine',
    'get_alerts_engine',
    
    # Types & Rules
    'AlertType',
    'AlertLevel', 
    'Alert',
    'AlertRule',
    'AlertFactory',
    'RuleFactory',
    
    # Notifications
    'NotificationChannel',
    'NotificationConfig',
    'NotificationManager',
    
    # Configuration
    'AlertConfig',
    'AlertThresholds',
    'get_default_config',
    
    # API
    'alerts_router',
]

# Configuração padrão do módulo
DEFAULT_CONFIG = get_default_config()

def configure_alerts(config: AlertConfig = None):
    """
    Configurar sistema de alertas globalmente
    
    Args:
        config: Configuração personalizada ou None para padrão
    """
    global DEFAULT_CONFIG
    if config:
        DEFAULT_CONFIG = config
    
    # Configurar manager global
    manager = get_alert_manager()
    manager.configure(DEFAULT_CONFIG)
    
    return manager

# ========================================
# CONVENIENCE FUNCTIONS FOR MIGRATION
# ========================================

def create_cultural_alert(alert_type: AlertType, term: str, value: float, 
                         threshold: float, level: AlertLevel = AlertLevel.WARNING) -> bool:
    """Função conveniente para criar alerta cultural"""
    alert = AlertFactory.create_cultural_alert(alert_type, term, value, threshold, level)
    return get_alert_manager().add_alert(alert)

def create_system_alert(alert_type: AlertType, component: str, message: str,
                       level: AlertLevel = AlertLevel.ERROR) -> bool:
    """Função conveniente para criar alerta de sistema"""
    alert = AlertFactory.create_system_alert(alert_type, component, message, level)
    return get_alert_manager().add_alert(alert)

def monitor_with_alerts(data: dict):
    """Função conveniente para monitoramento com alertas automáticos"""
    get_alert_manager().process_data(data)

def setup_notifications(email_enabled: bool = False, slack_webhook: str = "", 
                       webhook_urls: list = None):
    """Função conveniente para configurar notificações"""
    config = get_default_config()
    config.notifications.email_enabled = email_enabled
    config.notifications.slack_webhook_url = slack_webhook
    config.notifications.webhook_urls = webhook_urls or []
    
    configure_alerts(config)

# ========================================
# BACKWARD COMPATIBILITY ALIASES
# ========================================

# Para compatibilidade com core.alert_system
def get_alert_manager_compat():
    """Alias para compatibilidade com core.alert_system"""
    return get_alert_manager()

# Para compatibilidade com alerts.alerts
# AlertsManagerCompat = AlertsManager

# Manter nomes antigos funcionando
get_alert_manager_legacy = get_alert_manager
AlertManager_legacy = AlertManager
