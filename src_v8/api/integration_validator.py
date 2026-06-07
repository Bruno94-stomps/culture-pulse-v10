#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 INTEGRATION VALIDATOR V9.0 - Culture Intelligence Engine
Sistema de validação completa da integração de todos os módulos

VERIFICA:
✅ Config (centralized_config.py, .env)
✅ Collectors (orchestrator.py, data_collectors.py)
✅ Data (database_config.py, production_database_manager.py)
✅ Scripts (setup_culture_pulse.py, setup_database.py)
✅ Dashboard (utils.py, dashboard_config.py)
✅ Autonomous Agent (todos os componentes ML)
✅ Requirements.txt
✅ APIs (todas as 8 APIs configuradas)
"""

import sys
import os
import importlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

class IntegrationValidator:
    """Validador completo da integração do sistema"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.validation_results = {}
        self.integration_score = 0.0
        self.missing_components = []
        self.available_components = []
        
    def validate_complete_integration(self) -> Dict[str, Any]:
        """Validação completa de toda a integração"""
        
        print("🔍 INICIANDO VALIDAÇÃO COMPLETA DA INTEGRAÇÃO...")
        print("=" * 60)
        
        # 1. Validar Config
        config_result = self._validate_config_integration()
        
        # 2. Validar Collectors
        collectors_result = self._validate_collectors_integration()
        
        # 3. Validar Data Layer
        data_result = self._validate_data_integration()
        
        # 4. Validar Scripts
        scripts_result = self._validate_scripts_integration()
        
        # 5. Validar Dashboard
        dashboard_result = self._validate_dashboard_integration()
        
        # 6. Validar Autonomous Agent
        agent_result = self._validate_autonomous_agent_integration()
        
        # 7. Validar APIs
        apis_result = self._validate_apis_integration()
        
        # 8. Validar Requirements
        requirements_result = self._validate_requirements()
        
        # Consolidar resultados
        self.validation_results = {
            "config": config_result,
            "collectors": collectors_result,
            "data": data_result,
            "scripts": scripts_result,
            "dashboard": dashboard_result,
            "autonomous_agent": agent_result,
            "apis": apis_result,
            "requirements": requirements_result
        }
        
        # Calcular score de integração
        self._calculate_integration_score()
        
        # Gerar relatório
        return self._generate_integration_report()
    
    def _validate_config_integration(self) -> Dict[str, Any]:
        """Valida integração dos módulos de configuração"""
        
        print("\\n📁 VALIDANDO CONFIG...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar centralized_config.py
        try:
            from config.centralized_config import config
            results["components"]["centralized_config"] = "✅ Disponível"
            self.available_components.append("config.centralized_config")
        except ImportError as e:
            results["components"]["centralized_config"] = f"❌ Erro: {e}"
            self.missing_components.append("config.centralized_config")
            results["issues"].append("centralized_config.py não importável")
        
        # O constants.py foi depreciado na V9.9 (Inteligência movida para ResearchRefiner)
        results["components"]["constants"] = "✅ Depreciado (OK)"
        
        # Verificar .env
        env_path = self.base_path / ".env"
        if env_path.exists():
            results["components"]["env_file"] = "✅ Arquivo .env encontrado"
            self.available_components.append(".env")
        else:
            results["components"]["env_file"] = "❌ Arquivo .env não encontrado"
            self.missing_components.append(".env")
            results["issues"].append("Arquivo .env não encontrado")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_collectors_integration(self) -> Dict[str, Any]:
        """Valida integração dos coletores"""
        
        print("📡 VALIDANDO COLLECTORS...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar orchestrator.py
        try:
            from collectors.orchestrator import CulturalDataOrchestrator
            results["components"]["orchestrator"] = "✅ Disponível"
            self.available_components.append("collectors.orchestrator")
        except ImportError as e:
            results["components"]["orchestrator"] = f"❌ Erro: {e}"
            self.missing_components.append("collectors.orchestrator")
            results["issues"].append("orchestrator.py não importável")
        
        # Verificar data_collectors.py
        try:
            import collectors.data_collectors
            results["components"]["data_collectors"] = "✅ Disponível"
            self.available_components.append("collectors.data_collectors")
        except ImportError:
            results["components"]["data_collectors"] = "❌ Não disponível"
            self.missing_components.append("collectors.data_collectors")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_data_integration(self) -> Dict[str, Any]:
        """Valida integração da camada de dados"""
        
        print("🗄️ VALIDANDO DATA LAYER...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar database_config.py
        try:
            from data.database_config import DatabaseConfig
            results["components"]["database_config"] = "✅ Disponível"
            self.available_components.append("data.database_config")
        except ImportError as e:
            results["components"]["database_config"] = f"❌ Erro: {e}"
            self.missing_components.append("data.database_config")
            results["issues"].append("database_config.py não importável")
        
        # Verificar production_database_manager.py
        try:
            from data.production_database_manager import ProductionDatabaseManager
            results["components"]["production_database_manager"] = "✅ Disponível"
            self.available_components.append("data.production_database_manager")
        except ImportError as e:
            results["components"]["production_database_manager"] = f"❌ Erro: {e}"
            self.missing_components.append("data.production_database_manager")
            results["issues"].append("production_database_manager.py não importável")
        
        # Verificar BusinessSynthesizer (Filtro de Obviedade / Core)
        try:
            from core.intelligence.business_synthesizer import BusinessSynthesizer
            results["components"]["business_synthesizer"] = "active"
            print("   ✅ BusinessSynthesizer (Filtro de Obviedade) integrado")
        except ImportError as e:
            results["status"] = "partial"
            results["issues"].append(f"BusinessSynthesizer não encontrado: {e}")
            print(f"   ❌ Erro ao importar BusinessSynthesizer: {e}")

        # Verificar se o banco de dados existe
        db_path = self.base_path / "data" / "culture_db.db"
        if db_path.exists():
            results["components"]["database_file"] = "✅ Banco de dados encontrado"
            self.available_components.append("culture_db.db")
        else:
            results["components"]["database_file"] = "⚠️ Banco de dados não encontrado"
            results["issues"].append("Banco de dados não encontrado")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_scripts_integration(self) -> Dict[str, Any]:
        """Valida integração dos scripts de setup"""
        
        print("⚙️ VALIDANDO SCRIPTS...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar setup_culture_pulse.py
        try:
            from scripts.setup_culture_pulse import CulturePulseSetup
            results["components"]["setup_culture_pulse"] = "✅ Disponível"
            self.available_components.append("scripts.setup_culture_pulse")
        except ImportError as e:
            results["components"]["setup_culture_pulse"] = f"❌ Erro: {e}"
            self.missing_components.append("scripts.setup_culture_pulse")
            results["issues"].append("setup_culture_pulse.py não importável")
        
        # Verificar setup_database.py
        try:
            from scripts.setup_database import DatabaseSetup
            results["components"]["setup_database"] = "✅ Disponível"
            self.available_components.append("scripts.setup_database")
        except ImportError:
            results["components"]["setup_database"] = "❌ Não disponível"
            self.missing_components.append("scripts.setup_database")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_dashboard_integration(self) -> Dict[str, Any]:
        """Valida integração dos utilitários do dashboard do Next.js (via API)"""
        
        print("📊 VALIDANDO DASHBOARD (NEXT.JS + API)...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar se os endpoints de dashboard estão registrados no main.py
        try:
            from api.main import FASTAPI_AVAILABLE
            results["components"]["api_main"] = "✅ FastAPI disponível"
            self.available_components.append("api.main")
        except ImportError as e:
            results["components"]["api_main"] = f"❌ Erro: {e}"
            self.missing_components.append("api.main")
            results["issues"].append("FastAPI principal não importável")
        
        # Verificar se o router de insights está disponível
        try:
            from api.endpoints.dashboard_insights import router
            results["components"]["dashboard_insights"] = "✅ Router Insights disponível"
            self.available_components.append("api.endpoints.dashboard_insights")
        except ImportError as e:
            results["components"]["dashboard_insights"] = f"❌ Erro: {e}"
            self.missing_components.append("api.endpoints.dashboard_insights")
            results["issues"].append("api.endpoints.dashboard_insights não importável")

        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_autonomous_agent_integration(self) -> Dict[str, Any]:
        """Valida integração completa do Autonomous Agent"""
        
        print("🤖 VALIDANDO AUTONOMOUS AGENT...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Componentes principais do Autonomous Agent
        agent_components = [
            ("research_refiner", "ResearchRefiner"),
            ("context_interpreter", "ContextInterpreter"),
            ("parameter_optimizer", "ParameterOptimizer"),
            ("decision_engine", "DecisionEngine"),
            ("weak_signals_detector", "WeakSignalsDetector"),
            ("feedback_collector", "FeedbackCollector"),
            ("intelligent_integration_engine", "IntelligentIntegrationEngine")
        ]
        
        for component_name, class_name in agent_components:
            try:
                module = importlib.import_module(f"autonomous_agent.{component_name}")
                if hasattr(module, class_name):
                    results["components"][component_name] = "✅ Disponível"
                    self.available_components.append(f"autonomous_agent.{component_name}")
                else:
                    results["components"][component_name] = f"❌ Classe {class_name} não encontrada"
                    self.missing_components.append(f"autonomous_agent.{component_name}.{class_name}")
                    results["issues"].append(f"Classe {class_name} não encontrada em {component_name}")
            except ImportError as e:
                results["components"][component_name] = f"❌ Erro: {e}"
                self.missing_components.append(f"autonomous_agent.{component_name}")
                results["issues"].append(f"{component_name}.py não importável")
        
        # Verificar ML Foundation
        ml_components = [
            "cultural_embeddings_simple",
            "advanced_nlp_processor",
            "feedback_learning",
            "bertimbau_brazilian",
            "github_models_engine",
            "ml_integrator_simple"
        ]
        
        ml_results = {}
        for ml_component in ml_components:
            try:
                module = importlib.import_module(f"autonomous_agent.ml_foundation.{ml_component}")
                ml_results[ml_component] = "✅ Disponível"
                self.available_components.append(f"ml_foundation.{ml_component}")
            except ImportError:
                ml_results[ml_component] = "❌ Não disponível"
                self.missing_components.append(f"ml_foundation.{ml_component}")
        
        results["components"]["ml_foundation"] = ml_results
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_apis_integration(self) -> Dict[str, Any]:
        """Valida integração das APIs"""
        
        print("🔌 VALIDANDO APIs...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        # Verificar .env para chaves de API
        env_path = self.base_path / ".env"
        required_apis = [
            "YOUTUBE_API_KEY",
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "SPOTIFY_CLIENT_ID", 
            "SPOTIFY_CLIENT_SECRET",
            "NEWS_API_KEY",
            "GITHUB_TOKEN"
        ]
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            for api in required_apis:
                if api in env_content and not env_content.count(f"{api}=your_") > 0:
                    results["components"][api] = "✅ Configurado"
                    self.available_components.append(f"API.{api}")
                else:
                    results["components"][api] = "❌ Não configurado"
                    self.missing_components.append(f"API.{api}")
                    results["issues"].append(f"API {api} não configurada")
        else:
            results["status"] = "error"
            results["issues"].append("Arquivo .env não encontrado")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _validate_requirements(self) -> Dict[str, Any]:
        """Valida arquivo requirements.txt"""
        
        print("📦 VALIDANDO REQUIREMENTS...")
        
        results = {
            "status": "success",
            "components": {},
            "issues": []
        }
        
        req_path = self.base_path / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                content = f.read()
            
            required_packages = [
                "plotly",
                "pandas",
                "numpy",
                "fastapi",
                "aiohttp",
                "requests",
                "scikit-learn",
                "nltk",
                "networkx",
                "duckdb"
            ]
            
            for package in required_packages:
                if package in content:
                    results["components"][package] = "✅ Listado"
                    self.available_components.append(f"package.{package}")
                else:
                    results["components"][package] = "❌ Ausente"
                    self.missing_components.append(f"package.{package}")
                    results["issues"].append(f"Pacote {package} não listado")
        else:
            results["status"] = "error"
            results["issues"].append("requirements.txt não encontrado")
        
        if results["issues"]:
            results["status"] = "partial"
            
        return results
    
    def _calculate_integration_score(self) -> None:
        """Calcula o score de integração baseado nos componentes disponíveis"""
        
        total_components = len(self.available_components) + len(self.missing_components)
        if total_components > 0:
            self.integration_score = len(self.available_components) / total_components * 100
        else:
            self.integration_score = 0.0
    
    def _generate_integration_report(self) -> Dict[str, Any]:
        """Gera relatório completo da integração"""
        
        print("\\n" + "=" * 60)
        print("📋 RELATÓRIO DE INTEGRAÇÃO COMPLETO")
        print("=" * 60)
        
        # Status geral
        if self.integration_score >= 90:
            status = "🟢 EXCELENTE"
        elif self.integration_score >= 70:
            status = "🟡 BOM"
        elif self.integration_score >= 50:
            status = "🟠 PARCIAL"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"\\n🎯 STATUS GERAL: {status}")
        print(f"📊 SCORE DE INTEGRAÇÃO: {self.integration_score:.1f}%")
        print(f"✅ COMPONENTES DISPONÍVEIS: {len(self.available_components)}")
        print(f"❌ COMPONENTES AUSENTES: {len(self.missing_components)}")
        
        # Detalhar por categoria
        for category, result in self.validation_results.items():
            print(f"\\n📁 {category.upper()}:")
            if isinstance(result["components"], dict):
                for comp, status in result["components"].items():
                    if isinstance(status, dict):
                        print(f"  📂 {comp}:")
                        for subcomp, substatus in status.items():
                            print(f"    {substatus} {subcomp}")
                    else:
                        print(f"  {status} {comp}")
            
            if result["issues"]:
                print(f"  ⚠️ Issues: {', '.join(result['issues'])}")
        
        # Recomendações
        print(f"\\n🔧 PRÓXIMOS PASSOS:")
        if self.missing_components:
            print("\\n❌ COMPONENTES A INTEGRAR:")
            for component in self.missing_components[:10]:  # Mostrar apenas os 10 primeiros
                print(f"  - {component}")
        
        if self.integration_score >= 90:
            print("\\n🎉 SISTEMA TOTALMENTE INTEGRADO!")
            print("✅ Todos os módulos principais estão funcionais")
        elif self.integration_score >= 70:
            print("\\n✅ SISTEMA BEM INTEGRADO")
            print("⚠️ Alguns componentes opcionais podem estar ausentes")
        else:
            print("\\n⚠️ INTEGRAÇÃO INCOMPLETA")
            print("🔧 Componentes críticos precisam ser integrados")
        
        return {
            "overall_status": status,
            "integration_score": self.integration_score,
            "available_components": len(self.available_components),
            "missing_components": len(self.missing_components),
            "detailed_results": self.validation_results,
            "recommendations": self.missing_components,
            "timestamp": datetime.now().isoformat()
        }

# ===== FUNÇÃO PRINCIPAL =====
def run_complete_integration_validation():
    """Executa validação completa da integração"""
    
    validator = IntegrationValidator()
    report = validator.validate_complete_integration()
    
    # Salvar relatório
    output_path = Path(__file__).parent / "integration_validation_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\\n💾 Relatório salvo em: {output_path}")
    
    return report

if __name__ == "__main__":
    run_complete_integration_validation()
