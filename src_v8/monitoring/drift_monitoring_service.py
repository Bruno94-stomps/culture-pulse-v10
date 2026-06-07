#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Drift Monitoring Service
Serviço de monitoramento contínuo para detectar shifts e drifts

Integra:
- ContextDriftDetector (mudança de contexto semântico)
- DistributionShiftDetector (divergência train vs prod)

Features:
- Monitoramento em tempo real
- Alertas automáticos por email/Slack
- Dashboard de métricas
- Histórico persistente

Autor: Culture Pulse V9.1
Data: Fevereiro 2026
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging
import asyncio
from datetime import datetime
import pandas as pd
import numpy as np

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from monitoring.context_drift_detector import ContextDriftDetector, DriftAlert as ContextDriftAlert
from monitoring.distribution_shift_detector import DistributionShiftDetector, ShiftAlert

logger = logging.getLogger(__name__)


class DriftMonitoringService:
    """
    Serviço centralizado de monitoramento de drift e shift
    
    Workflow:
    1. Coleta sinais de produção
    2. Extrai embeddings e features
    3. Detecta context drift (termos mudando sentido)
    4. Detecta distribution shift (dados divergindo do treino)
    5. Envia alertas se necessário
    6. Atualiza dashboard
    """
    
    def __init__(
        self,
        reference_data: Optional[pd.DataFrame] = None,
        context_drift_threshold: float = 0.3,
        distribution_p_threshold: float = 0.05,
        alert_callback: Optional[callable] = None
    ):
        """
        Args:
            reference_data: Dados de referência (treinamento sintético)
            context_drift_threshold: Threshold para context drift (cosine distance)
            distribution_p_threshold: Threshold para distribution shift (p-value)
            alert_callback: Função para enviar alertas (email, Slack, etc)
        """
        # Detectores
        self.context_detector = ContextDriftDetector(
            drift_threshold=context_drift_threshold,
            storage_path="data/context_drift_history.json"
        )
        
        self.distribution_detector = DistributionShiftDetector(
            reference_data=reference_data,
            p_value_threshold=distribution_p_threshold,
            storage_path="data/distribution_shift_history.json"
        )
        
        # Callback para alertas
        self.alert_callback = alert_callback or self._default_alert_handler
        
        # Contadores
        self.signals_processed = 0
        self.context_drifts_detected = 0
        self.distribution_shifts_detected = 0
        
        logger.info("✅ DriftMonitoringService initialized")
    
    async def monitor_signal(
        self,
        signal: Dict,
        embedding: np.ndarray,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Monitora um único sinal cultural
        
        Args:
            signal: Dicionário com dados do sinal (CulturalSignal)
            embedding: BERTimbau embedding (768d ou 776d)
            timestamp: Data/hora do sinal
        
        Returns:
            Dict com resultados da análise
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        termo = signal.get('termo', '')
        context_terms = signal.get('related_terms', [])
        
        results = {
            'termo': termo,
            'timestamp': timestamp.isoformat(),
            'context_drift_detected': False,
            'distribution_shift_detected': False,
            'alerts': []
        }
        
        # 1. Adicionar observação de contexto
        try:
            self.context_detector.add_observation(
                term=termo,
                embedding=embedding,
                context_terms=context_terms,
                timestamp=timestamp
            )
        except Exception as e:
            logger.error(f"Error adding context observation: {e}")
        
        # 2. Detectar context drift
        try:
            context_alert = self.context_detector.detect_drift(
                term=termo,
                current_embedding=embedding,
                current_context=context_terms,
                timestamp=timestamp
            )
            
            if context_alert:
                results['context_drift_detected'] = True
                results['context_drift'] = {
                    'drift_score': context_alert.drift_score,
                    'severity': context_alert.severity,
                    'recommendation': context_alert.recommendation
                }
                results['alerts'].append(context_alert)
                self.context_drifts_detected += 1
                
                # Enviar alerta
                await self._send_alert('context_drift', context_alert)
        
        except Exception as e:
            logger.error(f"Error detecting context drift: {e}")
        
        # 3. Adicionar sample de produção para distribution shift
        try:
            if 'features' in signal:
                signal_series = pd.Series(signal['features'])
                self.distribution_detector.add_production_sample(signal_series)
        except Exception as e:
            logger.error(f"Error adding production sample: {e}")
        
        self.signals_processed += 1
        
        return results
    
    async def check_distribution_shifts(
        self,
        production_data: pd.DataFrame,
        features_to_check: Optional[List[str]] = None
    ) -> List[ShiftAlert]:
        """
        Verifica distribution shifts em batch
        
        Args:
            production_data: Últimas N amostras de produção
            features_to_check: Features específicas (None = todas)
        
        Returns:
            Lista de ShiftAlerts detectados
        """
        try:
            alerts = self.distribution_detector.detect_shift(
                production_data,
                features=features_to_check
            )
            
            if alerts:
                self.distribution_shifts_detected += len(alerts)
                
                # Enviar alertas
                for alert in alerts:
                    await self._send_alert('distribution_shift', alert)
            
            return alerts
        
        except Exception as e:
            logger.error(f"Error checking distribution shifts: {e}")
            return []
    
    def get_monitoring_summary(self) -> Dict:
        """
        Retorna resumo do monitoramento
        
        Útil para dashboard
        """
        # Context drifts (últimos 30 dias)
        context_summary = self.context_detector.get_drift_summary(days=30)
        
        # Distribution shifts (últimos 30 dias)
        dist_summary = self.distribution_detector.get_shift_summary(days=30)
        
        return {
            'signals_processed': self.signals_processed,
            'context_drifts_total': self.context_drifts_detected,
            'distribution_shifts_total': self.distribution_shifts_detected,
            'context_drift_summary': context_summary,
            'distribution_shift_summary': dist_summary,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_top_drifted_terms(self, limit: int = 10) -> List[Dict]:
        """
        Retorna top termos com maior drift
        
        Args:
            limit: Número de termos a retornar
        
        Returns:
            Lista de {term, drift_score, severity}
        """
        context_summary = self.context_detector.get_drift_summary(days=30)
        top_terms = context_summary.get('top_drifted_terms', [])
        
        return top_terms[:limit]
    
    def get_top_shifted_features(self, limit: int = 10) -> List[Dict]:
        """
        Retorna top features com maior shift
        
        Args:
            limit: Número de features a retornar
        
        Returns:
            Lista de {feature, ks_statistic}
        """
        dist_summary = self.distribution_detector.get_shift_summary(days=30)
        top_features = dist_summary.get('top_shifted_features', [])
        
        return top_features[:limit]
    
    def requires_model_retrain(self) -> bool:
        """
        Verifica se sistema requer retreino de modelos
        
        Critérios:
        - 3+ context drifts críticos nos últimos 7 dias
        - 5+ distribution shifts severos nos últimos 7 dias
        - Average KS statistic > 0.4
        """
        # Context drifts (7 dias)
        context_summary = self.context_detector.get_drift_summary(days=7)
        critical_context_drifts = context_summary.get('drifts_by_severity', {}).get('critical', 0)
        
        # Distribution shifts (7 dias)
        dist_summary = self.distribution_detector.get_shift_summary(days=7)
        severe_shifts = dist_summary.get('shifts_by_magnitude', {}).get('severe', 0)
        critical_shifts = dist_summary.get('shifts_by_magnitude', {}).get('critical', 0)
        avg_ks = dist_summary.get('average_ks_statistic', 0.0)
        
        # Critérios
        if critical_context_drifts >= 3:
            logger.warning(f"🚨 RETRAIN REQUIRED: {critical_context_drifts} critical context drifts")
            return True
        
        if (severe_shifts + critical_shifts) >= 5:
            logger.warning(f"🚨 RETRAIN REQUIRED: {severe_shifts + critical_shifts} severe distribution shifts")
            return True
        
        if avg_ks > 0.4:
            logger.warning(f"🚨 RETRAIN REQUIRED: Average KS statistic {avg_ks:.3f} > 0.4")
            return True
        
        return False
    
    async def _send_alert(self, alert_type: str, alert):
        """Envia alerta usando callback"""
        try:
            await self.alert_callback(alert_type, alert)
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def _default_alert_handler(self, alert_type: str, alert):
        """Handler padrão de alertas (logging)"""
        if alert_type == 'context_drift':
            logger.warning(
                f"🌊 CONTEXT DRIFT: {alert.term} "
                f"(score={alert.drift_score:.3f}, severity={alert.severity})"
            )
        elif alert_type == 'distribution_shift':
            logger.warning(
                f"📊 DISTRIBUTION SHIFT: {alert.feature_name} "
                f"(KS={alert.ks_statistic:.3f}, magnitude={alert.shift_magnitude})"
            )


# Funções auxiliares para integração

async def monitor_signals_batch(
    service: DriftMonitoringService,
    signals: List[Dict],
    embeddings: List[np.ndarray]
) -> Dict:
    """
    Monitora batch de sinais
    
    Args:
        service: DriftMonitoringService instance
        signals: Lista de sinais culturais
        embeddings: Lista de embeddings correspondentes
    
    Returns:
        Summary de resultados
    """
    results = []
    
    for signal, embedding in zip(signals, embeddings):
        result = await service.monitor_signal(signal, embedding)
        results.append(result)
    
    # Resumo
    context_drifts = sum(1 for r in results if r['context_drift_detected'])
    
    return {
        'total_signals': len(results),
        'context_drifts_detected': context_drifts,
        'results': results
    }


def create_monitoring_service(
    reference_data_path: Optional[str] = None
) -> DriftMonitoringService:
    """
    Factory function para criar serviço de monitoramento
    
    Args:
        reference_data_path: Caminho para dados de referência (CSV/parquet)
    
    Returns:
        DriftMonitoringService configurado
    """
    reference_data = None
    
    if reference_data_path:
        try:
            if reference_data_path.endswith('.csv'):
                reference_data = pd.read_csv(reference_data_path)
            elif reference_data_path.endswith('.parquet'):
                reference_data = pd.read_parquet(reference_data_path)
            
            logger.info(f"✅ Reference data loaded: {reference_data.shape}")
        
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
    
    return DriftMonitoringService(reference_data=reference_data)


# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    
    # Criar serviço
    service = create_monitoring_service()
    
    # Simular monitoramento de sinais
    async def test_monitoring():
        # Sinal de teste
        test_signal = {
            'termo': 'sustentabilidade',
            'related_terms': ['meio ambiente', 'ESG', 'verde', 'clima'],
            'plataforma': 'YouTube',
            'momentum': 75.5,
            'features': {
                'momentum': 75.5,
                'sentiment': 0.85,
                'volume': 1250
            }
        }
        
        # Embedding simulado (em produção viria do BERTimbau)
        test_embedding = np.random.randn(768)
        
        # Monitorar
        result = await service.monitor_signal(
            test_signal,
            test_embedding,
            timestamp=datetime.now()
        )
        
        print("\n" + "="*70)
        print("MONITORING RESULT")
        print("="*70)
        print(f"Termo: {result['termo']}")
        print(f"Context drift detected: {result['context_drift_detected']}")
        print(f"Distribution shift detected: {result['distribution_shift_detected']}")
        
        # Resumo geral
        summary = service.get_monitoring_summary()
        print("\n" + "="*70)
        print("MONITORING SUMMARY")
        print("="*70)
        print(f"Signals processed: {summary['signals_processed']}")
        print(f"Context drifts: {summary['context_drifts_total']}")
        print(f"Distribution shifts: {summary['distribution_shifts_total']}")
        
        # Verificar se requer retreino
        needs_retrain = service.requires_model_retrain()
        print(f"\nRequires model retrain: {needs_retrain}")
    
    # Executar teste
    asyncio.run(test_monitoring())
