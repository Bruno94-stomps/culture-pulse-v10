#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Culture Pulse V8.0 - API Server Launcher
Script para inicializar a API REST

🚀 COMO USAR:
python run_api.py

🔧 OPÇÕES:
--host: Host para bind (padrão: 0.0.0.0)
--port: Porta para bind (padrão: 8000)
--reload: Modo desenvolvimento com auto-reload
--workers: Número de workers (produção)
"""

import argparse
import uvicorn
import logging
import sys
import os

# Adicionar o diretório src_v8 ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Função principal para inicializar a API"""
    
    parser = argparse.ArgumentParser(description='Culture Pulse V8.0 API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host para bind')
    parser.add_argument('--port', type=int, default=8000, help='Porta para bind')
    parser.add_argument('--reload', action='store_true', help='Modo desenvolvimento')
    parser.add_argument('--workers', type=int, default=1, help='Número de workers')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'])
    
    args = parser.parse_args()
    
    print("🧠 CULTURE PULSE V8.0 API")
    print("=" * 50)
    print(f"🌐 Host: {args.host}")
    print(f"🔌 Porta: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print(f"👥 Workers: {args.workers}")
    print(f"📋 Log Level: {args.log_level}")
    print("=" * 50)
    
    # Verificar se os módulos core estão disponíveis
    try:
        # Teste básico de imports
        import core.cultural_engine
        logger.info("✅ Core modules encontrados")
        
        # Não tentar importar main.py aqui devido a imports relativos
        logger.info("✅ Preparando para inicializar API...")
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        logger.error("Certifique-se de estar no diretório src_v8/")
        sys.exit(1)
    
    # Configuração do uvicorn
    config = {
        "app": "api.main:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "reload": args.reload
    }
    
    if not args.reload and args.workers > 1:
        config["workers"] = args.workers
    
    try:
        logger.info("🚀 Iniciando Culture Pulse V8.0 API...")
        
        # URLs importantes
        base_url = f"http://{args.host}:{args.port}"
        print(f"\n📚 DOCUMENTAÇÃO:")
        print(f"   Swagger UI: {base_url}/docs")
        print(f"   ReDoc: {base_url}/redoc")
        print(f"   Health Check: {base_url}/api/v8/health")
        print(f"   API Info: {base_url}/api/v8/info")
        
        print(f"\n🔐 AUTENTICAÇÃO DE TESTE:")
        print("   Use um dos Bearer Tokens:")
        print("   - Free: cp_demo_2025_free_tier")
        print("   - Pro: cp_pro_2025_advanced") 
        print("   - Enterprise: cp_enterprise_2025_unlimited")
        
        print(f"\n🎯 ENDPOINTS PRINCIPAIS:")
        print(f"   POST {base_url}/api/v8/analysis/brand - Análise completa")
        print(f"   POST {base_url}/api/v8/circles/analyze - Círculos culturais")
        print(f"   POST {base_url}/api/v8/tfidf/analyze - TF-IDF cultural")
        print(f"   POST {base_url}/api/v8/alma/analyze - Alma brasileira")
        
        print("\n🔥 API ONLINE! Press Ctrl+C to stop\n")
        
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        logger.info("🛑 API interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
