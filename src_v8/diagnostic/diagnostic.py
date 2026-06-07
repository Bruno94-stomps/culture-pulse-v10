#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Diagnostics - Culture Pulse V8.0
Diagnóstico completo do sistema para identificar problemas

🔍 EXECUTAR:
python diagnostic.py

🎯 VERIFICAÇÕES:
- Dependências instaladas
- APIs configuradas
- Conectividade
- Performance
- Logs de erro
"""

import sys
import os
import time
import asyncio
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Adicionar path do projeto - CORRIGIDO para pasta raiz
project_root = Path(__file__).parent.parent  # Subir um nível para a raiz do projeto
sys.path.insert(0, str(project_root))

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}🔍 {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_python_version() -> bool:
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Necessário Python 3.8+")
        return False

def check_dependencies() -> Dict[str, bool]:
    """Check required dependencies"""
    print_header("VERIFICAÇÃO DE DEPENDÊNCIAS")
    
    required_deps = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'streamlit': 'Dashboard interface',
        'requests': 'HTTP client',
        'aiohttp': 'Async HTTP client',
        'plotly': 'Data visualization',
        'pandas': 'Data manipulation',
        'pydantic': 'Data validation',
        'pytrends': 'Google Trends (opcional)',
        'redis': 'Cache (opcional)',
    }
    
    results = {}
    
    for dep, description in required_deps.items():
        try:
            importlib.import_module(dep)
            print_success(f"{dep:<15} - {description}")
            results[dep] = True
        except ImportError:
            print_error(f"{dep:<15} - {description} (FALTANDO)")
            results[dep] = False
    
    return results

def check_project_structure() -> bool:
    """Check project structure V9.0"""
    print_header("ESTRUTURA DO PROJETO V9.0")
    
    # Diretórios principais do V9.0
    required_dirs = [
        'core',
        'collectors', 
        'dashboard',
        'config',
        'api',
        'performance',
        'monitoring',
        'diagnostic'
    ]
    
    # Arquivos principais do V9.0
    required_files = [
        # API V9.0
        'api/main.py',
        'api/run_api.py',
        'api/models.py',
        
        # Coletores V9.0
        'collectors/data_collectors.py',
        'collectors/orchestrator.py',
        
        # Dashboard V9.0
        'dashboard/cultural_dashboard_integrated.py',
        'dashboard/utils.py',
        
        # Core V9.0
        'core/cache_redis.py',
        'core/cultural_terms_engine.py',
        'core/calibrated_metrics_engine.py',
        
        # Performance & Diagnóstico V9.0
        'performance/diagnostico_streamlit.py',
        'performance/performance_optimizer.py',
        
        # Monitoramento V9.0
        'monitoring/integrated_monitoring.py',
        'monitoring/integrated_monitoring_dashboard.py',
        
        # Configurações V9.0
        'config/centralized_config.py',
        'orchestrator_diagnostics.py',
        'run_diagnostics.py'
    ]
    
    all_good = True
    
    # Check directories
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print_success(f"📁 {dir_path}")
        else:
            print_error(f"📁 {dir_path} (FALTANDO)")
            all_good = False
    
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"📄 {file_path}")
        else:
            print_error(f"📄 {file_path} (FALTANDO)")
            all_good = False
    
    return all_good

def check_environment_variables() -> Dict[str, bool]:
    """Check environment variables"""
    print_header("VARIÁVEIS DE AMBIENTE")
    
    env_vars = {
        'YOUTUBE_API_KEY': 'YouTube Data API',
        'REDDIT_CLIENT_ID': 'Reddit API',
        'REDDIT_CLIENT_SECRET': 'Reddit API Secret', 
        'SPOTIFY_CLIENT_ID': 'Spotify API',
        'SPOTIFY_CLIENT_SECRET': 'Spotify API Secret',
        'NEWS_API_KEY': 'NewsAPI'
    }
    
    results = {}
    
    # Check .env file
    env_file = project_root / '.env'
    if env_file.exists():
        print_success(".env file encontrado")
        if ENV_LOADED:
            print_success("Variáveis de ambiente carregadas")
        else:
            print_warning("python-dotenv não instalado")
    else:
        print_warning(".env file não encontrado (usando .env.example como referência)")
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var:<25} - {description}")
            results[var] = True
        else:
            print_warning(f"{var:<25} - {description} (NÃO CONFIGURADO)")
            results[var] = False
    
    return results

async def check_api_connectivity() -> Dict[str, bool]:
    """Check external API connectivity"""
    print_header("CONECTIVIDADE DAS APIs")
    
    results = {}
    
    # Test simple HTTP connectivity
    test_urls = {
        'YouTube': 'https://www.googleapis.com/youtube/v3',
        'Reddit': 'https://www.reddit.com',
        'NewsAPI': 'https://newsapi.org/v2',
        'Spotify': 'https://accounts.spotify.com',
        'IBGE': 'https://servicodados.ibge.gov.br/api/v1/pesquisas',
        'Google': 'https://www.google.com'
    }
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for name, url in test_urls.items():
                try:
                    async with session.get(url) as response:
                        if response.status < 500:
                            print_success(f"{name:<15} - Conectividade OK")
                            results[name] = True
                        else:
                            print_error(f"{name:<15} - HTTP {response.status}")
                            results[name] = False
                except Exception as e:
                    print_error(f"{name:<15} - Erro: {str(e)[:50]}")
                    results[name] = False
    
    except ImportError:
        print_error("aiohttp não disponível - pulando teste de conectividade")
        results = {name: False for name in test_urls.keys()}
    
    return results

def check_collectors() -> Dict[str, bool]:
    """Check data collectors"""
    print_header("COLETORES DE DADOS")
    
    results = {}
    
    try:
        from collectors.data_collectors import create_data_collectors
        
        collectors = create_data_collectors()
        
        for name, collector in collectors.items():
            if collector:
                print_success(f"{name:<15} - Collector inicializado")
                results[name] = True
            else:
                print_error(f"{name:<15} - Falha na inicialização")
                results[name] = False
                
    except Exception as e:
        print_error(f"Erro ao carregar coletores: {e}")
        results = {}
    
    return results

def check_core_components() -> Dict[str, bool]:
    """Check core components"""
    print_header("COMPONENTES CORE")
    
    results = {}
    components = [
        ('cultural_engine', 'Engine principal'),
        ('circles_processor', 'Processador de círculos'),
        ('tfidf_analyzer', 'Analisador TF-IDF'),
        ('alma_brasileira', 'Analisador Alma Brasileira')
    ]
    
    for module_name, description in components:
        try:
            module = importlib.import_module(f'core.{module_name}')
            print_success(f"{module_name:<20} - {description}")
            results[module_name] = True
        except Exception as e:
            print_error(f"{module_name:<20} - {description} (ERRO: {str(e)[:30]})")
            results[module_name] = False
    
    return results

def performance_test() -> Dict[str, Any]:
    """Basic performance test"""
    print_header("TESTE DE PERFORMANCE")
    
    results = {}
    
    # Test import time
    start_time = time.time()
    try:
        from collectors.data_collectors import create_data_collectors
        import_time = time.time() - start_time
        print_success(f"Import time: {import_time:.2f}s")
        results['import_time'] = import_time
    except Exception as e:
        print_error(f"Import failed: {e}")
        results['import_time'] = -1
    
    # Test collector creation time
    start_time = time.time()
    try:
        collectors = create_data_collectors()
        creation_time = time.time() - start_time
        print_success(f"Collectors creation: {creation_time:.2f}s")
        results['creation_time'] = creation_time
        results['collectors_count'] = len(collectors)
    except Exception as e:
        print_error(f"Collector creation failed: {e}")
        results['creation_time'] = -1
        results['collectors_count'] = 0
    
    return results

def generate_report(all_results: Dict[str, Any]):
    """Generate final diagnostic report"""
    print_header("RELATÓRIO FINAL")
    
    # Count issues
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict):
            for result in results.values():
                if isinstance(result, bool):
                    total_checks += 1
                    if result:
                        passed_checks += 1
        elif isinstance(results, bool):
            total_checks += 1
            if results:
                passed_checks += 1
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n{Colors.BOLD}📊 RESUMO GERAL:{Colors.END}")
    print(f"Verificações realizadas: {total_checks}")
    print(f"Verificações aprovadas: {passed_checks}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print_success("Sistema em bom estado! ✨")
    elif success_rate >= 60:
        print_warning("Sistema funcional com alguns problemas 🔧")
    else:
        print_error("Sistema com problemas significativos! 🚨")
    
    # Recommendations
    print(f"\n{Colors.BOLD}🎯 RECOMENDAÇÕES:{Colors.END}")
    
    if not all_results.get('dependencies', {}).get('aiohttp', True):
        print("• Instalar dependências: pip install -r requirements.txt")
    
    env_configured = sum(all_results.get('environment', {}).values())
    if env_configured < 3:
        print("• Configurar variáveis de ambiente (.env file)")
    
    if not all_results.get('python_version', True):
        print("• Atualizar Python para versão 3.8+")
    
    if all_results.get('performance', {}).get('import_time', 0) > 5:
        print("• Verificar performance - imports muito lentos")

async def main():
    """Run all diagnostics"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("🧠 CULTURE PULSE V9.0 - DIAGNÓSTICO DO SISTEMA")
    print("=" * 60)
    print(f"{Colors.END}")
    
    all_results = {}
    
    # Run all checks
    all_results['python_version'] = check_python_version()
    all_results['dependencies'] = check_dependencies()
    all_results['project_structure'] = check_project_structure()
    all_results['environment'] = check_environment_variables()
    all_results['api_connectivity'] = await check_api_connectivity()
    all_results['collectors'] = check_collectors()
    all_results['core_components'] = check_core_components()
    all_results['performance'] = performance_test()
    
    # Generate final report
    generate_report(all_results)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}🏁 Diagnóstico concluído!{Colors.END}")
    print(f"{Colors.BLUE}Para resolver problemas, consulte: ANALISE_CODIGO_V8.md{Colors.END}")
    
    # Calcular success rate e definir exit code apropriado
    total_checks = sum(len(result) if isinstance(result, dict) else 1 for result in all_results.values())
    successful_checks = 0
    
    for category, result in all_results.items():
        if isinstance(result, dict):
            successful_checks += sum(1 for v in result.values() if v)
        elif result:
            successful_checks += 1
    
    success_rate = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
    
    # Exit codes informativos para o orquestrador
    if success_rate >= 80:
        exit_code = 0  # Sucesso total/bom
    elif success_rate >= 60:
        exit_code = 0  # Sucesso moderado (ainda considerado OK)
    elif success_rate >= 40:
        exit_code = 1  # Problemas moderados
    elif success_rate >= 20:
        exit_code = 1  # Problemas significativos  
    else:
        exit_code = 2  # Problemas críticos
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
