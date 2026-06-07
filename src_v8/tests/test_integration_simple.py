#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integração Simplificado - Sistema de Alertas V9.0
Validação final do sistema consolidado

🎯 TESTES BÁSICOS:
- Imports funcionando
- AlertManager operacional
- Criação de alertas
- Interface Streamlit
- API endpoints
"""

import sys
import os
from datetime import datetime
import traceback

def test_basic_imports():
    """Teste 1: Imports básicos"""
    try:
        from alerts import get_alert_manager, AlertType, AlertLevel, AlertFactory
        print("✅ Imports básicos OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_alert_manager():
    """Teste 2: Alert Manager funcionando"""
    try:
        from alerts import get_alert_manager
        manager = get_alert_manager()
        
        # Verificar métodos essenciais
        assert hasattr(manager, 'add_alert'), "Método add_alert não encontrado"
        assert hasattr(manager, 'get_alert_history'), "Método get_alert_history não encontrado"
        assert hasattr(manager, 'get_alert_stats'), "Método get_alert_stats não encontrado"
        assert manager.config is not None, "Config não carregada"
        
        print("✅ AlertManager funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro no AlertManager: {e}")
        return False

def test_alert_creation():
    """Teste 3: Criação de alertas"""
    try:
        from alerts import get_alert_manager, AlertType, AlertLevel, AlertFactory
        
        manager = get_alert_manager()
        
        # Criar alerta usando factory
        alert = AlertFactory.create_system_alert(
            AlertType.SYSTEM_PERFORMANCE,
            "test_component",
            "Teste de integração",
            AlertLevel.INFO
        )
        
        # Adicionar ao manager
        result = manager.add_alert(alert)
        
        print("✅ Criação de alertas OK")
        return True
    except Exception as e:
        print(f"❌ Erro na criação de alertas: {e}")
        return False

def test_streamlit_interface():
    """Teste 4: Interface Streamlit"""
    try:
        from alerts.streamlit_interface import show_alerts_dashboard, AlertsManager
        
        # Verificar se pode instanciar
        alerts_manager = AlertsManager()
        
        print("✅ Interface Streamlit OK")
        return True
    except Exception as e:
        print(f"❌ Erro na interface Streamlit: {e}")
        return False

def test_api_endpoints():
    """Teste 5: API Endpoints"""
    try:
        from alerts.api_endpoints import alerts_router
        
        # Verificar se router tem rotas
        routes = alerts_router.routes
        assert len(routes) > 0, "Nenhuma rota encontrada"
        
        print("✅ API Endpoints OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos API endpoints: {e}")
        return False

def test_config_system():
    """Teste 6: Sistema de configuração"""
    try:
        from alerts.alert_config import get_default_config, AlertConfig
        
        config = get_default_config()
        assert isinstance(config, AlertConfig), "Config inválida"
        
        print("✅ Sistema de configuração OK")
        return True
    except Exception as e:
        print(f"❌ Erro no sistema de configuração: {e}")
        return False

def test_notification_channels():
    """Teste 7: Canais de notificação"""
    try:
        from alerts.notification_channels import NotificationManager, NotificationConfig
        
        config = NotificationConfig()
        manager = NotificationManager(config)
        
        print("✅ Canais de notificação OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos canais de notificação: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🎯 Culture Pulse V9.0 - Teste de Integração Simplificado")
    print("Sistema de Alertas Consolidado")
    print("=" * 60)
    
    tests = [
        ("Imports básicos", test_basic_imports),
        ("Alert Manager", test_alert_manager),
        ("Criação de alertas", test_alert_creation),
        ("Interface Streamlit", test_streamlit_interface),
        ("API Endpoints", test_api_endpoints),
        ("Sistema de configuração", test_config_system),
        ("Canais de notificação", test_notification_channels),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Teste: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"✅ Testes passou: {passed}/{total}")
    print(f"📈 Taxa de sucesso: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Todas as integrações estão operacionais")
        print("🚀 Sistema de alertas consolidado com sucesso!")
    elif percentage >= 80:
        print("\n⚠️ Sistema majoritariamente funcional")
        print("🔧 Algumas correções menores podem ser necessárias")
    else:
        print("\n❌ Sistema precisa de correções")
        print("🔧 Verificar erros acima")
    
    print(f"\n📝 Timestamp: {datetime.now().isoformat()}")
    
    # Mostrar falhas
    failures = [name for name, result in results if not result]
    if failures:
        print(f"\n❌ Testes que falharam:")
        for failure in failures:
            print(f"  - {failure}")
    
    return percentage == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
