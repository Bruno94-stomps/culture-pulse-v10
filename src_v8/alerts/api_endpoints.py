#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Endpoints para Alertas - Culture Pulse V9.0
Endpoints FastAPI consolidados para o sistema de alertas

🎯 FUNCIONALIDADES MIGRADAS:
- CRUD completo de alertas
- WebSocket para tempo real
- Configuração via API
- Estatísticas e métricas
- Integração com autenticação
- Documentação OpenAPI
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from pydantic import BaseModel, Field

from .alert_manager import get_alert_manager
from .alert_rules import Alert, AlertRule, AlertType, AlertLevel, AlertFactory, RuleFactory
from .alert_config import AlertConfig, AlertThresholds, NotificationConfig

# Router principal
alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])

# ========================================
# MODELS PYDANTIC
# ========================================

class AlertResponse(BaseModel):
    """Resposta de alerta"""
    id: str
    title: str
    message: str
    level: str
    alert_type: str
    source: str
    data: Dict[str, Any]
    timestamp: str
    resolved: bool
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    actions_taken: List[str]
    tags: List[str]
    metadata: Dict[str, Any]

class AlertRequest(BaseModel):
    """Requisição para criar alerta"""
    title: str = Field(..., description="Título do alerta")
    message: str = Field(..., description="Mensagem do alerta")
    level: str = Field(..., description="Nível do alerta (info, warning, error, critical)")
    alert_type: str = Field(..., description="Tipo do alerta")
    source: str = Field(default="api", description="Origem do alerta")
    data: Dict[str, Any] = Field(default_factory=dict, description="Dados adicionais")
    tags: List[str] = Field(default_factory=list, description="Tags do alerta")

class AlertRuleResponse(BaseModel):
    """Resposta de regra de alerta"""
    id: str
    name: str
    description: str
    alert_type: str
    alert_level: str
    enabled: bool
    threshold_value: float
    threshold_operator: str
    field_path: str
    cooldown_minutes: int
    max_alerts_per_hour: int
    require_consecutive: int
    created_at: str
    updated_at: str
    created_by: str

class AlertRuleRequest(BaseModel):
    """Requisição para criar/atualizar regra"""
    name: str = Field(..., description="Nome da regra")
    description: str = Field(..., description="Descrição da regra")
    alert_type: str = Field(..., description="Tipo de alerta a gerar")
    alert_level: str = Field(..., description="Nível de alerta a gerar")
    enabled: bool = Field(default=True, description="Se a regra está ativa")
    threshold_value: float = Field(..., description="Valor limite")
    threshold_operator: str = Field(default=">=", description="Operador de comparação")
    field_path: str = Field(..., description="Caminho do campo a avaliar")
    cooldown_minutes: int = Field(default=5, description="Cooldown em minutos")
    max_alerts_per_hour: int = Field(default=10, description="Máximo de alertas por hora")
    require_consecutive: int = Field(default=1, description="Ocorrências consecutivas necessárias")

class ResolveAlertRequest(BaseModel):
    """Requisição para resolver alerta"""
    resolved_by: Optional[str] = None
    action: Optional[str] = None

class AlertStatsResponse(BaseModel):
    """Resposta de estatísticas"""
    total_alerts: int
    alerts_today: int
    alerts_resolved: int
    active_alerts: int
    total_rules: int
    alerts_per_hour: float
    avg_resolution_time: float
    system_health: str
    alerts_by_type: Dict[str, int]
    alerts_by_level: Dict[str, int]
    cache_size: int
    queue_size: int

class ConfigResponse(BaseModel):
    """Resposta de configuração"""
    enabled: bool
    max_alerts_per_minute: int
    alert_cooldown_seconds: int
    alert_history_limit: int
    thresholds: Dict[str, float]
    notifications_enabled: bool

class ConfigRequest(BaseModel):
    """Requisição para atualizar configuração"""
    enabled: Optional[bool] = None
    max_alerts_per_minute: Optional[int] = None
    alert_cooldown_seconds: Optional[int] = None
    alert_history_limit: Optional[int] = None
    thresholds: Optional[Dict[str, float]] = None

# ========================================
# WEBSOCKET MANAGER
# ========================================

class WebSocketManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Aceitar nova conexão"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remover conexão"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_alert(self, alert: Alert):
        """Enviar alerta para todas as conexões"""
        if not self.active_connections:
            return
        
        message = {
            "event": "new_alert",
            "data": alert.to_dict()
        }
        
        # Enviar para todas as conexões ativas
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remover conexões mortas
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast mensagem para todas as conexões"""
        if not self.active_connections:
            return
        
        text_message = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(text_message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

# Instância global do WebSocket manager
ws_manager = WebSocketManager()

# ========================================
# HELPER FUNCTIONS
# ========================================

def alert_to_response(alert: Alert) -> AlertResponse:
    """Converter Alert para AlertResponse"""
    return AlertResponse(
        id=alert.id,
        title=alert.title,
        message=alert.message,
        level=alert.level.value,
        alert_type=alert.alert_type.value,
        source=alert.source,
        data=alert.data,
        timestamp=alert.timestamp.isoformat(),
        resolved=alert.resolved,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        resolved_by=alert.resolved_by,
        actions_taken=alert.actions_taken,
        tags=alert.tags,
        metadata=alert.metadata
    )

def rule_to_response(rule: AlertRule) -> AlertRuleResponse:
    """Converter AlertRule para AlertRuleResponse"""
    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        alert_type=rule.alert_type.value,
        alert_level=rule.alert_level.value,
        enabled=rule.enabled,
        threshold_value=rule.threshold_value,
        threshold_operator=rule.threshold_operator,
        field_path=rule.field_path,
        cooldown_minutes=rule.cooldown_minutes,
        max_alerts_per_hour=rule.max_alerts_per_hour,
        require_consecutive=rule.require_consecutive,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
        created_by=rule.created_by
    )

# ========================================
# ENDPOINTS DE ALERTAS
# ========================================

@alerts_router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = Query(50, ge=1, le=1000),
    level: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    active_only: bool = Query(False)
):
    """
    Listar alertas com filtros opcionais
    
    - **limit**: Número máximo de alertas a retornar
    - **level**: Filtrar por nível (info, warning, error, critical)
    - **alert_type**: Filtrar por tipo de alerta
    - **resolved**: Filtrar por status de resolução
    - **active_only**: Retornar apenas alertas ativos
    """
    try:
        manager = get_alert_manager()
        
        if active_only:
            alerts = manager.get_active_alerts()
        else:
            alerts = manager.get_alert_history(limit)
        
        # Aplicar filtros
        if level:
            try:
                level_enum = AlertLevel(level)
                alerts = [a for a in alerts if a.level == level_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Nível inválido: {level}")
        
        if alert_type:
            try:
                type_enum = AlertType(alert_type)
                alerts = [a for a in alerts if a.alert_type == type_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Tipo inválido: {alert_type}")
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return [alert_to_response(alert) for alert in alerts[:limit]]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {str(e)}")

@alerts_router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str):
    """Obter alerta específico por ID"""
    try:
        manager = get_alert_manager()
        
        # Procurar em alertas ativos
        if alert_id in manager._active_alerts:
            alert = manager._active_alerts[alert_id]
            return alert_to_response(alert)
        
        # Procurar no histórico
        for alert in manager.get_alert_history():
            if alert.id == alert_id:
                return alert_to_response(alert)
        
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alerta: {str(e)}")

@alerts_router.post("/", response_model=AlertResponse)
async def create_alert(alert_request: AlertRequest, background_tasks: BackgroundTasks):
    """Criar novo alerta"""
    try:
        # Validar enums
        try:
            level = AlertLevel(alert_request.level)
            alert_type = AlertType(alert_request.alert_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Valor inválido: {str(e)}")
        
        # Criar alerta
        if alert_type in [AlertType.HIGH_MOMENTUM, AlertType.NEGATIVE_SENTIMENT, 
                         AlertType.VOLUME_SPIKE, AlertType.CONSENSUS_LOW]:
            # Alerta cultural
            term = alert_request.data.get('term', 'termo_api')
            value = alert_request.data.get('value', 0)
            threshold = alert_request.data.get('threshold', 0)
            
            alert = AlertFactory.create_cultural_alert(
                alert_type, term, value, threshold, level
            )
        else:
            # Alerta de sistema
            component = alert_request.data.get('component', 'api')
            
            alert = AlertFactory.create_system_alert(
                alert_type, component, alert_request.message, level, alert_request.data
            )
        
        # Customizar com dados da requisição
        alert.title = alert_request.title
        alert.message = alert_request.message
        alert.source = alert_request.source
        alert.tags.extend(alert_request.tags)
        
        # Adicionar alerta
        manager = get_alert_manager()
        success = manager.add_alert(alert)
        
        if not success:
            raise HTTPException(status_code=400, detail="Alerta rejeitado (rate limit ou duplicado)")
        
        # Enviar via WebSocket em background
        background_tasks.add_task(ws_manager.send_alert, alert)
        
        return alert_to_response(alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar alerta: {str(e)}")

@alerts_router.put("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(alert_id: str, resolve_request: ResolveAlertRequest):
    """Resolver alerta específico"""
    try:
        manager = get_alert_manager()
        
        success = manager.resolve_alert(
            alert_id, 
            resolve_request.resolved_by,
            resolve_request.action
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Alerta não encontrado ou já resolvido")
        
        # Retornar alerta atualizado
        if alert_id in manager._active_alerts:
            alert = manager._active_alerts[alert_id]
            return alert_to_response(alert)
        
        raise HTTPException(status_code=404, detail="Alerta não encontrado após resolução")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resolver alerta: {str(e)}")

@alerts_router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Remover alerta (apenas de alertas ativos)"""
    try:
        manager = get_alert_manager()
        
        if alert_id in manager._active_alerts:
            del manager._active_alerts[alert_id]
            return {"message": "Alerta removido com sucesso"}
        
        raise HTTPException(status_code=404, detail="Alerta não encontrado nos alertas ativos")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover alerta: {str(e)}")

