#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regras e Tipos de Alertas - Culture Pulse V9.0
Definições centralizadas de tipos, níveis e regras de alertas

🎯 FUNCIONALIDADES:
- Enum de tipos de alerta
- Enum de níveis de alerta
- Estruturas de dados para alertas
- Regras de validação
- Factories para criação
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

class AlertType(Enum):
    """Tipos de alerta do sistema"""
    
    # Alertas culturais
    HIGH_MOMENTUM = "high_momentum"
    LOW_MOMENTUM = "low_momentum"
    POSITIVE_SENTIMENT = "positive_sentiment"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    VOLUME_SPIKE = "volume_spike"
    VOLUME_DROP = "volume_drop"
    CONSENSUS_HIGH = "consensus_high"
    CONSENSUS_LOW = "consensus_low"
    
    # Alertas de tendências
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    EMERGING_PROFILE = "emerging_profile"
    CULTURAL_TENSION = "cultural_tension"
    
    # Alertas de sistema
    API_HEALTH = "api_health"
    SYSTEM_PERFORMANCE = "system_performance"
    DATA_ANOMALY = "data_anomaly"
    COLLECTOR_STATUS = "collector_status"
    CACHE_PERFORMANCE = "cache_performance"
    
    # Alertas de negócio
    BRAND_SCORE = "brand_score"
    ENGAGEMENT_DROP = "engagement_drop"
    QUALITY_ISSUE = "quality_issue"

class AlertLevel(Enum):
    """Níveis de severidade dos alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __lt__(self, other):
        """Comparação de níveis (para ordenação)"""
        levels = ['info', 'warning', 'error', 'critical']
        return levels.index(self.value) < levels.index(other.value)
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other

@dataclass
class Alert:
    """Estrutura de um alerta"""
    id: str
    title: str
    message: str
    level: AlertLevel
    alert_type: AlertType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        result = asdict(self)
        result['level'] = self.level.value
        result['alert_type'] = self.alert_type.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Criar Alert a partir de dicionário"""
        # Converter strings para enums
        data['level'] = AlertLevel(data['level'])
        data['alert_type'] = AlertType(data['alert_type'])
        
        # Converter timestamps
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('resolved_at'):
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'])
        
        return cls(**data)
    
    def resolve(self, resolved_by: str = None, action: str = None):
        """Marcar alerta como resolvido"""
        self.resolved = True
        self.resolved_at = datetime.now()
        self.resolved_by = resolved_by
        
        if action:
            self.actions_taken.append(action)
    
    def add_action(self, action: str):
        """Adicionar ação tomada"""
        self.actions_taken.append(action)
        self.metadata['last_action'] = action
        self.metadata['last_action_time'] = datetime.now().isoformat()
    
    def add_tag(self, tag: str):
        """Adicionar tag ao alerta"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def is_recent(self, minutes: int = 60) -> bool:
        """Verificar se alerta é recente"""
        threshold = datetime.now() - timedelta(minutes=minutes)
        return self.timestamp > threshold
    
    def get_age_minutes(self) -> int:
        """Obter idade do alerta em minutos"""
        return int((datetime.now() - self.timestamp).total_seconds() / 60)

@dataclass
class AlertRule:
    """Regra para geração de alertas"""
    id: str
    name: str
    description: str
    alert_type: AlertType
    alert_level: AlertLevel
    enabled: bool = True
    
    # Condições
    threshold_value: Union[float, int] = 0
    threshold_operator: str = ">="  # >=, <=, ==, !=, >, <
    field_path: str = ""  # Campo para avaliar (ex: "momentum", "sentiment")
    
    # Configurações
    cooldown_minutes: int = 5
    max_alerts_per_hour: int = 10
    require_consecutive: int = 1  # Quantas vezes consecutivas antes de alertar
    
    # Metadados
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    # Contadores internos
    _consecutive_count: int = field(default=0, init=False)
    _last_alert: Optional[datetime] = field(default=None, init=False)
    _alerts_this_hour: int = field(default=0, init=False)
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """
        Avaliar se regra deve gerar alerta
        
        Args:
            data: Dados para avaliar
            
        Returns:
            True se deve gerar alerta
        """
        if not self.enabled:
            return False
        
        # Verificar cooldown
        if self._last_alert:
            time_since_last = datetime.now() - self._last_alert
            if time_since_last.total_seconds() < (self.cooldown_minutes * 60):
                return False
        
        # Verificar limite por hora
        if self._alerts_this_hour >= self.max_alerts_per_hour:
            return False
        
        # Obter valor do campo
        value = self._get_field_value(data, self.field_path)
        if value is None:
            return False
        
        # Avaliar condição
        condition_met = self._evaluate_condition(value, self.threshold_value, self.threshold_operator)
        
        # Verificar consecutividade
        if condition_met:
            self._consecutive_count += 1
        else:
            self._consecutive_count = 0
            return False
        
        # Verificar se atingiu o mínimo consecutivo
        if self._consecutive_count >= self.require_consecutive:
            self._last_alert = datetime.now()
            self._alerts_this_hour += 1
            self._consecutive_count = 0  # Reset contador
            return True
        
        return False
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Obter valor de campo usando dot notation"""
        try:
            value = data
            for key in field_path.split('.'):
                if isinstance(value, dict):
                    value = value.get(key)
                elif hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return None
                
                if value is None:
                    return None
            
            return value
        except:
            return None
    
    def _evaluate_condition(self, value: Any, threshold: Any, operator: str) -> bool:
        """Avaliar condição baseada no operador"""
        try:
            if operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == "==":
                return value == threshold
            elif operator == "!=":
                return value != threshold
            else:
                return False
        except:
            return False
    
    def reset_counters(self):
        """Reset contadores da regra"""
        self._consecutive_count = 0
        self._alerts_this_hour = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        result = asdict(self)
        result['alert_type'] = self.alert_type.value
        result['alert_level'] = self.alert_level.value
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result

