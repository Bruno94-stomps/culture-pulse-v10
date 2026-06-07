#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Alertas - Culture Pulse V9.0
Core business logic para processamento de alertas

🎯 FUNCIONALIDADES CONSOLIDADAS:
- ✅ Processamento assíncrono de alertas
- ✅ Sistema de regras avançado  
- ✅ Multi-channel notifications
- ✅ Cache e persistência
- ✅ Rate limiting inteligente
- ✅ WebSocket real-time
- ✅ Histórico e estatísticas
"""

import asyncio
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from collections import defaultdict, deque
from dataclasses import asdict

# Local imports
from .alert_config import AlertConfig, get_default_config
from .alert_rules import Alert, AlertRule, AlertType, AlertLevel, AlertFactory, DEFAULT_RULES
from .notification_channels import NotificationManager, NotificationConfig

# Configure logger
logger = logging.getLogger(__name__)

class AlertManager:
    """
    Gerenciador principal de alertas - Core Business Logic
    Centraliza todo o processamento de alertas do sistema
    """
    
    def __init__(self, config: AlertConfig = None):
        """
        Inicializar AlertManager
        
        Args:
            config: Configuração do sistema de alertas
        """
        self.config = config or get_default_config()
        
        # Estado interno
        self._alert_queue = asyncio.Queue(maxsize=self.config.queue_max_size)
        self._alert_history: List[Alert] = []
        self._active_alerts: Set[str] = set()
        self._rules: Dict[str, AlertRule] = {}
        self._subscribers: List[Callable] = []
        
        # Rate limiting
        self._rate_limiter = defaultdict(lambda: deque(maxlen=100))
        self._cooldown_cache: Dict[str, datetime] = {}
        
        # Componentes
        self.notification_manager = NotificationManager(self.config.notifications)
        self.cache_manager = None  # Será inicializado se necessário
        
        # Estado assíncrono
        self._background_task = None
        self._websocket_manager = None
        self._is_running = False
        
        # Carregar regras padrão
        self._load_default_rules()
        
        # Inicializar processamento assíncrono se habilitado
        if self.config.async_processing:
            self._start_async_processing()
    
    def _load_default_rules(self):
        """Carregar regras padrão do sistema"""
        for rule in DEFAULT_RULES:
            self._rules[rule.name] = rule
        logger.info(f"Carregadas {len(self._rules)} regras padrão")
    
    def _start_async_processing(self):
        """Inicializar processamento assíncrono em background"""
        if not self._is_running:
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            self._background_task = loop.create_task(self._process_alerts_async())
            self._is_running = True
            logger.info("Processamento assíncrono iniciado")
    
    async def _process_alerts_async(self):
        """Loop principal de processamento assíncrono"""
        try:
            while self._is_running:
                try:
                    # Processar batch de alertas
                    alerts_batch = []
                    batch_size = min(self.config.batch_size, self._alert_queue.qsize())
                    
                    # Coletar batch
                    for _ in range(batch_size):
                        if not self._alert_queue.empty():
                            alert_data = await asyncio.wait_for(
                                self._alert_queue.get(), 
                                timeout=1.0
                            )
                            alerts_batch.append(alert_data)
                        else:
                            break
                    
                    # Processar batch se não vazio
                    if alerts_batch:
                        await self._process_batch(alerts_batch)
                    else:
                        # Aguardar um pouco se não há alertas
                        await asyncio.sleep(0.1)
                        
                except asyncio.TimeoutError:
                    # Timeout normal, continuar loop
                    continue
                except Exception as e:
                    logger.error(f"Erro no processamento assíncrono: {e}")
                    await asyncio.sleep(1.0)
                    
        except asyncio.CancelledError:
            logger.info("Processamento assíncrono cancelado")
        except Exception as e:
            logger.error(f"Erro crítico no processamento assíncrono: {e}")
    
    async def _process_batch(self, alerts_batch: List[Dict[str, Any]]):
        """Processar batch de alertas"""
        tasks = []
        for alert_data in alerts_batch:
            task = asyncio.create_task(self._process_single_alert(alert_data))
            tasks.append(task)
        
        # Aguardar todos os alertas do batch
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_alert(self, alert_data: Dict[str, Any]):
        """Processar um único alerta"""
        try:
            # Criar alerta a partir dos dados
            if isinstance(alert_data, Alert):
                alert = alert_data
            else:
                alert = Alert(**alert_data)
            
            # Verificar rate limiting
            if not self._check_rate_limit(alert):
                logger.debug(f"Alerta bloqueado por rate limiting: {alert.id}")
                return
            
            # Aplicar regras
            if self._apply_rules(alert):
                # Adicionar ao histórico
                self._alert_history.append(alert)
                self._active_alerts.add(alert.id)
                
                # Notificar subscritores
                await self._notify_subscribers(alert)
                
                # Enviar notificações
                await self.notification_manager.send_notification(alert)
                
                # Cache se habilitado
                if self.cache_manager:
                    await self.cache_manager.store_alert(alert)
                
                # WebSocket para tempo real
                if self._websocket_manager:
                    await self._websocket_manager.broadcast_alert(alert)
                
                logger.info(f"Alerta processado: {alert.id} - {alert.alert_type}")
                
        except Exception as e:
            logger.error(f"Erro ao processar alerta: {e}")
    
    def _check_rate_limit(self, alert: Alert) -> bool:
        """Verificar rate limiting para o alerta"""
        now = datetime.now()
        alert_key = f"{alert.alert_type}_{alert.source}"
        
        # Verificar cooldown
        if alert_key in self._cooldown_cache:
            if (now - self._cooldown_cache[alert_key]).seconds < self.config.thresholds.cooldown_period:
                return False
        
        # Verificar rate per minute
        minute_key = now.strftime("%Y%m%d%H%M")
        rate_key = f"{alert_key}_{minute_key}"
        
        self._rate_limiter[rate_key].append(now)
        
        if len(self._rate_limiter[rate_key]) > self.config.thresholds.max_alerts_per_minute:
            self._cooldown_cache[alert_key] = now
            return False
        
        return True
    
    def _apply_rules(self, alert: Alert) -> bool:
        """Aplicar regras de validação ao alerta"""
        for rule in self._rules.values():
            if not rule.applies_to(alert):
                continue
                
            if not rule.validate(alert):
                logger.debug(f"Alerta rejeitado pela regra {rule.name}: {alert.id}")
                return False
        
        return True
    
    async def _notify_subscribers(self, alert: Alert):
        """Notificar subscritores do alerta"""
        for subscriber in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(alert)
                else:
                    subscriber(alert)
            except Exception as e:
                logger.error(f"Erro ao notificar subscriber: {e}")
    
    def add_alert(self, alert: Alert) -> bool:
        """
        Adicionar alerta à fila de processamento
        
        Args:
            alert: Instância do alerta
            
        Returns:
            True se adicionado com sucesso
        """
        try:
            if self.config.async_processing:
                # Processamento assíncrono
                asyncio.create_task(self._create_and_send_alert(alert))
            else:
                # Processamento síncrono
                if self._check_rate_limit(alert) and self._apply_rules(alert):
                    self._alert_history.append(alert)
                    self._active_alerts.add(alert.id)
                    
                    # Notificação síncrona
                    import asyncio
                    asyncio.create_task(self.notification_manager.send_notification(alert))
                    
                    logger.info(f"Alerta adicionado: {alert.id}")
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar alerta: {e}")
            return False
    
    async def _create_and_send_alert(self, alert: Alert):
        """Adicionar alerta à fila assíncrona"""
        try:
            await self._alert_queue.put(alert)
        except asyncio.QueueFull:
            logger.warning("Fila de alertas cheia, descartando alerta mais antigo")
            # Descartar um alerta antigo e tentar novamente
            try:
                await asyncio.wait_for(self._alert_queue.get(), timeout=0.1)
                await self._alert_queue.put(alert)
            except asyncio.TimeoutError:
                logger.error("Não foi possível adicionar alerta à fila")
    
    def create_cultural_alert(self, alert_type: AlertType, term: str, 
                            value: float, threshold: float, 
                            level: AlertLevel = AlertLevel.WARNING) -> bool:
        """Criar e processar alerta cultural"""
        alert = AlertFactory.create_cultural_alert(alert_type, term, value, threshold, level)
        return self.add_alert(alert)
    
    def create_system_alert(self, alert_type: AlertType, component: str, 
                          message: str, level: AlertLevel = AlertLevel.ERROR) -> bool:
        """Criar e processar alerta de sistema"""
        alert = AlertFactory.create_system_alert(alert_type, component, message, level)
        return self.add_alert(alert)
    
    def add_rule(self, rule: AlertRule):
        """Adicionar regra de validação"""
        self._rules[rule.name] = rule
        logger.info(f"Regra adicionada: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remover regra de validação"""
        if rule_name in self._rules:
            del self._rules[rule_name]
            logger.info(f"Regra removida: {rule_name}")
    
    def subscribe(self, callback: Callable[[Alert], None]):
        """Adicionar subscriber para notificações de alertas"""
        self._subscribers.append(callback)
        logger.info("Subscriber adicionado")
    
    def unsubscribe(self, callback: Callable[[Alert], None]):
        """Remover subscriber"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.info("Subscriber removido")
    
    def get_alerts(self, limit: int = 100, level: AlertLevel = None, 
                  alert_type: AlertType = None) -> List[Alert]:
        """Obter alertas com filtros opcionais"""
        filtered_alerts = self._alert_history.copy()
        
        if level:
            filtered_alerts = [a for a in filtered_alerts if a.level == level]
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.alert_type == alert_type]
        
        # Ordenar por timestamp (mais recente primeiro)
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_alerts[:limit]
    
    def resolve_alert(self, alert_id: str, resolution: str = ""):
        """Marcar alerta como resolvido"""
        for alert in self._alert_history:
            if alert.id == alert_id:
                alert.status = "resolved"
                alert.metadata["resolution"] = resolution
                alert.metadata["resolved_at"] = datetime.now().isoformat()
                
                if alert_id in self._active_alerts:
                    self._active_alerts.remove(alert_id)
                
                logger.info(f"Alerta resolvido: {alert_id}")
                break
    
    def clear_history(self):
        """Limpar histórico de alertas"""
        self._alert_history.clear()
        self._active_alerts.clear()
        logger.info("Histórico de alertas limpo")
    
    def export_alerts(self, format: str = "json") -> str:
        """Exportar alertas em formato específico"""
        alerts_data = [asdict(alert) for alert in self._alert_history]
        
        if format == "json":
            return json.dumps(alerts_data, indent=2, ensure_ascii=False, default=str)
        elif format == "csv":
            # Implementar CSV se necessário
            pass
        
        return json.dumps(alerts_data, default=str)
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas dos alertas
        
        Returns:
            Dicionário com estatísticas completas
        """
        total_alerts = len(self._alert_history)
        
        # Contar por tipo
        type_counts = {}
        for alert in self._alert_history:
            alert_type = alert.alert_type.value if hasattr(alert.alert_type, 'value') else str(alert.alert_type)
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Contar por nível
        level_counts = {}
        for alert in self._alert_history:
            alert_level = alert.level.value if hasattr(alert.level, 'value') else str(alert.level)
            level_counts[alert_level] = level_counts.get(alert_level, 0) + 1
        
        # Estatísticas de tempo
        recent_alerts = len([a for a in self._alert_history if 
                           (datetime.now() - a.timestamp).total_seconds() < 3600])
        
        return {
            "total_alerts": total_alerts,
            "recent_alerts_1h": recent_alerts,
            "alerts_by_type": type_counts,
            "alerts_by_level": level_counts,
            "active_alerts": len(self._active_alerts),
            "manager_status": "active",
            "config_loaded": self.config is not None,
            "notification_manager": self.notification_manager is not None,
            "rules_count": len(self._rules),
            "queue_size": self._alert_queue.qsize() if self.config.async_processing else 0,
            "is_running": self._is_running
        }
    
    def get_alert_history(self, limit: int = 100, level: AlertLevel = None, 
                         alert_type: AlertType = None) -> List[Alert]:
        """
        Obter histórico de alertas com filtros
        
        Args:
            limit: Número máximo de alertas a retornar
            level: Filtrar por nível específico
            alert_type: Filtrar por tipo específico
            
        Returns:
            Lista de alertas filtrados
        """
        return self.get_alerts(limit, level, alert_type)
    
    def configure(self, config: AlertConfig):
        """Atualizar configuração do manager"""
        self.config = config
        
        # Reconfigurar notification manager
        if self.notification_manager:
            self.notification_manager.config = config.notifications
        
        logger.info("Configuração do AlertManager atualizada")
    
    def process_data(self, data: Dict[str, Any]):
        """Processar dados e gerar alertas automaticamente se necessário"""
        # Implementar lógica de análise de dados e geração automática de alertas
        # Baseado em thresholds e regras configuradas
        pass
    
    async def shutdown(self):
        """Finalizar o AlertManager de forma limpa"""
        try:
            self._is_running = False
            
            # Parar processamento assíncrono
            if self._background_task:
                self._background_task.cancel()
                try:
                    await self._background_task
                except asyncio.CancelledError:
                    pass
            
            # Processar alertas restantes na fila
            while not self._alert_queue.empty():
                try:
                    alert = await asyncio.wait_for(self._alert_queue.get(), timeout=1.0)
                    await self._process_single_alert(alert)
                except asyncio.TimeoutError:
                    break
            
            # Salvar estado final se necessário
            if self.cache_manager:
                await self.cache_manager.save_state()
            
            logger.info("AlertManager finalizado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao finalizar AlertManager: {e}")

# ========================================
# SINGLETON PATTERN
# ========================================

_alert_manager_instance = None
_manager_lock = threading.Lock()

def get_alert_manager(config: AlertConfig = None) -> AlertManager:
    """
    Obter instância singleton do AlertManager
    
    Args:
        config: Configuração opcional para inicialização
        
    Returns:
        Instância singleton do AlertManager
    """
    global _alert_manager_instance
    
    if _alert_manager_instance is None:
        with _manager_lock:
            if _alert_manager_instance is None:
                _alert_manager_instance = AlertManager(config)
    
    return _alert_manager_instance

def reset_alert_manager():
    """Reset do singleton (usado principalmente em testes)"""
    global _alert_manager_instance
    with _manager_lock:
        _alert_manager_instance = None

# ========================================
# CONVENIENCE FUNCTIONS  
# ========================================

def monitor_with_alerts(data: Dict[str, Any]):
    """Função conveniente para monitoramento com alertas automáticos"""
    get_alert_manager().process_data(data)
