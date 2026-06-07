#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎛️ Culture Pulse V9.0 - Orquestrador de Diagnósticos
Orquestrador principal para execução coordenada de todos os diagnósticos

🎯 MODOS DE EXECUÇÃO:
- FULL: Executa todos os níveis (CLI + Monitoring + UI)
- CLI_ONLY: Apenas diagnósticos CLI (rápido)
- MONITORING: CLI + Monitoramento (sem UI)
- HEADLESS: Todos exceto interface Streamlit
- UI_ONLY: Apenas interface Streamlit

🚀 EXECUÇÃO:
python orchestrator_diagnostics.py --mode full
python orchestrator_diagnostics.py --mode cli_only
python orchestrator_diagnostics.py --mode headless --config config.yaml

🎯 OUTPUTS:
- Console colorido em tempo real
- Relatórios JSON estruturados
- Logs detalhados para debugging
- URLs de acesso aos dashboards
"""

import asyncio
import logging
import json
import time
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import concurrent.futures

class ExecutionMode(Enum):
    FULL = "full"           # Executa todos os níveis
    CLI_ONLY = "cli_only"   # Apenas diagnósticos CLI
    MONITORING = "monitoring"  # CLI + Monitoramento
    HEADLESS = "headless"   # Sem interface Streamlit
    UI_ONLY = "ui_only"     # Apenas interfaces Streamlit

class DiagnosticLevel(Enum):
    SYSTEM = "system"       # diagnostic.py + integration_verifier.py
    MONITORING = "monitoring"  # integrated_monitoring.py + dashboard
    UI_STREAMLIT = "ui_streamlit"  # diagnostico_streamlit.py
    UI_MAIN = "ui_main"     # cultural_dashboard_integrated.py

@dataclass
class OrchestrationResult:
    level: str
    component: str
    success: bool
    duration: float
    message: str
    start_time: str
    end_time: str
    data: Optional[Dict] = None
    url: Optional[str] = None
    pid: Optional[int] = None

class Colors:
    """Cores para output colorido no console"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DiagnosticOrchestrator:
    """Orquestrador principal de diagnósticos V9.0"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.results: List[OrchestrationResult] = []
        self.logger = self._setup_logging()
        self.start_time = time.time()
        self.running_processes = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Carrega configuração centralizada ou usa defaults"""
        default_config = {
            "levels": {
                "system": {
                    "enabled": True, 
                    "timeout": 300,
                    "components": ["diagnostic.py", "integration_verifier.py"]
                },
                "monitoring": {
                    "enabled": True, 
                    "timeout": 600,
                    "components": ["integrated_monitoring.py", "integrated_monitoring_dashboard.py"]
                }, 
                "ui": {
                    "enabled": True, 
                    "timeout": 120,
                    "components": ["diagnostico_streamlit.py", "cultural_dashboard_integrated.py"]
                }
            },
            "output_dir": "./diagnostic_outputs",
            "parallel_execution": True,
            "ports": {
                "main_dashboard": 8501,
                "diagnostic_dashboard": 8502,
                "monitoring_dashboard": 8503
            },
            "generate_reports": True,
            "auto_open_browser": False
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    if config_path.endswith('.json'):
                        user_config = json.load(f)
                    else:
                        # Assumir YAML se não for JSON
                        import yaml
                        user_config = yaml.safe_load(f)
                
                # Merge configurations
                default_config.update(user_config)
                self._print_colored(f"✅ Configuração carregada: {config_path}", Colors.GREEN)
                
            except Exception as e:
                self._print_colored(f"⚠️ Erro ao carregar config: {e}. Usando defaults.", Colors.YELLOW)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup de logging unificado com arquivo e console"""
        logger = logging.getLogger("DiagnosticOrchestrator")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path(self.config["output_dir"])
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _print_colored(self, message: str, color: str = Colors.WHITE):
        """Print colorido no console"""
        print(f"{color}{message}{Colors.END}")
    
    def _print_header(self, title: str):
        """Print header destacado"""
        border = "=" * 60
        print(f"\n{Colors.CYAN}{Colors.BOLD}{border}")
        print(f"🎛️  {title}")
        print(f"{border}{Colors.END}\n")

    async def execute_level_1_system(self) -> List[OrchestrationResult]:
        """Executa diagnósticos de sistema (CLI)"""
        results = []
        self._print_header("NÍVEL 1 - DIAGNÓSTICOS DE SISTEMA")
        
        try:
            # 1. Diagnóstico geral
            self._print_colored("🔍 Executando diagnostic.py...", Colors.BLUE)
            start_time = time.time()
            start_timestamp = datetime.now().isoformat()
            
            # Usar comando que sabemos que funciona
            diagnostic_result = await self._run_subprocess([
                sys.executable, "diagnostic/diagnostic.py"
            ], timeout=self.config["levels"]["system"]["timeout"])
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = diagnostic_result["returncode"] == 0
            message = "Diagnóstico geral do sistema concluído" if success else f"Falha no diagnóstico geral (código: {diagnostic_result['returncode']})"
            if not success:
                # Debug mais detalhado
                if diagnostic_result.get("stderr"):
                    message += f" - STDERR: {diagnostic_result['stderr'][:200]}..."
                if diagnostic_result.get("stdout"):
                    # Verificar se há mensagens de erro no stdout também
                    stdout_lines = diagnostic_result['stdout'].split('\n')[-10:]  # Últimas 10 linhas
                    message += f" - STDOUT: {' '.join(stdout_lines)[:200]}..."
                self._print_colored(f"❌ DEBUG diagnostic.py: returncode={diagnostic_result['returncode']}", Colors.RED)
                self._print_colored(f"   STDERR: {diagnostic_result.get('stderr', 'Nenhum')}", Colors.RED)
                self._print_colored(f"   Últimas linhas STDOUT: {stdout_lines}", Colors.YELLOW)
            
            results.append(OrchestrationResult(
                level="system",
                component="diagnostic.py",
                success=success,
                duration=duration,
                message=message,
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                data=diagnostic_result
            ))
            
            # 2. Verificação de integrações
            self._print_colored("🔗 Executando integration_verifier.py...", Colors.BLUE)
            start_time = time.time()
            start_timestamp = datetime.now().isoformat()
            
            # Usar comando que sabemos que funciona
            integration_result = await self._run_subprocess([
                sys.executable, "diagnostic/integration_verifier.py"
            ], timeout=self.config["levels"]["system"]["timeout"])
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = integration_result["returncode"] == 0
            message = "Verificação de integrações concluída" if success else f"Falha na verificação de integrações (código: {integration_result['returncode']})"
            if not success:
                # Debug mais detalhado
                if integration_result.get("stderr"):
                    message += f" - STDERR: {integration_result['stderr'][:200]}..."
                if integration_result.get("stdout"):
                    # Verificar se há mensagens de erro no stdout também
                    stdout_lines = integration_result['stdout'].split('\n')[-10:]  # Últimas 10 linhas
                    message += f" - STDOUT: {' '.join(stdout_lines)[:200]}..."
                self._print_colored(f"❌ DEBUG integration_verifier.py: returncode={integration_result['returncode']}", Colors.RED)
                self._print_colored(f"   STDERR: {integration_result.get('stderr', 'Nenhum')}", Colors.RED)
                self._print_colored(f"   Últimas linhas STDOUT: {stdout_lines}", Colors.YELLOW)
            
            results.append(OrchestrationResult(
                level="system",
                component="integration_verifier.py",
                success=success,
                duration=duration,
                message=message,
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                data=integration_result
            ))
            
            success_count = sum(1 for r in results if r.success)
            total_count = len(results)
            
            if success_count == total_count:
                self._print_colored(f"✅ Nível 1 concluído: {success_count}/{total_count} sucessos", Colors.GREEN)
            else:
                self._print_colored(f"⚠️ Nível 1 com falhas: {success_count}/{total_count} sucessos", Colors.YELLOW)
                # Mostrar detalhes das falhas
                for result in results:
                    if not result.success:
                        self._print_colored(f"   ❌ {result.component}: {result.message}", Colors.RED)
            
        except Exception as e:
            self._print_colored(f"❌ Erro no nível 1: {str(e)}", Colors.RED)
            results.append(OrchestrationResult(
                level="system",
                component="level_1",
                success=False,
                duration=0.0,
                message=f"Erro geral no nível 1: {str(e)}",
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat()
            ))
        
        return results

    async def execute_level_2_monitoring(self) -> List[OrchestrationResult]:
        """Executa monitoramento (Backend + Dashboard)"""
        results = []
        self._print_header("NÍVEL 2 - MONITORAMENTO")
        
        try:
            # 1. Backend de monitoramento
            self._print_colored("📊 Iniciando backend de monitoramento...", Colors.BLUE)
            start_timestamp = datetime.now().isoformat()
            
            monitoring_proc = await self._start_background_service([
                sys.executable, "monitoring/integrated_monitoring.py"
            ])
            
            results.append(OrchestrationResult(
                level="monitoring",
                component="integrated_monitoring.py",
                success=True,
                duration=1.0,  # Processo em background
                message="Backend de monitoramento iniciado",
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                pid=monitoring_proc.pid if monitoring_proc else None
            ))
            
            # Aguardar inicialização
            await asyncio.sleep(2)
            
            # 2. Dashboard de monitoramento
            self._print_colored("📈 Iniciando dashboard de monitoramento...", Colors.BLUE)
            start_timestamp = datetime.now().isoformat()
            
            dashboard_proc = await self._start_background_service([
                sys.executable, "-m", "streamlit", "run",
                "monitoring/integrated_monitoring_dashboard.py",
                "--server.port", str(self.config["ports"]["monitoring_dashboard"]),
                "--server.headless", "true"
            ])
            
            dashboard_url = f"http://localhost:{self.config['ports']['monitoring_dashboard']}"
            
            results.append(OrchestrationResult(
                level="monitoring",
                component="integrated_monitoring_dashboard.py",
                success=True,
                duration=2.0,
                message=f"Dashboard de monitoramento disponível",
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                url=dashboard_url,
                pid=dashboard_proc.pid if dashboard_proc else None
            ))
            
            self._print_colored(f"✅ Nível 2 concluído: Dashboard em {dashboard_url}", Colors.GREEN)
            
        except Exception as e:
            self._print_colored(f"❌ Erro no nível 2: {str(e)}", Colors.RED)
            results.append(OrchestrationResult(
                level="monitoring",
                component="level_2",
                success=False,
                duration=0.0,
                message=f"Erro geral no nível 2: {str(e)}",
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat()
            ))
        
        return results

    async def execute_level_3_ui(self) -> List[OrchestrationResult]:
        """Executa interfaces Streamlit"""
        results = []
        self._print_header("NÍVEL 3 - INTERFACES STREAMLIT")
        
        try:
            # 1. Dashboard principal
            self._print_colored("🏠 Iniciando dashboard principal...", Colors.BLUE)
            start_timestamp = datetime.now().isoformat()
            
            main_proc = await self._start_background_service([
                sys.executable, "-m", "streamlit", "run",
                "dashboard/cultural_dashboard_integrated.py",
                "--server.port", str(self.config["ports"]["main_dashboard"]),
                "--server.headless", "true"
            ])
            
            main_url = f"http://localhost:{self.config['ports']['main_dashboard']}"
            
            results.append(OrchestrationResult(
                level="ui",
                component="cultural_dashboard_integrated.py",
                success=True,
                duration=3.0,
                message="Dashboard principal Culture Pulse disponível",
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                url=main_url,
                pid=main_proc.pid if main_proc else None
            ))
            
            # Aguardar inicialização
            await asyncio.sleep(2)
            
            # 2. Dashboard de diagnóstico
            self._print_colored("🔬 Iniciando dashboard de diagnóstico...", Colors.BLUE)
            start_timestamp = datetime.now().isoformat()
            
            diag_proc = await self._start_background_service([
                sys.executable, "-m", "streamlit", "run",
                "performance/diagnostico_streamlit.py",
                "--server.port", str(self.config["ports"]["diagnostic_dashboard"]),
                "--server.headless", "true"
            ])
            
            diag_url = f"http://localhost:{self.config['ports']['diagnostic_dashboard']}"
            
            results.append(OrchestrationResult(
                level="ui",
                component="diagnostico_streamlit.py",
                success=True,
                duration=3.0,
                message="Dashboard de diagnóstico disponível",
                start_time=start_timestamp,
                end_time=datetime.now().isoformat(),
                url=diag_url,
                pid=diag_proc.pid if diag_proc else None
            ))
            
            self._print_colored(f"✅ Nível 3 concluído:", Colors.GREEN)
            self._print_colored(f"   🏠 Principal: {main_url}", Colors.CYAN)
            self._print_colored(f"   🔬 Diagnóstico: {diag_url}", Colors.CYAN)
            
        except Exception as e:
            self._print_colored(f"❌ Erro no nível 3: {str(e)}", Colors.RED)
            results.append(OrchestrationResult(
                level="ui",
                component="level_3",
                success=False,
                duration=0.0,
                message=f"Erro geral no nível 3: {str(e)}",
                start_time=datetime.now().isoformat(),
                end_time=datetime.now().isoformat()
            ))
        
        return results

    async def _run_subprocess(self, cmd: List[str], timeout: int = 300) -> Dict:
        """Executa subprocess com timeout e encoding UTF-8"""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}  # Forçar UTF-8
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), 
                timeout=timeout
            )
            
            return {
                "returncode": proc.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),  # Usar replace para evitar erros
                "stderr": stderr.decode('utf-8', errors='replace'),
                "cmd": ' '.join(cmd)
            }
            
        except asyncio.TimeoutError:
            self._print_colored(f"⏰ Timeout executando: {' '.join(cmd)}", Colors.YELLOW)
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Timeout após {timeout}s",
                "cmd": ' '.join(cmd)
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "cmd": ' '.join(cmd)
            }

    async def _start_background_service(self, cmd: List[str]):
        """Inicia serviço em background e registra para cleanup"""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            if proc:
                self.running_processes.append(proc)
            
            return proc
            
        except Exception as e:
            self._print_colored(f"❌ Erro ao iniciar serviço: {' '.join(cmd)} - {e}", Colors.RED)
            return None

    async def orchestrate(self, mode: ExecutionMode = ExecutionMode.FULL) -> List[OrchestrationResult]:
        """Executa orquestração baseada no modo"""
        self._print_header(f"CULTURE PULSE V9.0 - ORQUESTRAÇÃO DIAGNÓSTICA")
        self._print_colored(f"🎯 Modo de execução: {mode.value.upper()}", Colors.BOLD)
        self._print_colored(f"🕒 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
        
        all_results = []
        
        try:
            # Nível 1 - Sistema (CLI)
            if mode in [ExecutionMode.FULL, ExecutionMode.CLI_ONLY, ExecutionMode.MONITORING, ExecutionMode.HEADLESS]:
                level_1_results = await self.execute_level_1_system()
                all_results.extend(level_1_results)
                
                # Verificar se deve continuar
                failed_critical = any(not r.success for r in level_1_results)
                if failed_critical and mode != ExecutionMode.CLI_ONLY:
                    self._print_colored("⚠️ Falhas críticas detectadas no nível 1. Continuando com outros níveis...", Colors.YELLOW)

            # Nível 2 - Monitoramento
            if mode in [ExecutionMode.FULL, ExecutionMode.MONITORING, ExecutionMode.HEADLESS]:
                level_2_results = await self.execute_level_2_monitoring()
                all_results.extend(level_2_results)

            # Nível 3 - UI Streamlit
            if mode in [ExecutionMode.FULL, ExecutionMode.UI_ONLY]:
                level_3_results = await self.execute_level_3_ui()
                all_results.extend(level_3_results)

            self.results = all_results
            self._generate_summary_report()
            
            return all_results
            
        except KeyboardInterrupt:
            self._print_colored("\n🛑 Orquestração interrompida pelo usuário", Colors.YELLOW)
            await self._cleanup_processes()
            return all_results
            
        except Exception as e:
            self._print_colored(f"❌ Erro crítico na orquestração: {e}", Colors.RED)
            await self._cleanup_processes()
            return all_results

    async def _cleanup_processes(self):
        """Limpa processos em background"""
        if self.running_processes:
            self._print_colored("🧹 Limpando processos em background...", Colors.YELLOW)
            
            for proc in self.running_processes:
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except:
                    try:
                        proc.kill()
                    except:
                        pass

    def _generate_summary_report(self):
        """Gera relatório de resumo da execução"""
        total_time = time.time() - self.start_time
        
        self._print_header("RELATÓRIO DE EXECUÇÃO")
        
        # Estatísticas gerais
        total_components = len(self.results)
        successful_components = sum(1 for r in self.results if r.success)
        failed_components = total_components - successful_components
        
        self._print_colored(f"📊 Total de componentes: {total_components}", Colors.WHITE)
        self._print_colored(f"✅ Sucessos: {successful_components}", Colors.GREEN)
        self._print_colored(f"❌ Falhas: {failed_components}", Colors.RED)
        self._print_colored(f"⏱️ Tempo total: {total_time:.2f}s", Colors.BLUE)
        
        # URLs disponíveis
        available_urls = [r.url for r in self.results if r.url]
        if available_urls:
            print(f"\n{Colors.CYAN}{Colors.BOLD}🌐 DASHBOARDS DISPONÍVEIS:{Colors.END}")
            for url in available_urls:
                self._print_colored(f"   • {url}", Colors.CYAN)
        
        # Processos em background
        running_pids = [r.pid for r in self.results if r.pid]
        if running_pids:
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}🔄 PROCESSOS EM BACKGROUND:{Colors.END}")
            for pid in running_pids:
                self._print_colored(f"   • PID: {pid}", Colors.MAGENTA)
        
        # Salvar relatório JSON se configurado
        if self.config["generate_reports"]:
            self._save_json_report()
    
    def _save_json_report(self):
        """Salva relatório em JSON"""
        try:
            output_dir = Path(self.config["output_dir"])
            output_dir.mkdir(exist_ok=True)
            
            report = {
                "execution_summary": {
                    "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "total_duration": time.time() - self.start_time,
                    "total_components": len(self.results),
                    "successful_components": sum(1 for r in self.results if r.success),
                    "failed_components": sum(1 for r in self.results if not r.success)
                },
                "results": [asdict(r) for r in self.results],
                "config": self.config
            }
            
            report_file = output_dir / f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self._print_colored(f"📋 Relatório salvo: {report_file}", Colors.GREEN)
            
        except Exception as e:
            self._print_colored(f"⚠️ Erro ao salvar relatório: {e}", Colors.YELLOW)

# CLI Interface
async def main():
    """Interface CLI principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🎛️ Culture Pulse V9.0 - Orquestrador de Diagnósticos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python orchestrator_diagnostics.py --mode full
  python orchestrator_diagnostics.py --mode cli_only --config config.json
  python orchestrator_diagnostics.py --mode headless
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=[mode.value for mode in ExecutionMode],
        default="full",
        help="Modo de execução (default: full)"
    )
    
    parser.add_argument(
        "--config", 
        help="Caminho para arquivo de configuração (JSON ou YAML)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./diagnostic_outputs",
        help="Diretório para outputs (default: ./diagnostic_outputs)"
    )
    
    parser.add_argument(
        "--no-reports",
        action="store_true",
        help="Não gerar relatórios JSON"
    )
    
    args = parser.parse_args()
    
    # Criar orquestrador
    orchestrator = DiagnosticOrchestrator(args.config)
    
    # Override configurações via CLI
    if args.output_dir:
        orchestrator.config["output_dir"] = args.output_dir
    if args.no_reports:
        orchestrator.config["generate_reports"] = False
    
    # Executar orquestração
    mode = ExecutionMode(args.mode)
    results = await orchestrator.orchestrate(mode)
    
    # Exit code baseado no sucesso
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    
    if total_count == 0:
        sys.exit(1)  # Nenhum componente executado
    elif success_count == total_count:
        sys.exit(0)  # Todos sucessos
    elif success_count > total_count // 2:
        sys.exit(2)  # Maioria sucessos, algumas falhas
    else:
        sys.exit(3)  # Maioria falhas

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Execução interrompida pelo usuário{Colors.END}")
        sys.exit(130)