class AlertFactory:
    """Factory para criação de alertas"""
    
    @staticmethod
    def create_cultural_alert(
        alert_type: AlertType,
        term: str,
        value: float,
        threshold: float,
        level: AlertLevel = AlertLevel.WARNING
    ) -> Alert:
        """Criar alerta cultural"""
        
        titles = {
            AlertType.HIGH_MOMENTUM: f"🔥 Alto Momentum: {term}",
            AlertType.NEGATIVE_SENTIMENT: f"😞 Sentimento Negativo: {term}",
            AlertType.VOLUME_SPIKE: f"📈 Pico de Volume: {term}",
            AlertType.CONSENSUS_LOW: f"⚠️ Baixo Consenso: {term}",
        }
        
        messages = {
            AlertType.HIGH_MOMENTUM: f"O termo '{term}' está com momentum de {value:.1f} (limite: {threshold})",
            AlertType.NEGATIVE_SENTIMENT: f"O termo '{term}' tem sentimento de {value:.2f} (limite: {threshold})",
            AlertType.VOLUME_SPIKE: f"O termo '{term}' teve pico de volume: {value} (limite: {threshold})",
            AlertType.CONSENSUS_LOW: f"O termo '{term}' tem baixo consenso: {value:.1f}% (limite: {threshold}%)",
        }
        
        return Alert(
            id=str(uuid.uuid4()),
            title=titles.get(alert_type, f"Alerta: {term}"),
            message=messages.get(alert_type, f"Alerta para {term}: {value}"),
            level=level,
            alert_type=alert_type,
            source="cultural_analysis",
            data={
                "term": term,
                "value": value,
                "threshold": threshold,
                "measurement_type": alert_type.value
            },
            tags=["cultural", "automated"]
        )
    
    @staticmethod
    def create_system_alert(
        alert_type: AlertType,
        component: str,
        message: str,
        level: AlertLevel = AlertLevel.ERROR,
        data: Dict[str, Any] = None
    ) -> Alert:
        """Criar alerta de sistema"""
        
        return Alert(
            id=str(uuid.uuid4()),
            title=f"🔧 Sistema: {component}",
            message=message,
            level=level,
            alert_type=alert_type,
            source="system_monitor",
            data=data or {},
            tags=["system", "automated"]
        )

class RuleFactory:
    """Factory para criação de regras"""
    
    @staticmethod
    def create_momentum_rule(threshold: float = 80.0) -> AlertRule:
        """Criar regra para alto momentum"""
        return AlertRule(
            id=f"momentum_rule_{threshold}",
            name="Alto Momentum Cultural",
            description=f"Alerta quando momentum > {threshold}",
            alert_type=AlertType.HIGH_MOMENTUM,
            alert_level=AlertLevel.WARNING,
            threshold_value=threshold,
            threshold_operator=">=",
            field_path="momentum",
            cooldown_minutes=5
        )
    
    @staticmethod
    def create_sentiment_rule(threshold: float = -0.5) -> AlertRule:
        """Criar regra para sentimento negativo"""
        return AlertRule(
            id=f"sentiment_rule_{threshold}",
            name="Sentimento Negativo",
            description=f"Alerta quando sentimento <= {threshold}",
            alert_type=AlertType.NEGATIVE_SENTIMENT,
            alert_level=AlertLevel.WARNING,
            threshold_value=threshold,
            threshold_operator="<=",
            field_path="sentiment",
            cooldown_minutes=10
        )
    
    @staticmethod
    def create_volume_rule(threshold: int = 100) -> AlertRule:
        """Criar regra para pico de volume"""
        return AlertRule(
            id=f"volume_rule_{threshold}",
            name="Pico de Volume",
            description=f"Alerta quando volume > {threshold}",
            alert_type=AlertType.VOLUME_SPIKE,
            alert_level=AlertLevel.INFO,
            threshold_value=threshold,
            threshold_operator=">",
            field_path="volume",
            cooldown_minutes=3
        )

# Regras padrão do sistema
DEFAULT_RULES = [
    RuleFactory.create_momentum_rule(80.0),
    RuleFactory.create_sentiment_rule(-0.5),
    RuleFactory.create_volume_rule(100),
]
