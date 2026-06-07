#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Culture Pulse V9.0 - Advanced System Launcher
Sistema inteligente de inicialização com validação de integração

🚀 FUNCIONALIDADES:
- Validação automática da integração
- Inicialização do ML Foundation
- Dashboard integrado
- Monitoramento de componentes

🎯 EXECUTAR:
python start_system.py
"""

import subprocess
import time
import os
import sys
from pathlib import Path
import json

def validate_system_integration():
    """Validar integração do sistema antes de iniciar"""
    print("🔍 VALIDANDO INTEGRAÇÃO DO SISTEMA...")
    
    try:
        # Executar o integration_validator
        from api.integration_validator import IntegrationValidator
        validator = IntegrationValidator()
        
        # Validação rápida dos componentes críticos
        critical_components = [
            "config.centralized_config",
            "autonomous_agent.research_refiner", 
            "dashboard.cultural_dashboard_integrated"
        ]
        
        missing_critical = []
        for component in critical_components:
            try:
                if component == "config.centralized_config":
                    from config.centralized_config import config
                    print(f"  ✅ {component}")
                elif component == "autonomous_agent.research_refiner":
                    from core.Abas.analise_cultural_completa.research_refiner import ResearchRefiner
                    print(f"  ✅ {component}")
                elif component == "dashboard.cultural_dashboard_integrated":
                    # Apenas verificar se o arquivo existe
                    dashboard_path = Path("dashboard/cultural_dashboard_integrated.py")
                    if dashboard_path.exists():
                        print(f"  ✅ {component}")
                    else:
                        print(f"  ❌ {component}")
                        missing_critical.append(component)
                else:
                    __import__(component)
                    print(f"  ✅ {component}")
            except ImportError:
                print(f"  ❌ {component}")
                missing_critical.append(component)
        
        if missing_critical:
            print(f"\\n⚠️ COMPONENTES CRÍTICOS AUSENTES: {len(missing_critical)}")
            for comp in missing_critical:
                print(f"    - {comp}")
            print("\\n🔧 RECOMENDAÇÃO: Execute 'python integration_validator.py' para diagnóstico completo")
            return False
        else:
            print("\\n✅ TODOS OS COMPONENTES CRÍTICOS DISPONÍVEIS")
            return True
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def initialize_ml_foundation():
    """Inicializar ML Foundation se disponível"""
    print("\\n🤖 INICIALIZANDO ML FOUNDATION...")
    
    try:
        from core.Abas.analise_cultural_completa.research_refiner import ResearchRefiner
        refiner = ResearchRefiner()
        
        if refiner.ml_integrator:
            print("  ✅ ML Integrator disponível")
            if refiner.ml_integrator.is_initialized:
                print("  ✅ ML Foundation já inicializado")
            else:
                print("  🔄 Inicializando componentes ML...")
                refiner.ml_integrator._initialize_components()
                print(f"  ✅ ML Foundation inicializado: {refiner.ml_integrator.is_initialized}")
        else:
            print("  ⚠️ ML Integrator não disponível (verificando ml_integrator_simple...)")
            try:
                from autonomous_agent.ml_foundation.ml_integrator_simple import MLIntegratorSimple
                simple_ml = MLIntegratorSimple()
                results = simple_ml._initialize_components()
                print(f"  ✅ ML Integrator Simple carregado: {sum(results.values())}/4 componentes")
            except ImportError as e:
                print(f"  ❌ ML Integrator Simple também não disponível: {e}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização ML: {e}")
        return False

def check_environment():
    """Verificar ambiente e configurações"""
    print("\\n🌍 VERIFICANDO AMBIENTE...")
    
    # Verificar .env
    env_path = Path(".env")
    if env_path.exists():
        print("  ✅ Arquivo .env encontrado")
    else:
        print("  ⚠️ Arquivo .env não encontrado")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"  ✅ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"  ❌ Python {python_version.major}.{python_version.minor} (requer 3.8+)")
        return False
    
    # Verificar dependências críticas
    critical_packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n❌ PACOTES AUSENTES: {missing_packages}")
        print("🔧 Execute: pip install -r requirements.txt")
        return False
    
    return True

def start_dashboard():
    """Iniciar dashboard Streamlit"""
    print("\\n🎨 INICIANDO DASHBOARD STREAMLIT...")
    
    dashboard_path = "dashboard/cultural_dashboard_integrated.py"
    
    if not Path(dashboard_path).exists():
        print(f"❌ Dashboard não encontrado: {dashboard_path}")
        return False
    
    print("🌐 Dashboard será aberto em: http://localhost:8501")
    print("💡 Para parar o sistema: Ctrl+C")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "dark"
        ])
        return True
        
    except KeyboardInterrupt:
        print("\\n\\n🛑 Parando sistema...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
        return False

def main():
    """Função principal do launcher"""
    print("🧠 CULTURE PULSE V9.0 - INTELLIGENT SYSTEM LAUNCHER")
    print("=" * 70)
    
    # Verificar diretório
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    print(f"📂 Diretório: {current_dir}")
    
    # 1. Verificar ambiente
    if not check_environment():
        print("\\n❌ FALHA NA VERIFICAÇÃO DO AMBIENTE")
        return 1
    
    # 2. Validar integração
    if not validate_system_integration():
        print("\\n❌ FALHA NA VALIDAÇÃO DA INTEGRAÇÃO")
        print("🔧 RECOMENDAÇÃO: Execute diagnóstico completo:")
        print("   python integration_validator.py")
        return 1
    
    # 3. Inicializar ML Foundation
    ml_success = initialize_ml_foundation()
    if ml_success:
        print("✅ Sistema de IA pronto")
    else:
        print("⚠️ Sistema funcionará em modo básico")
    
    # 4. Iniciar dashboard
    print("\\n" + "=" * 70)
    print("🎯 SISTEMA CULTURE PULSE V9.0 INICIADO!")
    print("🎨 Dashboard: http://localhost:8501")
    if ml_success:
        print("🤖 IA: ML Foundation + GitHub Models ativo")
    else:
        print("🤖 IA: Modo básico")
    print("=" * 70)
    
    success = start_dashboard()
    
    if success:
        print("✅ Sistema finalizado com sucesso!")
        return 0
    else:
        print("❌ Erro durante execução")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