# ========================================
# ENDPOINTS DE REGRAS
# ========================================

@alerts_router.get("/rules", response_model=List[AlertRuleResponse])
async def get_rules():
    """Listar todas as regras de alerta"""
    try:
        manager = get_alert_manager()
        rules = manager.get_rules()
        return [rule_to_response(rule) for rule in rules]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter regras: {str(e)}")

@alerts_router.post("/rules", response_model=AlertRuleResponse)
async def create_rule(rule_request: AlertRuleRequest):
    """Criar nova regra de alerta"""
    try:
        # Validar enums
        try:
            alert_type = AlertType(rule_request.alert_type)
            alert_level = AlertLevel(rule_request.alert_level)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Valor inválido: {str(e)}")
        
        # Criar regra
        rule = AlertRule(
            id=f"api_rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=rule_request.name,
            description=rule_request.description,
            alert_type=alert_type,
            alert_level=alert_level,
            enabled=rule_request.enabled,
            threshold_value=rule_request.threshold_value,
            threshold_operator=rule_request.threshold_operator,
            field_path=rule_request.field_path,
            cooldown_minutes=rule_request.cooldown_minutes,
            max_alerts_per_hour=rule_request.max_alerts_per_hour,
            require_consecutive=rule_request.require_consecutive,
            created_by="api"
        )
        
        # Adicionar regra
        manager = get_alert_manager()
        manager.add_rule(rule)
        
        return rule_to_response(rule)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar regra: {str(e)}")

