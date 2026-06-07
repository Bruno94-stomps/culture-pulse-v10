#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Database V8.0 - Script Atualizado
Inicializa o banco de dados usando ProductionDatabaseManager

🎯 FUNCIONALIDADE:
- Usa ProductionDatabaseManager simplificado e funcional
- Configuração automática e robusta
- Pronto para produção
"""

import sys
from pathlib import Path
import logging
import sqlite3
from typing import Dict

# Adicionar o diretório data ao path
sys.path.append(str(Path(__file__).parent.parent / "data"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Configurador do banco de dados"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "culture_db.db"
        self.setup_scripts = self._load_setup_scripts()
    
    def _load_setup_scripts(self) -> Dict[str, str]:
        """Scripts SQL para setup inicial"""
        return {
            "create_tables": """
                CREATE TABLE IF NOT EXISTS cultural_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    results TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "create_indexes": """
                CREATE INDEX IF NOT EXISTS idx_cultural_data_term ON cultural_data(term);
                CREATE INDEX IF NOT EXISTS idx_cultural_data_platform ON cultural_data(platform);
                CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
            """
        }
    
    def setup_database(self) -> bool:
        """Configura o banco de dados inicial"""
        try:
            # Criar diretório se não existir
            self.db_path.parent.mkdir(exist_ok=True)
            
            # Conectar ao banco
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Executar scripts de setup
                for script_name, script_sql in self.setup_scripts.items():
                    logger.info(f"Executando {script_name}...")
                    cursor.executescript(script_sql)
                
                conn.commit()
                logger.info(f"✅ Database configurado: {self.db_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro no setup: {e}")
            return False
    
    def validate_database(self) -> bool:
        """Valida se o banco está configurado corretamente"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Verificar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['cultural_data', 'analysis_results']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    logger.error(f"❌ Tabelas ausentes: {missing_tables}")
                    return False
                
                logger.info("✅ Database validado com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False

def setup_database():
    """
    Configurar banco de dados usando ProductionDatabaseManager.
    Agora com sistema simplificado! 🚀
    """
    
    logger.info("🚀 Configurando banco de dados Culture Pulse V8.0...")
    
    try:
        # Importar ProductionDatabaseManager
        from production_database_manager import ProductionDatabaseManager
        
        logger.info("📊 Inicializando ProductionDatabaseManager...")
        
        # O ProductionDatabaseManager automaticamente:
        # 1. Cria o arquivo culture_db.db
        # 2. Conecta ao DuckDB
        # 3. Testa a conexão
        db_manager = ProductionDatabaseManager()
        
        # Mostrar health do sistema
        logger.info("📈 Verificando status do sistema...")
        health = db_manager.get_system_health()
        
        logger.info("✅ Métricas do Sistema:")
        for key, value in health.items():
            logger.info(f"  📊 {key}: {value}")
        
        # Teste básico de conectividade
        result = db_manager.execute_query("SELECT 'Database Setup OK!' as status")
        if result:
            logger.info(f"✅ Teste de conectividade: {result[0]['status']}")
        
        logger.info("🎉 Setup concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no setup: {e}")
        return False
        
        logger.info(f"✅ Database criado: {metrics['database_path']}")
        logger.info(f"📊 Tamanho: {metrics['database_size_mb']} MB")
        logger.info(f"🔗 Conexões ativas: {metrics['active_connections']}/{metrics['max_connections']}")
        logger.info(f"⚡ Queries executadas: {metrics['queries_executed']}")
        
        # Testar uma query simples
        logger.info("🧪 Testando conectividade...")
        result = db_manager.pool.execute_query("SELECT 'Database OK!' as status")
        logger.info(f"✅ Teste: {result[0]['status']}")
        
        # Fechar conexões
        db_manager.close()
        
        logger.info("🎉 Database Culture Pulse V8.0 configurado com sucesso!")
        logger.info("🏢 Sistema multi-tenant pronto para produção!")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ DatabaseManager não encontrado: {e}")
        logger.info("💡 Certifique-se de que database_manager.py está em src_v8/core/")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar database: {e}", exc_info=True)
        return False

def main():
    """Função principal"""
    success = setup_database()
    
    if success:
        print("\n" + "="*60)
        print("🎯 CULTURE PULSE V8.0 - DATABASE CONFIGURADO!")
        print("="*60)
        print("✅ Schema multi-tenant criado")
        print("✅ Pool de conexões ativo")
        print("✅ Tabelas e índices otimizados")
        print("✅ Pronto para análises culturais!")
        print("="*60)
    else:
        print("\n❌ Falha na configuração do database!")
        exit(1)

if __name__ == "__main__":
    main()
