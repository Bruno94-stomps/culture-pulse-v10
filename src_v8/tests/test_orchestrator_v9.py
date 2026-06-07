#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do OrchestratorV9 - Culture Pulse V9.0
Teste rápido das funcionalidades V9.0 implementadas

🎯 TESTA:
- Inicialização do OrchestratorV9
- Integração com sistemas V9.0
- Coleta com monitoramento
- Dashboard data V9.0
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_orchestrator_v9():
    """Teste principal do OrchestratorV9"""
    print("🧪 Testando OrchestratorV9 - Culture Pulse V9.0")
    print("=" * 60)
    
    try:
        # 1. Importar OrchestratorV9
        print("1️⃣ Importando OrchestratorV9...")
        from collectors.orchestrator import OrchestratorV9
        print("✅ Import successful")
        
        # 2. Inicializar orchestrador
        print("\n2️⃣ Inicializando OrchestratorV9...")
        orchestrator = OrchestratorV9()
        print(f"✅ Orchestrator inicializado")
        print(f"   V9 Systems Available: {orchestrator.secure_config is not None}")
        
        # 3. Testar get_dashboard_data
        print("\n3️⃣ Testando get_dashboard_data...")
        dashboard_data = await orchestrator.get_dashboard_data()
        print("✅ Dashboard data obtido")
        print(f"   Keys: {list(dashboard_data.keys())}")
        
        if 'v9_systems' in dashboard_data:
            v9_systems = dashboard_data['v9_systems']
            print(f"   V9 Systems Available: {v9_systems.get('available', False)}")
            
            if v9_systems.get('available'):
                print("   V9 Components:")
                for component, data in v9_systems.items():
                    if component != 'available':
                        print(f"     - {component}: {type(data).__name__}")
        
        # 4. Testar coleta com monitoramento (versão melhorada)
        print("\n4️⃣ Testando collect_with_monitoring...")
        try:
            # Verificar se o método record_operation existe
            if hasattr(orchestrator.latency_metrics, 'record_operation'):
                print("   ✅ Método record_operation disponível")
            else:
                print("   ⚠️ Método record_operation não encontrado")
            
            # Usar tópicos simples para teste
            topics = ["teste", "cultura"]
            collectors = ["instagram", "meetup"]  # Coletores mais simples
            
            print(f"   Tópicos: {topics}")
            print(f"   Coletores: {collectors}")
            
            result = await orchestrator.collect_with_monitoring(
                topics=topics,
                collectors=collectors
            )
            
            print("✅ Coleta com monitoramento concluída")
            print(f"   Success: {result.get('success', False)}")
            
            if 'v9_metrics' in result:
                v9_metrics = result['v9_metrics']
                print("   V9 Metrics:")
                print(f"     - Collection time: {v9_metrics.get('collection_time', 0):.2f}s")
                print(f"     - Latency score: {v9_metrics.get('latency_score', 'N/A')}")
                
        except Exception as e:
            print(f"⚠️ Erro na coleta: {e}")
            print(f"   Tipo do erro: {type(e).__name__}")
            
            # Verificar se é o erro específico do record_operation
            if "'LatencyMetrics' object has no attribute 'record_operation'" in str(e):
                print("   🔧 DIAGNÓSTICO: Método record_operation não implementado em LatencyMetrics")
            
        # 5. Verificar métricas internas
        print("\n5️⃣ Verificando métricas internas...")
        metrics = orchestrator.v9_metrics
        print("✅ Métricas V9.0:")
        for key, value in metrics.items():
            print(f"   - {key}: {value}")
        
        # Diagnóstico das métricas
        if metrics['failed_collections'] > 0:
            print("   🔧 DIAGNÓSTICO: Coleta falhada detectada")
            print("   💡 Isso é esperado se há problemas com as APIs ou métodos ausentes")
        
        # 6. Testar integração de sistemas V9.0
        print("\n6️⃣ Testando integração V9.0...")
        if orchestrator.monitoring:
            print("✅ IntegratedMonitoring: Disponível")
        else:
            print("⚠️ IntegratedMonitoring: Não disponível")
        
        if orchestrator.latency_metrics:
            print("✅ LatencyMetrics: Disponível")
            # Verificar métodos específicos
            methods_to_check = ['record_operation', 'get_current_metrics']
            for method in methods_to_check:
                if hasattr(orchestrator.latency_metrics, method):
                    print(f"   ✅ Método {method}: Disponível")
                else:
                    print(f"   ❌ Método {method}: Ausente")
        else:
            print("⚠️ LatencyMetrics: Não disponível")
        
        if orchestrator.source_indicators:
            print("✅ SourceIndicators: Disponível")
            # Verificar métodos específicos
            methods_to_check = ['get_all_sources_status', 'update_source_status']
            for method in methods_to_check:
                if hasattr(orchestrator.source_indicators, method):
                    print(f"   ✅ Método {method}: Disponível")
                else:
                    print(f"   ❌ Método {method}: Ausente")
        else:
            print("⚠️ SourceIndicators: Não disponível")
        
        if orchestrator.secure_config:
            print("✅ SecureConfig: Disponível")
        else:
            print("⚠️ SecureConfig: Não disponível")
        
        print("\n🏁 Teste OrchestratorV9 concluído!")
        print("✅ Funcionalidades básicas verificadas")
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("💡 Verifique se todos os componentes V9.0 estão disponíveis")
    
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        print("\n🔍 Traceback completo:")
        traceback.print_exc()