@alerts_router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Remover regra de alerta"""
    try:
        manager = get_alert_manager()
        success = manager.remove_rule(rule_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        return {"message": "Regra removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover regra: {str(e)}")

# ========================================
# ENDPOINTS DE CONFIGURAÇÃO
# ========================================

@alerts_router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Obter configuração atual do sistema de alertas"""
    try:
        manager = get_alert_manager()
        config = manager.config
        
        return ConfigResponse(
            enabled=config.enabled,
            max_alerts_per_minute=config.max_alerts_per_minute,
            alert_cooldown_seconds=config.alert_cooldown_seconds,
            alert_history_limit=config.alert_history_limit,
            thresholds={
                "high_momentum": config.thresholds.high_momentum,
                "low_momentum": config.thresholds.low_momentum,
                "positive_sentiment": config.thresholds.positive_sentiment,
                "negative_sentiment": config.thresholds.negative_sentiment,
                "volume_spike": config.thresholds.volume_spike,
                "volume_drop": config.thresholds.volume_drop,
                "consensus_high": config.thresholds.consensus_high,
                "consensus_low": config.thresholds.consensus_low,
            },
            notifications_enabled=config.notifications.enabled
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter configuração: {str(e)}")

@alerts_router.put("/config", response_model=ConfigResponse)
async def update_config(config_request: ConfigRequest):
    """Atualizar configuração do sistema de alertas"""
    try:
        manager = get_alert_manager()
        config = manager.config
        
        # Atualizar campos fornecidos
        if config_request.enabled is not None:
            config.enabled = config_request.enabled
        
        if config_request.max_alerts_per_minute is not None:
            config.max_alerts_per_minute = config_request.max_alerts_per_minute
        
        if config_request.alert_cooldown_seconds is not None:
            config.alert_cooldown_seconds = config_request.alert_cooldown_seconds
        
        if config_request.alert_history_limit is not None:
            config.alert_history_limit = config_request.alert_history_limit
        
        if config_request.thresholds:
            for key, value in config_request.thresholds.items():
                if hasattr(config.thresholds, key):
                    setattr(config.thresholds, key, value)
        
        # Reaplicar configuração
        manager.configure(config)
        
        # Retornar configuração atualizada
        return await get_config()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar configuração: {str(e)}")

# ========================================
# ENDPOINTS DE ESTATÍSTICAS
# ========================================

@alerts_router.get("/stats", response_model=AlertStatsResponse)
async def get_stats():
    """Obter estatísticas do sistema de alertas"""
    try:
        manager = get_alert_manager()
        stats = manager.get_stats()
        
        return AlertStatsResponse(
            total_alerts=stats['total_alerts'],
            alerts_today=stats['alerts_today'],
            alerts_resolved=stats['alerts_resolved'],
            active_alerts=stats['active_alerts'],
            total_rules=stats['total_rules'],
            alerts_per_hour=stats['alerts_per_hour'],
            avg_resolution_time=stats['avg_resolution_time'],
            system_health=stats['system_health'],
            alerts_by_type=dict(stats['alerts_by_type']),
            alerts_by_level=dict(stats['alerts_by_level']),
            cache_size=stats['cache_size'],
            queue_size=stats['queue_size']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

# ========================================
# ENDPOINT DE PROCESSAMENTO
# ========================================

@alerts_router.post("/process")
async def process_data(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Processar dados e gerar alertas automaticamente
    
    Aceita dados de análise cultural e aplica todas as regras configuradas
    """
    try:
        manager = get_alert_manager()
        
        # Processar dados em background
        background_tasks.add_task(manager.process_data, data)
        
        return {"message": "Dados enviados para processamento"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")

# ========================================
# WEBSOCKET ENDPOINT
# ========================================

@alerts_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para alertas em tempo real
    
    Conecte-se para receber notificações de novos alertas em tempo real
    """
    await ws_manager.connect(websocket)
    
    try:
        # Enviar alertas ativos na conexão
        manager = get_alert_manager()
        active_alerts = manager.get_active_alerts()
        
        if active_alerts:
            await websocket.send_text(json.dumps({
                "event": "active_alerts",
                "data": [alert.to_dict() for alert in active_alerts[-5:]]  # Últimos 5
            }))
        
        # Manter conexão viva
        while True:
            # Aguardar ping do cliente
            await websocket.receive_text()
            
            # Responder com pong
            await websocket.send_text(json.dumps({
                "event": "pong",
                "timestamp": datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# ========================================
# ENDPOINTS DE UTILIDADE
# ========================================

@alerts_router.post("/clear/resolved")
async def clear_resolved_alerts():
    """Limpar alertas resolvidos dos ativos"""
    try:
        manager = get_alert_manager()
        manager.clear_resolved_alerts()
        return {"message": "Alertas resolvidos removidos"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar alertas: {str(e)}")

@alerts_router.post("/clear/history")
async def clear_history():
    """Limpar histórico de alertas"""
    try:
        manager = get_alert_manager()
        manager.clear_history()
        return {"message": "Histórico de alertas limpo"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar histórico: {str(e)}")

@alerts_router.get("/export")
async def export_alerts(format: str = Query("json", regex="^(json|csv)$")):
    """Exportar alertas em formato específico"""
    try:
        manager = get_alert_manager()
        export_data = manager.export_alerts(format)
        
        return {
            "format": format,
            "data": export_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar alertas: {str(e)}")

@alerts_router.get("/health")
async def health_check():
    """Health check do sistema de alertas"""
    try:
        manager = get_alert_manager()
        stats = manager.get_stats()
        
        return {
            "status": "healthy",
            "system_health": stats['system_health'],
            "active_alerts": stats['active_alerts'],
            "total_rules": stats['total_rules'],
            "websocket_connections": len(ws_manager.active_connections),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
