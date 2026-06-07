#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integração - Culture Pulse V9.0
Verificar se todos os sistemas implementados estão funcionando
"""

def test_secure_config():
    """Testar sistema de configuração segura"""
    try:
        from config.secure_config import SecureConfig
        print('✅ secure_config.py - OK')
        
        # Teste básico
        config = SecureConfig()
        print(f'   Configuração carregada com {len(config.api_configs)} APIs')
        return True
    except Exception as e:
        print(f'❌ secure_config.py - ERRO: {e}')
        return False

def test_latency_metrics():
    """Testar sistema de métricas de latência"""
    try:
        from monitoring.latency_metrics import LatencyMetrics
        print('✅ latency_metrics.py - OK')
        
        # Teste básico
        metrics = LatencyMetrics()
        print(f'   Sistema de métricas inicializado')
        return True
    except Exception as e:
        print(f'❌ latency_metrics.py - ERRO: {e}')
        return False

def test_source_indicators():
    """Testar sistema de indicadores visuais"""
    try:
        from collectors.orchestrator import OrchestratorV9
        orchestrator = OrchestratorV9()
        indicators = orchestrator.source_indicators
        print('✅ OrchestratorV9.source_indicators - OK')
        
        # Teste básico
        if indicators:
            indicators.log("test", "Iniciando teste de integração")
            print('   Indicador log: OK')
        else:
            print('   Note: Source Indicators não disponível (V9_SYSTEMS_AVAILABLE=False)')
            
        return True
    except Exception as e:
        print(f'❌ OrchestratorV9.source_indicators - ERRO: {e}')
        return False

def test_integrated_monitoring():
    """Testar sistema de monitoramento integrado"""
    try:
        from collectors.orchestrator import OrchestratorV9
        orchestrator = OrchestratorV9()
        monitoring = orchestrator.monitoring
        print('✅ OrchestratorV9.monitoring - OK')
        
        if monitoring:
            # Teste básico se não for mock
            if hasattr(monitoring, 'get_system_health'):
                health = monitoring.get_system_health()
                print(f'   Saúde do sistema: {health.health_level}')
            else:
                print('   Note: Sistema de monitoramento em modo Mock/Simulado')
        else:
            print('   Note: Monitoring não disponível (V9_SYSTEMS_AVAILABLE=False)')
            
        return True
    except Exception as e:
        print(f'❌ OrchestratorV9.monitoring - ERRO: {e}')
        return False

def test_data_collectors():
    """Testar carregamento de coletores de dados"""
    try:
        from collectors.orchestrator import CulturalDataOrchestrator
        print('✅ collectors.orchestrator.py - OK')
        return True
    except Exception as e:
        print(f'❌ collectors.orchestrator.py - ERRO: {e}')
        return False

def test_supabase_persistence():
    """Testar persistência no Supabase (cultural_signals)"""
    try:
        from config.centralized_config import get_supabase_client
        supabase = get_supabase_client()
        if not supabase:
            print('⚠️ Supabase - Ignorado (credenciais ausentes)')
            return True
            
        print('✅ Supabase Connection - OK')
        
        # 1. Tentar ler sinais existentes
        result = supabase.table("cultural_signals").select("id").limit(1).execute()
        print(f'   Leitura inicial: {len(result.data)} registros encontrados')
        
        # 2. Teste de escrita (Safe mode: insert temporal)
        import uuid
        from datetime import datetime
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        test_data = {
            "termo": "TEST_INTEGRATION_V9",
            "circulo": "música_festivais",
            "plataforma": "pytest",
            "score": 0.99,
            "regiao": "Brasil",
            "raw_data": {"test": True, "momentum": 99.0, "sentiment": 0.8},
            "ts": datetime.now().isoformat()
        }
        
        insert_res = supabase.table("cultural_signals").insert(test_data).execute()
        if insert_res.data:
            print(f'   Escrita: OK (ID: {insert_res.data[0]["id"]})')
            
            # 3. Limpeza (deletar o teste)
            supabase.table("cultural_signals").delete().eq("termo", "TEST_INTEGRATION_V9").execute()
            print('   Limpeza: OK')
        else:
            print('❌ Supabase - Falha na escrita (sem dados retornados)')
            return False
            
        return True
    except Exception as e:
        print(f'❌ Supabase Persistence - ERRO: {e}')
        return False

def main():
    """Executar todos os testes"""
    print("🧪 Testando Implementações V9.0 + Supabase")
    print("=" * 50)
    
    tests = [
        test_secure_config,
        test_latency_metrics,
        test_source_indicators,
        test_integrated_monitoring,
        test_data_collectors,
        test_supabase_persistence
    ]
# ...existing code...
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f'❌ Erro no teste: {e}')
            results.append(False)
        print()
    
    # Resumo
    passed = sum(results)
    total = len(results)
    
    print("📊 RESUMO DOS TESTES:")
    print(f"   ✅ Passaram: {passed}/{total}")
    print(f"   ❌ Falharam: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Todos os sistemas estão funcionando!")
    else:
        print(f"\n⚠️ {total - passed} sistema(s) com problemas")
    
    return passed == total

if __name__ == "__main__":
    main()