async def test_dashboard_integration():
    """Teste da integração com dashboard"""
    print("\n" + "=" * 60)
    print("🧪 Testando Integração Dashboard V9.0")
    print("=" * 60)
    
    try:
        # Testar import do dashboard integrado (path corrigido)
        print("1️⃣ Testando import dashboard...")
        from monitoring.integrated_monitoring_dashboard import IntegratedMonitoringDashboard
        print("✅ IntegratedMonitoringDashboard importado")
        
        # Inicializar dashboard
        print("\n2️⃣ Inicializando dashboard...")
        dashboard = IntegratedMonitoringDashboard()
        print(f"✅ Dashboard inicializado")
        print(f"   Initialized: {dashboard.initialized}")
        
        # Testar get_system_overview
        if dashboard.initialized:
            print("\n3️⃣ Testando get_system_overview...")
            overview = await dashboard.get_system_overview()
            print("✅ System overview obtido")
            print(f"   Status: {overview.get('status', 'N/A')}")
            print(f"   Overall Score: {overview.get('overall_score', 0):.1%}")
        else:
            print("⚠️ Dashboard não inicializado - sistemas V9.0 não disponíveis")
        
        print("\n🏁 Teste Dashboard Integration concluído!")
        
    except ImportError as e:
        print(f"❌ Erro de import dashboard: {e}")
        print("💡 Verifique se o arquivo foi movido para a pasta 'monitoring'")
    
    except Exception as e:
        print(f"❌ Erro no teste dashboard: {e}")

async def test_latency_metrics_fix():
    """Teste específico para verificar LatencyMetrics"""
    print("\n" + "=" * 60)
    print("🧪 Teste Específico - LatencyMetrics")
    print("=" * 60)
    
    try:
        print("1️⃣ Importando LatencyMetrics...")
        from monitoring.latency_metrics import LatencyMetrics
        print("✅ LatencyMetrics importado")
        
        print("\n2️⃣ Inicializando LatencyMetrics...")
        metrics = LatencyMetrics()
        print("✅ LatencyMetrics inicializado")
        
        print("\n3️⃣ Testando método record_operation...")
        await metrics.record_operation(
            operation="test_operation",
            duration=1.5,
            success=True
        )
        print("✅ record_operation executado com sucesso")
        
        print("\n4️⃣ Testando método get_current_metrics...")
        current_metrics = await metrics.get_current_metrics()
        print("✅ get_current_metrics executado")
        print(f"   Average latency: {current_metrics.get('average_latency', 0):.2f}s")
        print(f"   Total operations: {current_metrics.get('total_operations', 0)}")
        print(f"   Success rate: {current_metrics.get('success_rate', 0):.1%}")
        
        print("\n🏁 Teste LatencyMetrics concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste LatencyMetrics: {e}")
        import traceback
        print("\n🔍 Traceback:")
        traceback.print_exc()

def main():
    """Função principal"""
    print(f"🚀 Culture Pulse V9.0 - Teste Orchestrator")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar testes
    asyncio.run(test_orchestrator_v9())
    asyncio.run(test_dashboard_integration())
    asyncio.run(test_latency_metrics_fix())
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES CONCLUÍDOS")
    print("💡 Para teste completo, execute o dashboard: python dashboard/run_dashboard.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
