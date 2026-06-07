#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Autenticação - Culture Pulse V8.0
Módulo para gerenciar usuários e sessões no dashboard

🔐 FUNCIONALIDADES:
- Login/Logout
- Gestão de sessões
- Controle de acesso por perfil
- Auditoria de ações
"""

import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import uuid

SESSION_STORE = defaultdict(dict)

# Base de usuários (em produção, usar banco de dados)
USERS_DB = {
    "admin": {
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "role": "admin",
        "name": "Administrador",
        "email": "admin@culturepulse.com",
        "created_at": "2025-01-01T00:00:00",
        "last_login": None,
        "permissions": ["read", "write", "admin", "export", "alerts"]
    },
    "analyst": {
        "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "analyst123"
        "role": "analyst",
        "name": "Analista Cultural",
        "email": "analyst@culturepulse.com",
        "created_at": "2025-01-01T00:00:00",
        "last_login": None,
        "permissions": ["read", "write", "export"]
    },
    "viewer": {
        "password": "3d4f2bf07dc1be38b20cd6e46949a1071f9d0e3d06a1b2c4e5f6789012345678",  # "viewer123"
        "role": "viewer",
        "name": "Visualizador",
        "email": "viewer@culturepulse.com",
        "created_at": "2025-01-01T00:00:00",
        "last_login": None,
        "permissions": ["read"]
    }
}

class AuthenticationManager:
    """Gerenciador de autenticação"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hora
        self.max_login_attempts = 3
        self.lockout_duration = 300  # 5 minutos
        self.username = None
        
    def hash_password(self, password: str) -> str:
        """Gerar hash da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar senha"""
        return self.hash_password(password) == hashed
    
    def get_user(self, username: str) -> dict:
        """Obter dados do usuário"""
        return USERS_DB.get(username)
    
    def authenticate(self, username: str, password: str) -> dict:
        """Autenticar usuário"""
        user = self.get_user(username)
        
        if not user:
            return {"success": False, "message": "Usuário não encontrado"}
        
        # Verificar tentativas de login
        attempts_key = f"login_attempts_{username}"
        lockout_key = f"lockout_until_{username}"
        
        session_state = SESSION_STORE[username]
        if lockout_key in session_state:
            if time.time() < session_state[lockout_key]:
                remaining = int(session_state[lockout_key] - time.time())
                return {"success": False, "message": f"Conta bloqueada. Tente novamente em {remaining}s"}
            else:
                # Lockout expirou
                del session_state[lockout_key]
                if attempts_key in session_state:
                    del session_state[attempts_key]
        
        if not self.verify_password(password, user["password"]):
            # Incrementar tentativas
            attempts = session_state.get(attempts_key, 0) + 1
            session_state[attempts_key] = attempts
            
            if attempts >= self.max_login_attempts:
                session_state[lockout_key] = time.time() + self.lockout_duration
                return {"success": False, "message": f"Muitas tentativas. Conta bloqueada por {self.lockout_duration//60} minutos"}
            
            return {"success": False, "message": f"Senha incorreta. {self.max_login_attempts - attempts} tentativas restantes"}
        
        # Login bem-sucedido
        if attempts_key in session_state:
            del session_state[attempts_key]
        
        # Atualizar último login
        USERS_DB[username]["last_login"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "user": user,
            "message": "Login realizado com sucesso"
        }
    
    def create_session(self, username: str, user_data: dict):
        """Criar sessão do usuário"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "username": username,
            "user_data": user_data,
            "login_time": time.time(),
            "last_activity": time.time(),
            "authenticated": True
        }
        
        SESSION_STORE[username].update(session_data)
        self.username = username
    
    def is_authenticated(self) -> bool:
        """Verificar se usuário está autenticado"""
        if not self.username:
            return False

        session_state = SESSION_STORE.get(self.username, {})
        if not session_state.get("authenticated", False):
            return False
        
        # Verificar timeout da sessão
        last_activity = session_state.get("last_activity", 0)
        if time.time() - last_activity > self.session_timeout:
            self.logout()
            return False
        
        # Atualizar última atividade
        session_state["last_activity"] = time.time()
        return True
    
    def logout(self):
        """Fazer logout"""
        if not self.username:
            return

        session_state = SESSION_STORE.get(self.username, {})
        keys_to_remove = [
            "authenticated", "session_id", "username", "user_data",
            "login_time", "last_activity"
        ]

        for key in keys_to_remove:
            session_state.pop(key, None)

        self.username = None
    
    def get_current_user(self) -> dict:
        """Obter usuário atual"""
        if self.is_authenticated():
            return SESSION_STORE.get(self.username, {}).get("user_data", {})
        return None
    
    def has_permission(self, permission: str) -> bool:
        """Verificar se usuário tem permissão"""
        user = self.get_current_user()
        if not user:
            return False
        
        return permission in user.get("permissions", [])
    
    def require_permission(self, permission: str):
        """Retorna True se permissão permitida"""
        return self.has_permission(permission)


# Viable backend helpers exposed for authentication.

# Instância global
auth_manager = AuthenticationManager()


def get_current_user():
    """Obter usuário atual (função de conveniência)"""
    return auth_manager.get_current_user()


def has_permission(permission: str) -> bool:
    """Verificar permissão (função de conveniência)"""
    return auth_manager.has_permission(permission)
