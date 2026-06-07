#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de Autenticação - Culture Pulse V9.1 (4 Tiers)
Sistema de autenticação baseado em Bearer Token

🎯 RESPONSABILIDADES:
- Validação de tokens de acesso
- Identificação de clientes (4 tiers: free/pro/executive/enterprise)
- Controle de permissões por hierarquia de plano
- Rate limiting por cliente (50/500/2000/10000 req/h)

Tiers:
  free       → R$ 0       (10 análises/mês, 1 usuário)
  pro        → R$ 6k/mês  (30 análises/mês, 2 usuários)
  executive  → R$ 14k/mês (60 análises/mês, 3 usuários)
  enterprise → R$ 25k/mês (100 análises/mês, 5 usuários)

Config centralizada: config/plan_config.py (PLAN_CONFIG)
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, Union
import jwt
import logging
import os
from datetime import datetime, timedelta

# Ambiente e controle de demo
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
ENABLE_DEMO_AUTH = os.getenv("ENABLE_DEMO_AUTH", "false").strip().lower() in ("1", "true", "yes", "y")
# Demo auth só é permitido quando explicitamente ativado; não há auto-fallback por ambiente.
ALLOW_DEMO_AUTH = ENABLE_DEMO_AUTH

# Importação para integração real com Supabase
from collectors.supabase_writer import _get_client as get_sb_client

logger = logging.getLogger(__name__)

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "culture_pulse_integrated_secret_key_2025")  # Em produção, usar variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security scheme
security = HTTPBearer()

# Simulação de banco de dados de clientes
# Em produção, isso viria de um banco de dados real (Supabase profiles)
# V9.1: 4 tiers — free / pro / executive / enterprise + ONBOARDING DATA (Momento)
CLIENTS_DB = {
    "client_demo": {
        "id": "client_demo",
        "name": "Cliente Demonstração",
        "email": "demo@culturepulse.com.br",
        "tier": "free",
        "rate_limit": 50,
        "active": True,
        "created_at": "2025-01-01",
        "api_key": "cp_demo_2025_free_tier",
        "onboarding": {
            "moment": "Exploração cultural inicial",
            "segment": "Geral",
            "brand": "Demo"
        }
    },
    "client_pro": {
        "id": "client_pro",
        "name": "Cliente Profissional",
        "email": "pro@culturepulse.com.br",
        "tier": "pro",
        "rate_limit": 500,
        "active": True,
        "created_at": "2025-01-01",
        "api_key": "cp_pro_2025_advanced",
        "onboarding": {
            "moment": "Expansão de mercado e novos públicos",
            "segment": "Tecnologia",
            "brand": "TechPro"
        }
    },
    "client_executive": {
        "id": "client_executive",
        "name": "Cliente Executivo",
        "email": "executive@culturepulse.com.br",
        "tier": "executive",
        "rate_limit": 2000,
        "active": True,
        "created_at": "2025-01-01",
        "api_key": "cp_executive_2025_premium",
        "onboarding": {
            "moment": "Rejuvenescimento urbano e conexão com periferia digital",
            "segment": "Calçados",
            "brand": "Nike Brasil"
        }
    },
    "client_enterprise": {
        "id": "client_enterprise",
        "name": "Cliente Enterprise",
        "email": "enterprise@culturepulse.com.br",
        "tier": "enterprise",
        "rate_limit": 10000,
        "active": True,
        "created_at": "2025-01-01",
        "api_key": "cp_enterprise_2025_unlimited",
        "onboarding": {
            "moment": "Transformação digital e inovação contínua",
            "segment": "Bancos",
            "brand": "Itaú"
        }
    }
}


class ClientInfo:
    """Informações do cliente autenticado"""
    def __init__(self, client_data: Dict[str, Any]):
        self.id = client_data["id"]
        self.name = client_data["name"]
        self.email = client_data["email"]
        self.tier = client_data["tier"]
        self.rate_limit = client_data["rate_limit"]
        self.active = client_data["active"]
        self.created_at = client_data["created_at"]
        self.api_key = client_data["api_key"]
        self.onboarding = client_data.get("onboarding", {
            "moment": "Geral",
            "segment": "Geral",
            "brand": "Geral"
        })


