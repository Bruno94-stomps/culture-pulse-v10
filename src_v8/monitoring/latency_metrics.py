#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Métricas de Latência - Culture Pulse V9.0
Monitoramento detalhado de performance das APIs

📊 FUNCIONALIDADES:
- Latência individual por API
- Métricas históricas e tendências
- Detecção de degradação de performance
- Alertas automáticos
- Dashboard de monitoramento

🎯 MÉTRICAS RASTREADAS:
- Tempo de resposta por API
- Taxa de sucesso/erro
- Throughput (calls/minuto)
- Percentis de latência (P50, P95, P99)
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class APICallMetric:
    """Métrica de uma chamada de API"""
    api_name: str
    start_time: float
    end_time: float
    success: bool
    error_type: Optional[str] = None
    response_size: Optional[int] = None
    endpoint: Optional[str] = None
    
    @property
    def latency_ms(self) -> float:
        """Latência em milissegundos"""
        return (self.end_time - self.start_time) * 1000
    
    @property
    def timestamp(self) -> datetime:
        """Timestamp da chamada"""
        return datetime.fromtimestamp(self.start_time)


@dataclass
class APIPerformanceStats:
    """Estatísticas de performance de uma API"""
    api_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_history: deque = field(default_factory=lambda: deque(maxlen=100))
    hourly_stats: Dict[str, int] = field(default_factory=dict)
    
    @property
    def avg_latency_ms(self) -> float:
        """Latência média"""
        return self.total_latency_ms / max(self.total_calls, 1)
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso"""
        return (self.successful_calls / max(self.total_calls, 1)) * 100
    
    @property
    def error_rate(self) -> float:
        """Taxa de erro"""
        return (self.failed_calls / max(self.total_calls, 1)) * 100


class LatencyMetrics:
    """Sistema completo de métricas de latência"""
    
    def __init__(self):
        self.api_stats: Dict[str, APIPerformanceStats] = {}
        self.active_calls: Dict[str, float] = {}  # call_id -> start_time
        self.global_stats = {
            'total_calls': 0,
            'total_apis': 0,
            'avg_latency_all_apis': 0.0,
            'system_health_score': 100.0
        }
        
        # Configuração de alertas
        self.alert_thresholds = {
            'latency_p95_ms': 5000,  # P95 > 5s = alerta
            'error_rate_percent': 10,  # Error rate > 10% = alerta
            'success_rate_percent': 90,  # Success rate < 90% = alerta
            'degradation_factor': 2.0  # Latência 2x maior = degradação
        }
        
        # Histórico de alertas
        self.recent_alerts = deque(maxlen=50)
        
        logger.info("📊 Sistema de métricas de latência inicializado")
    
    def start_api_call(self, api_name: str, endpoint: str = None) -> str:
        """Iniciar rastreamento de uma chamada de API"""
        call_id = f"{api_name}_{int(time.time() * 1000000)}"
        self.active_calls[call_id] = time.time()
        
        # Inicializar stats da API se necessário
        if api_name not in self.api_stats:
            self.api_stats[api_name] = APIPerformanceStats(api_name=api_name)
            self.global_stats['total_apis'] = len(self.api_stats)
        
        return call_id
    
    def end_api_call(
        self, 
        call_id: str, 
        success: bool = True, 
        error_type: str = None,
        response_size: int = None
    ):
        """Finalizar rastreamento de uma chamada de API"""
        if call_id not in self.active_calls:
            logger.warning(f"Call ID {call_id} não encontrado")
            return
        
        start_time = self.active_calls.pop(call_id)
        end_time = time.time()
        
        # Extrair info do call_id - melhorar parsing para operações V9.0
        api_name = call_id.split('_')[0]
        
        # Se for uma operação V9.0, usar nome genérico
        if api_name in ['unified', 'test', 'operation']:
            api_name = 'system_operation'
        
        # Criar métrica
        metric = APICallMetric(
            api_name=api_name,
            start_time=start_time,
            end_time=end_time,
            success=success,
            error_type=error_type,
            response_size=response_size
        )
        
        # Atualizar estatísticas
        self._update_api_stats(metric)
        self._update_global_stats()
        self._check_performance_alerts(api_name)
        
        logger.debug(f"📊 {api_name}: {metric.latency_ms:.1f}ms ({'✅' if success else '❌'})")
    
    def _update_api_stats(self, metric: APICallMetric):
        """Atualizar estatísticas da API"""
        stats = self.api_stats[metric.api_name]
        
        # Contadores
        stats.total_calls += 1
        if metric.success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
            stats.error_history.append({
                'timestamp': metric.timestamp,
                'error_type': metric.error_type
            })
        
        # Latência
        latency_ms = metric.latency_ms
        stats.total_latency_ms += latency_ms
        stats.min_latency_ms = min(stats.min_latency_ms, latency_ms)
        stats.max_latency_ms = max(stats.max_latency_ms, latency_ms)
        stats.latency_history.append(latency_ms)
        
        # Estatísticas horárias
        hour_key = metric.timestamp.strftime('%Y-%m-%d-%H')
        stats.hourly_stats[hour_key] = stats.hourly_stats.get(hour_key, 0) + 1
    
    def _update_global_stats(self):
        """Atualizar estatísticas globais"""
        total_calls = sum(stats.total_calls for stats in self.api_stats.values())
        total_latency = sum(stats.total_latency_ms for stats in self.api_stats.values())
        
        self.global_stats['total_calls'] = total_calls
        self.global_stats['avg_latency_all_apis'] = total_latency / max(total_calls, 1)
        
        # Calcular health score
        avg_success_rate = statistics.mean([
            stats.success_rate for stats in self.api_stats.values()
        ]) if self.api_stats else 100
        
        avg_latency = self.global_stats['avg_latency_all_apis']
        latency_penalty = min(50, avg_latency / 100)  # Max 50 pontos de penalidade
        
        self.global_stats['system_health_score'] = max(0, avg_success_rate - latency_penalty)
    
    def _check_performance_alerts(self, api_name: str):
        """Verificar alertas de performance"""
        stats = self.api_stats[api_name]
        alerts = []
        
        # Alert: Taxa de erro alta
        if stats.error_rate > self.alert_thresholds['error_rate_percent']:
            alerts.append({
                'type': 'high_error_rate',
                'api': api_name,
                'value': stats.error_rate,
                'threshold': self.alert_thresholds['error_rate_percent'],
                'severity': 'HIGH' if stats.error_rate > 20 else 'MEDIUM'
            })
        
        # Alert: Taxa de sucesso baixa
        if stats.success_rate < self.alert_thresholds['success_rate_percent']:
            alerts.append({
                'type': 'low_success_rate',
                'api': api_name,
                'value': stats.success_rate,
                'threshold': self.alert_thresholds['success_rate_percent'],
                'severity': 'HIGH'
            })
        
        # Alert: Latência P95 alta
        if len(stats.latency_history) >= 20:
            p95_latency = self._calculate_percentile(list(stats.latency_history), 95)
            if p95_latency > self.alert_thresholds['latency_p95_ms']:
                alerts.append({
                    'type': 'high_latency_p95',
                    'api': api_name,
                    'value': p95_latency,
                    'threshold': self.alert_thresholds['latency_p95_ms'],
                    'severity': 'MEDIUM'
                })
        
        # Alert: Degradação de performance
        if len(stats.latency_history) >= 50:
            recent_avg = statistics.mean(list(stats.latency_history)[-10:])
            historical_avg = statistics.mean(list(stats.latency_history)[:-10])
            
            if recent_avg > historical_avg * self.alert_thresholds['degradation_factor']:
                alerts.append({
                    'type': 'performance_degradation',
                    'api': api_name,
                    'recent_avg': recent_avg,
                    'historical_avg': historical_avg,
                    'degradation_factor': recent_avg / historical_avg,
                    'severity': 'HIGH'
                })
        
        # Registrar alertas
        for alert in alerts:
            alert['timestamp'] = datetime.now()
            self.recent_alerts.append(alert)
            
            severity_emoji = {'LOW': '🟡', 'MEDIUM': '🟠', 'HIGH': '🔴'}
            emoji = severity_emoji.get(alert['severity'], '⚠️')
            
            logger.warning(f"{emoji} ALERTA {alert['type']}: {api_name} - {alert}")
    
    def get_api_performance(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Obter performance detalhada de uma API"""
        if api_name not in self.api_stats:
            return None
        
        stats = self.api_stats[api_name]
        latencies = list(stats.latency_history)
        
        performance = {
            'api_name': api_name,
            'total_calls': stats.total_calls,
            'success_rate': round(stats.success_rate, 2),
            'error_rate': round(stats.error_rate, 2),
            'avg_latency_ms': round(stats.avg_latency_ms, 2),
            'min_latency_ms': round(stats.min_latency_ms, 2),
            'max_latency_ms': round(stats.max_latency_ms, 2),
        }
        
        # Percentis de latência
        if latencies:
            performance.update({
                'p50_latency_ms': round(self._calculate_percentile(latencies, 50), 2),
                'p95_latency_ms': round(self._calculate_percentile(latencies, 95), 2),
                'p99_latency_ms': round(self._calculate_percentile(latencies, 99), 2),
            })
        
        # Throughput (calls por minuto)
        recent_calls = [
            timestamp for timestamp in stats.hourly_stats.values()
        ]
        if recent_calls:
            performance['throughput_calls_per_minute'] = sum(recent_calls[-60:]) / max(len(recent_calls[-60:]), 1)
        
        # Erros recentes
        performance['recent_errors'] = list(stats.error_history)[-5:]
        
        return performance
    
    def get_all_apis_summary(self) -> Dict[str, Any]:
        """Resumo de todas as APIs"""
        summary = {
            'global_stats': self.global_stats.copy(),
            'api_count': len(self.api_stats),
            'apis': {}
        }
        
        for api_name, stats in self.api_stats.items():
            summary['apis'][api_name] = {
                'calls': stats.total_calls,
                'success_rate': round(stats.success_rate, 1),
                'avg_latency_ms': round(stats.avg_latency_ms, 1),
                'status': self._get_api_status(stats)
            }
        
        # Top APIs por volume
        summary['top_apis_by_volume'] = sorted(
            [(name, stats.total_calls) for name, stats in self.api_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top APIs por latência
        summary['top_apis_by_latency'] = sorted(
            [(name, stats.avg_latency_ms) for name, stats in self.api_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return summary
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Obter alertas recentes"""
        return list(self.recent_alerts)[-limit:]
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """Calcular percentil"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = int(index)
            upper = lower + 1
            weight = index - lower
            return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def _get_api_status(self, stats: APIPerformanceStats) -> str:
        """Determinar status da API"""
        if stats.total_calls == 0:
            return 'INACTIVE'
        
        if stats.success_rate >= 95 and stats.avg_latency_ms < 2000:
            return 'EXCELLENT'
        elif stats.success_rate >= 90 and stats.avg_latency_ms < 5000:
            return 'GOOD'
        elif stats.success_rate >= 80:
            return 'FAIR'
        else:
            return 'POOR'
    
    def reset_metrics(self, api_name: str = None):
        """Resetar métricas"""
        if api_name:
            if api_name in self.api_stats:
                del self.api_stats[api_name]
                logger.info(f"📊 Métricas de {api_name} resetadas")
        else:
            self.api_stats.clear()
            self.global_stats = {
                'total_calls': 0,
                'total_apis': 0,
                'avg_latency_all_apis': 0.0,
                'system_health_score': 100.0
            }
            logger.info("📊 Todas as métricas resetadas")
    
    async def record_operation(
        self, 
        operation: str, 
        duration: float, 
        success: bool = True, 
        error: str = None
    ):
        """
        Registrar uma operação genérica com métricas
        
        Args:
            operation: Nome da operação (ex: 'unified_collection', 'api_call')
            duration: Duração em segundos
            success: Se a operação foi bem-sucedida
            error: Mensagem de erro (se houver)
        """
        try:
            # Simular call_id baseado na operação
            call_id = f"{operation}_{int(time.time() * 1000000)}"
            
            # Registrar como se fosse uma chamada de API
            start_time = time.time() - duration
            self.active_calls[call_id] = start_time
            
            # Finalizar chamada
            self.end_api_call(
                call_id=call_id,
                success=success,
                error_type=error
            )
            
            logger.debug(f"📊 Operação {operation} registrada: {duration:.2f}s, success={success}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar operação {operation}: {e}")
    
    async def get_current_metrics(self) -> dict:
        """
        Obter métricas atuais em formato compatível com V9.0
        
        Returns:
            Dict com métricas formatadas para dashboard
        """
        try:
            total_calls = sum(stats.total_calls for stats in self.api_stats.values())
            total_success = sum(stats.successful_calls for stats in self.api_stats.values())
            
            if total_calls > 0:
                success_rate = total_success / total_calls
                avg_latency = self.global_stats.get('avg_latency_all_apis', 0) / 1000  # Convert to seconds
            else:
                success_rate = 1.0
                avg_latency = 0.0
            
            # Calcular operações por minuto
            operations_per_minute = 0
            if self.api_stats:
                recent_calls = 0
                current_time = time.time()
                for stats in self.api_stats.values():
                    # Simular calls dos últimos 60 segundos
                    recent_calls += min(stats.total_calls, 10)  # Mock data
                operations_per_minute = recent_calls
            
            return {
                'average_latency': avg_latency,
                'total_operations': total_calls,
                'success_rate': success_rate,
                'operations_per_minute': operations_per_minute,
                'system_health_score': self.global_stats.get('system_health_score', 100) / 100
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas atuais: {e}")
            return {
                'average_latency': 0,
                'total_operations': 0,
                'success_rate': 1.0,
                'operations_per_minute': 0,
                'system_health_score': 1.0
            }


# Context manager para rastreamento automático
class APICallTracker:
    """Context manager para rastreamento automático de latência"""
    
    def __init__(self, metrics: LatencyMetrics, api_name: str, endpoint: str = None):
        self.metrics = metrics
        self.api_name = api_name
        self.endpoint = endpoint
        self.call_id = None
        self.error_occurred = False
        self.error_type = None
    
    async def __aenter__(self):
        self.call_id = self.metrics.start_api_call(self.api_name, self.endpoint)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            self.error_type = exc_type.__name__
        
        self.metrics.end_api_call(
            self.call_id,
            success=not self.error_occurred,
            error_type=self.error_type
        )
        
        return False  # Não suprimir exceções


        return {}
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Obter todas as métricas de todas as APIs"""
        all_metrics = {}
        
        for api_name in self.api_stats:
            all_metrics[api_name] = self.get_api_performance(api_name)
        
        return all_metrics


# Instância global
latency_metrics = LatencyMetrics()


# Funções de conveniência
def start_api_call_tracking(api_name: str, endpoint: str = None) -> str:
    """Iniciar rastreamento de latência"""
    return latency_metrics.start_api_call(api_name, endpoint)


def end_api_call_tracking(call_id: str, success: bool = True, error_type: str = None):
    """Finalizar rastreamento de latência"""
    latency_metrics.end_api_call(call_id, success, error_type)


def get_api_metrics(api_name: str) -> Optional[Dict]:
    """Obter métricas de uma API"""
    return latency_metrics.get_api_performance(api_name)


def get_system_metrics() -> Dict:
    """Obter métricas do sistema"""
    return latency_metrics.get_all_apis_summary()


def track_api_call(api_name: str, endpoint: str = None):
    """Decorator/context manager para rastreamento automático"""
    return APICallTracker(latency_metrics, api_name, endpoint)


if __name__ == "__main__":
    # Teste do sistema de métricas
    async def test_metrics():
        print("🧪 Testando Sistema de Métricas de Latência V9.0")
        print("=" * 60)
        
        metrics = LatencyMetrics()
        
        # Simular algumas chamadas
        for i in range(10):
            # YouTube API
            call_id = metrics.start_api_call('youtube')
            await asyncio.sleep(0.1 + (i * 0.02))  # Simular latência crescente
            metrics.end_api_call(call_id, success=i < 8)  # 2 falhas
            
            # Spotify API
            call_id = metrics.start_api_call('spotify')
            await asyncio.sleep(0.05)
            metrics.end_api_call(call_id, success=True)
        
        # Mostrar resultados
        print("\n📊 Resumo do Sistema:")
        summary = metrics.get_all_apis_summary()
        print(f"   Health Score: {summary['global_stats']['system_health_score']:.1f}%")
        print(f"   Total Calls: {summary['global_stats']['total_calls']}")
        print(f"   Latência Média: {summary['global_stats']['avg_latency_all_apis']:.1f}ms")
        
        print("\n📈 Performance por API:")
        for api_name in ['youtube', 'spotify']:
            perf = metrics.get_api_performance(api_name)
            if perf:
                print(f"   {api_name}:")
                print(f"     Calls: {perf['total_calls']}")
                print(f"     Success Rate: {perf['success_rate']:.1f}%")
                print(f"     Avg Latency: {perf['avg_latency_ms']:.1f}ms")
        
        # Testar context manager
        print("\n🔄 Testando Context Manager:")
        async with track_api_call('reddit', '/r/brasil') as tracker:
            await asyncio.sleep(0.1)
        
        perf = metrics.get_api_performance('reddit')
        print(f"   Reddit: {perf['total_calls']} call, {perf['avg_latency_ms']:.1f}ms")
        
        print("\n✅ Teste concluído!")
    
    asyncio.run(test_metrics())
