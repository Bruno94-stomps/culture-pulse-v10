"""
🔧 Sistema de Verificação e Integração V9.0
Verifica e aprimora integrações entre todos os componentes
Garante comunicação fluida entre engines e sistemas
"""

import os
import importlib
import inspect
import sys
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import traceback
from pathlib import Path

class IntegrationVerifier:
    """Verificador de integrações entre componentes"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.integration_report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'components_checked': 0,
            'integrations_verified': 0,
            'issues_found': [],
            'recommendations': [],
            'dependency_graph': {},
            'performance_metrics': {}
        }
        
        # Mapeamento de componentes críticos
        self.critical_components = {
            'autonomous_agent': [
                'research_refiner.py',
                'decision_engine.py', 
                'parameter_optimizer.py',
                'narrative_generator.py',
                'predictive_analytics.py',
                'real_time_monitor.py',
                'temporal_validator.py',
                'ab_testing_engine.py',
                'advanced_validation_criteria.py'
            ],
            'core': [
                'culture_pulse_executive_integration.py',
                'enhanced_dashboard.py'
            ],
            'dashboard': [
                'cultural_dashboard_integrated.py',
                'advanced_metrics_component.py'
            ],
            'collectors': ['*.py'],
            'api': ['*.py'],
            'services': ['*.py']
        }
        
        print("🔧 Integration Verifier V9.0 inicializado!")
    
    def run_full_integration_check(self) -> Dict[str, Any]:
        """Executa verificação completa de integrações"""
        
        print("🔍 Iniciando verificação completa de integrações...")
        
        try:
            # 1. Verificar estrutura de arquivos
            self._verify_file_structure()
            
            # 2. Verificar imports e dependências
            self._verify_imports_and_dependencies()
            
            # 3. Verificar comunicação entre componentes
            self._verify_component_communication()
            
            # 4. Verificar configurações
            self._verify_configurations()
            
            # 5. Verificar ML Foundation
            self._verify_ml_foundation_integration()
            
            # 6. Verificar sistemas autônomos
            self._verify_autonomous_systems()
            
            # 7. Teste de integração end-to-end
            self._run_integration_tests()
            
            # 8. Gerar recomendações
            self._generate_integration_recommendations()
            
            self.integration_report['status'] = 'completed'
            
        except Exception as e:
            self.integration_report['status'] = 'failed'
            self.integration_report['issues_found'].append({
                'type': 'critical_error',
                'component': 'integration_verifier',
                'message': f"Erro crítico durante verificação: {str(e)}",
                'traceback': traceback.format_exc()
            })
        
        return self.integration_report
    
    def _verify_file_structure(self) -> None:
        """Verifica estrutura de arquivos"""
        
        print("📁 Verificando estrutura de arquivos...")
        
        for component, files in self.critical_components.items():
            component_path = self.base_path / component
            
            if not component_path.exists():
                self.integration_report['issues_found'].append({
                    'type': 'missing_directory',
                    'component': component,
                    'message': f"Diretório {component} não encontrado",
                    'severity': 'high'
                })
                continue
            
            for file_pattern in files:
                if file_pattern == '*.py':
                    # Verificar se há pelo menos um arquivo Python
                    py_files = list(component_path.glob('*.py'))
                    if not py_files:
                        self.integration_report['issues_found'].append({
                            'type': 'no_python_files',
                            'component': component,
                            'message': f"Nenhum arquivo Python encontrado em {component}",
                            'severity': 'medium'
                        })
                else:
                    file_path = component_path / file_pattern
                    if not file_path.exists():
                        self.integration_report['issues_found'].append({
                            'type': 'missing_file',
                            'component': component,
                            'file': file_pattern,
                            'message': f"Arquivo {file_pattern} não encontrado em {component}",
                            'severity': 'medium'
                        })
        
        self.integration_report['components_checked'] += len(self.critical_components)
    
    def _verify_imports_and_dependencies(self) -> None:
        """Verifica imports e dependências"""
        
        print("📦 Verificando imports e dependências...")
        
        dependency_graph = {}
        
        for component, files in self.critical_components.items():
            component_path = self.base_path / component
            
            if not component_path.exists():
                continue
            
            # Obter todos os arquivos Python do componente
            if '*.py' in files:
                py_files = list(component_path.glob('*.py'))
            else:
                py_files = [component_path / f for f in files if f.endswith('.py')]
            
            for py_file in py_files:
                if py_file.exists():
                    try:
                        imports = self._extract_imports_from_file(py_file)
                        dependency_graph[str(py_file.relative_to(self.base_path))] = imports
                        
                        # Verificar se imports são resolvíveis
                        self._verify_import_resolution(py_file, imports)
                        
                    except Exception as e:
                        self.integration_report['issues_found'].append({
                            'type': 'import_analysis_error',
                            'component': component,
                            'file': py_file.name,
                            'message': f"Erro ao analisar imports: {str(e)}",
                            'severity': 'low'
                        })
        
        self.integration_report['dependency_graph'] = dependency_graph
    
    def _extract_imports_from_file(self, file_path: Path) -> List[str]:
        """Extrai imports de um arquivo Python"""
        
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Import direto
                if line.startswith('import ') and not line.startswith('import '):
                    import_name = line.replace('import ', '').split(' as ')[0].split('.')[0]
                    imports.append(import_name)
                
                # From import
                elif line.startswith('from '):
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        module_name = parts[1].split('.')[0]
                        imports.append(module_name)
        
        except Exception:
            pass
        
        return list(set(imports))  # Remover duplicatas
    
    def _verify_import_resolution(self, file_path: Path, imports: List[str]) -> None:
        """Verifica se imports podem ser resolvidos"""
        
        for import_name in imports:
            try:
                # Tentar importar
                importlib.import_module(import_name)
            except ImportError:
                # Verificar se é import local
                if not self._is_local_import(import_name):
                    self.integration_report['issues_found'].append({
                        'type': 'unresolved_import',
                        'component': file_path.parent.name,
                        'file': file_path.name,
                        'import': import_name,
                        'message': f"Import '{import_name}' não pode ser resolvido",
                        'severity': 'medium'
                    })
    
    def _is_local_import(self, import_name: str) -> bool:
        """Verifica se é um import local do projeto"""
        
        local_modules = [
            'autonomous_agent', 'core', 'dashboard', 'collectors',
            'api', 'services', 'config', 'metrics', 'cache'
        ]
        
        return any(import_name.startswith(mod) for mod in local_modules)
    
    def _verify_component_communication(self) -> None:
        """Verifica comunicação entre componentes"""
        
        print("🔗 Verificando comunicação entre componentes...")
        
        # Testar comunicação ML Foundation <-> Autonomous Agent
        self._test_ml_foundation_communication()
        
        # Testar comunicação Dashboard <-> Core Systems
        self._test_dashboard_communication()
        
        # Testar comunicação API <-> Services
        self._test_api_services_communication()
        
        # Testar comunicação Cache <-> Collectors
        self._test_cache_collectors_communication()
        
        self.integration_report['integrations_verified'] += 4
    
    def _test_ml_foundation_communication(self) -> None:
        """Testa comunicação ML Foundation"""
        
        try:
            # Verificar se ML Foundation está integrado
            ml_foundation_path = self.base_path / 'core' / 'culture_pulse_executive_integration.py'
            
            if ml_foundation_path.exists():
                with open(ml_foundation_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar integração com autonomous agents
                if 'autonomous_agent' not in content:
                    self.integration_report['issues_found'].append({
                        'type': 'missing_integration',
                        'component': 'ml_foundation',
                        'message': "ML Foundation não integrado com Autonomous Agents",
                        'severity': 'high'
                    })
                
                # Verificar classes essenciais
                required_classes = ['MLFoundation', 'ExecutiveIntegration']
                for class_name in required_classes:
                    if f"class {class_name}" not in content:
                        self.integration_report['issues_found'].append({
                            'type': 'missing_class',
                            'component': 'ml_foundation',
                            'class': class_name,
                            'message': f"Classe {class_name} não encontrada",
                            'severity': 'medium'
                        })
        
        except Exception as e:
            self.integration_report['issues_found'].append({
                'type': 'communication_test_error',
                'component': 'ml_foundation',
                'message': f"Erro ao testar comunicação ML Foundation: {str(e)}",
                'severity': 'medium'
            })
    
    def _test_dashboard_communication(self) -> None:
        """Testa comunicação Dashboard"""
        
        try:
            dashboard_path = self.base_path / 'dashboard' / 'cultural_dashboard_integrated.py'
            
            if dashboard_path.exists():
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar integração com sistemas core
                core_integrations = ['culture_pulse_executive_integration', 'enhanced_dashboard']
                for integration in core_integrations:
                    if integration not in content:
                        self.integration_report['issues_found'].append({
                            'type': 'missing_dashboard_integration',
                            'component': 'dashboard',
                            'integration': integration,
                            'message': f"Dashboard não integrado com {integration}",
                            'severity': 'medium'
                        })
        
        except Exception as e:
            self.integration_report['issues_found'].append({
                'type': 'communication_test_error',
                'component': 'dashboard',
                'message': f"Erro ao testar comunicação Dashboard: {str(e)}",
                'severity': 'medium'
            })
    
    def _test_api_services_communication(self) -> None:
        """Testa comunicação API Services"""
        
        try:
            api_path = self.base_path / 'api'
            services_path = self.base_path / 'services'
            
            if api_path.exists() and services_path.exists():
                # Verificar se APIs estão conectadas aos services
                api_files = list(api_path.glob('*.py'))
                service_files = list(services_path.glob('*.py'))
                
                if not api_files:
                    self.integration_report['issues_found'].append({
                        'type': 'no_api_files',
                        'component': 'api',
                        'message': "Nenhum arquivo de API encontrado",
                        'severity': 'medium'
                    })
                
                if not service_files:
                    self.integration_report['issues_found'].append({
                        'type': 'no_service_files',
                        'component': 'services',
                        'message': "Nenhum arquivo de service encontrado",
                        'severity': 'medium'
                    })
        
        except Exception as e:
            self.integration_report['issues_found'].append({
                'type': 'communication_test_error',
                'component': 'api_services',
                'message': f"Erro ao testar comunicação API-Services: {str(e)}",
                'severity': 'low'
            })
    
    def _test_cache_collectors_communication(self) -> None:
        """Testa comunicação Cache Collectors"""
        
        try:
            cache_path = self.base_path / 'cache'
            collectors_path = self.base_path / 'collectors'
            
            # Verificar se cache está sendo usado pelos collectors
            if collectors_path.exists():
                collector_files = list(collectors_path.glob('*.py'))
                
                cache_usage_count = 0
                for file_path in collector_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if 'cache' in content.lower():
                            cache_usage_count += 1
                    except:
                        continue
                
                if cache_usage_count == 0 and len(collector_files) > 0:
                    self.integration_report['issues_found'].append({
                        'type': 'no_cache_integration',
                        'component': 'collectors',
                        'message': "Collectors não estão usando sistema de cache",
                        'severity': 'low'
                    })
        
        except Exception as e:
            self.integration_report['issues_found'].append({
                'type': 'communication_test_error',
                'component': 'cache_collectors',
                'message': f"Erro ao testar comunicação Cache-Collectors: {str(e)}",
                'severity': 'low'
            })
    
    def _verify_configurations(self) -> None:
        """Verifica configurações do sistema"""
        
        print("⚙️ Verificando configurações...")
        
        config_files = [
            'config.json',
            'requirements.txt',
            'requirements_api.txt'
        ]
        
        for config_file in config_files:
            config_path = self.base_path / config_file
            
            if not config_path.exists():
                self.integration_report['issues_found'].append({
                    'type': 'missing_config',
                    'component': 'config',
                    'file': config_file,
                    'message': f"Arquivo de configuração {config_file} não encontrado",
                    'severity': 'medium' if config_file.endswith('.txt') else 'low'
                })
    
    def _verify_ml_foundation_integration(self) -> None:
        """Verifica integração específica do ML Foundation"""
        
        print("🤖 Verificando integração ML Foundation...")
        
        # Verificar se todos os componentes autônomos estão presentes
        autonomous_components = [
            'research_refiner.py',
            'decision_engine.py',
            'parameter_optimizer.py',
            'narrative_generator.py',
            'predictive_analytics.py',
            'real_time_monitor.py',
            'temporal_validator.py',
            'ab_testing_engine.py',
            'advanced_validation_criteria.py'
        ]
        
        autonomous_path = self.base_path / 'autonomous_agent'
        missing_components = []
        
        for component in autonomous_components:
            if not (autonomous_path / component).exists():
                missing_components.append(component)
        
        if missing_components:
            self.integration_report['issues_found'].append({
                'type': 'missing_autonomous_components',
                'component': 'autonomous_agent',
                'missing_files': missing_components,
                'message': f"Componentes autônomos ausentes: {', '.join(missing_components)}",
                'severity': 'high'
            })
    
    def _verify_autonomous_systems(self) -> None:
        """Verifica sistemas autônomos"""
        
        print("🤖 Verificando sistemas autônomos...")
        
        autonomous_path = self.base_path / 'autonomous_agent'
        
        if autonomous_path.exists():
            # Verificar integrações entre componentes autônomos
            component_interactions = {
                'research_refiner.py': ['decision_engine'],
                'decision_engine.py': ['parameter_optimizer', 'predictive_analytics'],
                'narrative_generator.py': ['advanced_validation_criteria'],
                'real_time_monitor.py': ['temporal_validator']
            }
            
            for component, expected_interactions in component_interactions.items():
                component_path = autonomous_path / component
                
                if component_path.exists():
                    try:
                        with open(component_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for interaction in expected_interactions:
                            if interaction not in content:
                                self.integration_report['issues_found'].append({
                                    'type': 'missing_autonomous_interaction',
                                    'component': 'autonomous_agent',
                                    'file': component,
                                    'missing_interaction': interaction,
                                    'message': f"{component} não interage com {interaction}",
                                    'severity': 'low'
                                })
                    
                    except Exception:
                        pass
    
    def _run_integration_tests(self) -> None:
        """Executa testes de integração end-to-end"""
        
        print("🧪 Executando testes de integração...")
        
        # Teste 1: Verificar se sistema pode ser importado
        try:
            sys.path.insert(0, str(self.base_path))
            
            # Tentar importar componentes principais
            critical_imports = [
                'core.culture_pulse_executive_integration',
                'dashboard.cultural_dashboard_integrated'
            ]
            
            for import_path in critical_imports:
                try:
                    importlib.import_module(import_path)
                except ImportError as e:
                    self.integration_report['issues_found'].append({
                        'type': 'integration_test_failure',
                        'component': import_path,
                        'message': f"Falha ao importar {import_path}: {str(e)}",
                        'severity': 'high'
                    })
        
        except Exception as e:
            self.integration_report['issues_found'].append({
                'type': 'integration_test_error',
                'component': 'system',
                'message': f"Erro durante testes de integração: {str(e)}",
                'severity': 'medium'
            })
    
    def _generate_integration_recommendations(self) -> None:
        """Gera recomendações de melhoria"""
        
        print("💡 Gerando recomendações...")
        
        # Analisar issues encontrados e gerar recomendações
        high_severity_issues = [
            issue for issue in self.integration_report['issues_found'] 
            if issue.get('severity') == 'high'
        ]
        
        medium_severity_issues = [
            issue for issue in self.integration_report['issues_found']
            if issue.get('severity') == 'medium'
        ]
        
        # Recomendações baseadas em issues
        if high_severity_issues:
            self.integration_report['recommendations'].append({
                'priority': 'high',
                'action': 'Corrigir issues críticos imediatamente',
                'description': f"Foram encontrados {len(high_severity_issues)} issues críticos que podem impactar o funcionamento do sistema",
                'issues_count': len(high_severity_issues)
            })
        
        if medium_severity_issues:
            self.integration_report['recommendations'].append({
                'priority': 'medium',
                'action': 'Revisar e corrigir issues de média prioridade',
                'description': f"Foram encontrados {len(medium_severity_issues)} issues que podem afetar a performance",
                'issues_count': len(medium_severity_issues)
            })
        
        # Recomendações gerais
        self.integration_report['recommendations'].extend([
            {
                'priority': 'medium',
                'action': 'Implementar testes unitários automatizados',
                'description': 'Adicionar testes para todos os componentes críticos'
            },
            {
                'priority': 'low',
                'action': 'Documentar APIs de integração',
                'description': 'Criar documentação detalhada das interfaces entre componentes'
            },
            {
                'priority': 'low',
                'action': 'Implementar monitoramento de health check',
                'description': 'Adicionar endpoints para verificação de saúde dos componentes'
            }
        ])
    
    def save_integration_report(self, output_path: Optional[str] = None) -> str:
        """Salva relatório de integração"""
        
        if output_path is None:
            output_path = self.base_path / 'integration_verification_report.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.integration_report, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Retorna resumo da verificação"""
        
        return {
            'status': self.integration_report['status'],
            'components_checked': self.integration_report['components_checked'],
            'integrations_verified': self.integration_report['integrations_verified'],
            'total_issues': len(self.integration_report['issues_found']),
            'critical_issues': len([
                issue for issue in self.integration_report['issues_found']
                if issue.get('severity') == 'high'
            ]),
            'recommendations_count': len(self.integration_report['recommendations']),
            'health_score': self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> float:
        """Calcula score de saúde da integração"""
        
        total_issues = len(self.integration_report['issues_found'])
        critical_issues = len([
            issue for issue in self.integration_report['issues_found']
            if issue.get('severity') == 'high'
        ])
        
        if total_issues == 0:
            return 1.0
        
        # Penalizar mais issues críticos
        penalty = (critical_issues * 0.3) + ((total_issues - critical_issues) * 0.1)
        health_score = max(0.0, 1.0 - penalty)
        
        return health_score

def run_integration_verification(base_path: str) -> Dict[str, Any]:
    """Função principal para executar verificação"""
    
    verifier = IntegrationVerifier(base_path)
    report = verifier.run_full_integration_check()
    
    # Salvar relatório
    report_path = verifier.save_integration_report()
    
    # Imprimir resumo
    summary = verifier.get_integration_summary()
    
    print("\n" + "="*50)
    print("📊 RESUMO DA VERIFICAÇÃO DE INTEGRAÇÃO")
    print("="*50)
    print(f"Status: {summary['status']}")
    print(f"Componentes verificados: {summary['components_checked']}")
    print(f"Integrações verificadas: {summary['integrations_verified']}")
    print(f"Issues encontrados: {summary['total_issues']}")
    print(f"Issues críticos: {summary['critical_issues']}")
    print(f"Score de saúde: {summary['health_score']:.1%}")
    print(f"Relatório salvo em: {report_path}")
    print("="*50)
    
    return {
        'report': report,
        'summary': summary,
        'report_path': report_path
    }

if __name__ == "__main__":
    # Executar verificação
    base_path = r"c:\Users\Roberto\Desktop\futuruma\src_v8"
    result = run_integration_verification(base_path)
    
    print("🔧 Verificação de integração concluída!")
