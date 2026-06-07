#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Culture Pulse V9.0 - Launcher Rápido
Script simplificado para execução dos diagnósticos mais comuns

🎯 COMANDOS DISPONÍVEIS:
- full: Execução completa (todos os níveis)
- quick: Diagnóstico rápido (apenas CLI)
- ui: Apenas interfaces Streamlit
- monitor: CLI + Monitoramento
"""

import subprocess
import sys
import os

def print_header():
    print("🎛️" + "=" * 58)
    print("🚀 CULTURE PULSE V9.0 - LAUNCHER DIAGNÓSTICO")
    print("🎛️" + "=" * 58)

def print_usage():
    print("\n📋 USO:")
    print("  python run_diagnostics.py [modo]")
    print("\n🎯 MODOS DISPONÍVEIS:")
    print("  full    - Execução completa (CLI + Monitoring + UI)")
    print("  quick   - Diagnóstico rápido (apenas CLI)")
    print("  ui      - Apenas interfaces Streamlit")
    print("  monitor - CLI + Monitoramento")
    print("  help    - Mostra esta ajuda")
    print("\n💡 EXEMPLOS:")
    print("  python run_diagnostics.py full")
    print("  python run_diagnostics.py quick")
    print("  python run_diagnostics.py ui")

def run_orchestrator(mode: str):
    """Executa o orquestrador com o modo especificado"""
    cmd = [sys.executable, "orchestrator_diagnostics.py", "--mode", mode]
    
    if os.path.exists("config/orchestrator_config.json"):
        cmd.extend(["--config", "config/orchestrator_config.json"])
    
    print(f"🔄 Executando: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na execução: {e}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário")
        sys.exit(130)

def main():
    print_header()
    
    if len(sys.argv) < 2:
        print("⚠️ Modo não especificado. Usando 'full' como padrão.")
        mode = "full"
    else:
        mode = sys.argv[1].lower()
    
    # Mapear comandos
    mode_mapping = {
        "full": "full",
        "quick": "cli_only", 
        "ui": "ui_only",
        "monitor": "headless",
        "help": None
    }
    
    if mode == "help" or mode not in mode_mapping:
        print_usage()
        return
    
    orchestrator_mode = mode_mapping[mode]
    
    print(f"🎯 Modo selecionado: {mode.upper()}")
    
    # Verificar se orquestrador existe
    if not os.path.exists("orchestrator_diagnostics.py"):
        print("❌ Arquivo orchestrator_diagnostics.py não encontrado!")
        print("💡 Certifique-se de estar no diretório correto.")
        sys.exit(1)
    
    run_orchestrator(orchestrator_mode)

if __name__ == "__main__":
    main()