def create_access_token(client_id: str) -> str:
    """Cria token JWT para cliente (S4.2: inclui tier no payload)."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    # S4.2: incluir tier para que WebSocket _resolve_plan() funcione com JWT
    client_data = CLIENTS_DB.get(client_id, {})
    tier = client_data.get("tier", "free")

    payload = {
        "sub": client_id,
        "tier": tier,           # S4.2 — plano dentro do JWT
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access_token"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id = payload.get("sub")
        
        if client_id is None:
            return None
            
        return client_id
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError, Exception) as e:
        logger.warning(f"Erro JWT: {e}")
        return None


def verify_api_key(api_key: str) -> Optional[str]:
    """Verifica API key e retorna client_id"""
    for client_id, client_data in CLIENTS_DB.items():
        if client_data["api_key"] == api_key and client_data["active"]:
            return client_id
    return None


async def get_current_client(credentials: HTTPAuthorizationCredentials = Depends(security)) -> ClientInfo:
    """
    Dependency para obter cliente atual autenticado via Supabase ou Fallback
    """
    token = credentials.credentials
    
    # 1. TENTATIVE: INTEGRACAO REAL SUPABASE
    sb = get_sb_client()
    supabase_unavailable = False

    if sb:
        try:
            # Primeiro verificamos se é um JWT do Supabase (contém UID)
            user_id = verify_token(token)
            
            if user_id:
                # Busca perfil completo + dados de onboarding no Supabase
                # Nota: A tabela `profiles` pode armazenar campos de onboarding inline
                result = sb.table("profiles").select("*").eq("id", user_id).execute()
                
                if result.data and len(result.data) > 0:
                    profile = result.data[0]
                    onboarding_raw = profile.get("onboarding") or {
                        "moment": profile.get("onboarding_moment", "Geral"),
                        "segment": profile.get("onboarding_segment", "Geral"),
                        "brand": profile.get("onboarding_brand", "Geral")
                    }
                    
                    logger.info(f"✅ Cliente Supabase autenticado: {user_id}")
                    return ClientInfo({
                        "id": profile["id"],
                        "name": profile.get("full_name") or profile.get("email", "User"),
                        "email": profile.get("email"),
                        "tier": profile.get("plan", "free"),
                        "rate_limit": 100, # Default para Supabase real
                        "active": True,
                        "created_at": profile.get("created_at"),
                        "api_key": profile.get("api_token"),
                        "onboarding": {
                            "moment": onboarding_raw.get("moment", "Geral"),
                            "segment": onboarding_raw.get("segment", "Geral"),
                            "brand": onboarding_raw.get("brand", "Geral")
                        }
                    })
            
            # Se não for JWT, tentar como API Key no Supabase
            result_key = sb.table("profiles").select("*").eq("api_token", token).execute()
            if result_key.data and len(result_key.data) > 0:
                profile = result_key.data[0]
                onboarding_raw = profile.get("onboarding") or {
                    "moment": profile.get("onboarding_moment", "Geral"),
                    "segment": profile.get("onboarding_segment", "Geral"),
                    "brand": profile.get("onboarding_brand", "Geral")
                }
                
                return ClientInfo({
                    "id": profile["id"],
                    "name": profile.get("full_name") or profile.get("email", "User"),
                    "email": profile.get("email"),
                    "tier": profile.get("plan", "free"),
                    "rate_limit": 100,
                    "active": True,
                    "created_at": profile.get("created_at"),
                    "api_key": profile.get("api_token"),
                    "onboarding": {
                        "moment": onboarding_raw.get("moment", "Geral"),
                        "segment": onboarding_raw.get("segment", "Geral"),
                        "brand": onboarding_raw.get("brand", "Geral")
                    }
                })
        except Exception as e:
            logger.warning(f"⚠️ Supabase Auth offline ou erro: {str(e)}. Fallback para mock.")
            supabase_unavailable = True
    else:
        logger.warning("⚠️ Supabase client não configurado; fallback auth será usado se ENABLE_DEMO_AUTH=true.")
        supabase_unavailable = True

    logger.info(f"Auth fallback check token: {token}")
    logger.info(f"ALLOW_DEMO_AUTH={ALLOW_DEMO_AUTH}, ENVIRONMENT={ENVIRONMENT}, ENABLE_DEMO_AUTH={ENABLE_DEMO_AUTH}")
    if ALLOW_DEMO_AUTH:
        client_id = verify_api_key(token)
        logger.info(f"verify_api_key result: {client_id}")
        if client_id:
            client_data = CLIENTS_DB.get(client_id)
            if client_data and client_data["active"]:
                logger.info(f"Cliente (Mock API key) autenticado: {client_id} ({client_data['tier']})")
                return ClientInfo(client_data)

    if not ALLOW_DEMO_AUTH:
        if supabase_unavailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase authentication unavailable and demo auth disabled",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. FALLBACK: CLIENTS_DB (PARA TESTES LOCAIS/MOCK)
    client_id = verify_token(token)
    
    # Se não for JWT válido no mock, tentar como API key no mock
    if not client_id:
        client_id = verify_api_key(token)
    
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar dados do cliente no dicionário mock
    client_data = CLIENTS_DB.get(client_id)
    if not client_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente não encontrado"
        )
    
    if not client_data["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente inativo"
        )
    
    logger.info(f"Cliente (Mock) autenticado: {client_id} ({client_data['tier']})")
    return ClientInfo(client_data)


async def get_current_active_client(current_client: ClientInfo = Depends(get_current_client)) -> ClientInfo:
    """Dependency para garantir que cliente está ativo"""
    if not current_client.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente inativo"
        )
    return current_client


def require_tier(required_tier: str):
    """Decorator para exigir tier específico (4 tiers: free < pro < executive < enterprise)"""
    def tier_dependency(current_client: ClientInfo = Depends(get_current_client)) -> ClientInfo:
        tier_hierarchy = {
            "free": 0,
            "pro": 1,
            "executive": 2,
            "enterprise": 3
        }
        
        current_level = tier_hierarchy.get(current_client.tier, -1)
        required_level = tier_hierarchy.get(required_tier, 999)
        
        if current_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tier {required_tier} ou superior necessário"
            )
        
        return current_client
    
    return tier_dependency


# Funções utilitárias para autenticação
def get_client_by_id(client_id: str) -> Optional[Dict[str, Any]]:
    """Busca cliente por ID"""
    return CLIENTS_DB.get(client_id)


def authenticate_client(api_key: str) -> Optional[ClientInfo]:
    """Autentica cliente por API key"""
    client_id = verify_api_key(api_key)
    if not client_id:
        return None
    
    client_data = CLIENTS_DB.get(client_id)
    if not client_data or not client_data["active"]:
        return None
    
    return ClientInfo(client_data)


def generate_demo_tokens() -> Dict[str, str]:
    """Gera tokens de demonstração para todos os tiers"""
    tokens = {}
    
    for client_id in CLIENTS_DB.keys():
        tokens[client_id] = create_access_token(client_id)
    
    return tokens


# Para testes e demonstração
if __name__ == "__main__":
    # Gerar tokens de exemplo
    demo_tokens = generate_demo_tokens()
    
    print("🔐 TOKENS DE DEMONSTRAÇÃO - Culture Pulse V8.0")
    print("=" * 60)
    
    for client_id, token in demo_tokens.items():
        client = CLIENTS_DB[client_id]
        print(f"\n📋 {client['name']} ({client['tier'].upper()})")
        print(f"   API Key: {client['api_key']}")
        print(f"   JWT Token: {token[:50]}...")
        print(f"   Rate Limit: {client['rate_limit']} req/hour")
    
    print(f"\n💡 Use qualquer uma das opções acima como Bearer Token")
    print(f"   Exemplo: Authorization: Bearer {demo_tokens['client_demo'][:30]}...")
