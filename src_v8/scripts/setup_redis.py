#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Setup Redis - Culture Pulse V9.0
Inicializa Redis para cache distribuído

Este script ajuda a configurar o Redis para melhor performance do sistema.
"""

import subprocess
import sys
import time
import os

def check_docker():
    """Verifica se Docker está disponível"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def check_redis():
    """Verifica se Redis está rodando"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        return True
    except:
        return False

def start_redis_docker():
    """Inicia Redis via Docker"""
    print("🚀 Iniciando Redis via Docker...")
    
    # Verificar se container já existe
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=redis-culture-pulse'], 
                              capture_output=True, text=True)
        if 'redis-culture-pulse' in result.stdout:
            print("📦 Container Redis já existe. Iniciando...")
            subprocess.run(['docker', 'start', 'redis-culture-pulse'])
        else:
            print("📦 Criando novo container Redis...")
            subprocess.run([
                'docker', 'run', '-d', 
                '--name', 'redis-culture-pulse',
                '-p', '6379:6379',
                'redis:7-alpine'
            ])
        
        print("⏳ Aguardando Redis inicializar...")
        time.sleep(3)
        
        if check_redis():
            print("✅ Redis iniciado com sucesso!")
            return True
        else:
            print("❌ Falha ao iniciar Redis")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar Redis: {e}")
        return False

def install_redis_windows():
    """Instruções para instalar Redis no Windows"""
    print("\n📋 Para instalar Redis no Windows:")
    print("1. Via Chocolatey:")
    print("   choco install redis-64")
    print("\n2. Via WSL2:")
    print("   wsl --install")
    print("   sudo apt install redis-server")
    print("\n3. Via Docker (recomendado):")
    print("   docker run -d -p 6379:6379 redis:alpine")

def main():
    print("🔧 Setup Redis para Culture Pulse V9.0")
    print("=" * 50)
    
    # Verificar se Redis já está rodando
    if check_redis():
        print("✅ Redis já está rodando e acessível!")
        print("📍 URL: redis://localhost:6379")
        return
    
    print("📍 Redis não detectado. Verificando opções...")
    
    # Verificar Docker
    if check_docker():
        print("🐳 Docker disponível. Iniciando Redis...")
        if start_redis_docker():
            print("\n✅ Setup concluído!")
            print("📍 Redis URL: redis://localhost:6379")
            print("🔄 Para parar: docker stop redis-culture-pulse")
            print("🔄 Para iniciar: docker start redis-culture-pulse")
        else:
            print("\n❌ Falha ao iniciar Redis via Docker")
            install_redis_windows()
    else:
        print("🐳 Docker não disponível.")
        install_redis_windows()
    
    print("\n💡 O sistema funcionará com cache local se Redis não estiver disponível.")
    print("💡 Redis é opcional mas recomendado para melhor performance em produção.")

if __name__ == "__main__":
    main()
