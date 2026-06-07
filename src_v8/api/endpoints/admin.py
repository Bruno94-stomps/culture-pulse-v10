#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin API Endpoints - Culture Pulse V3.0
Endpoints REST para administração de usuários, clientes e planos

🎯 ENDPOINTS:
- POST /api/v3/admin/clients - Criar cliente
- GET /api/v3/admin/clients - Listar clientes
- GET /api/v3/admin/clients/{client_id} - Obter cliente
- PUT /api/v3/admin/clients/{client_id} - Atualizar cliente
- DELETE /api/v3/admin/clients/{client_id} - Deletar cliente
- POST /api/v3/admin/clients/{client_id}/tier - Mudar tier
- GET /api/v3/admin/stats - Estatísticas gerais
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from auth.jwt_manager import JWTManager, TokenTier, TokenPayload

# Modelos Pydantic
class ClientCreate(BaseModel):
    """Modelo para criar cliente"""
    client_id: str
    name: str
    email: str
    tier: str = "free"
    metadata: Optional[Dict[str, Any]] = None


class ClientUpdate(BaseModel):
    """Modelo para atualizar cliente"""
    name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ClientTierUpdate(BaseModel):
    """Modelo para atualizar tier"""
    tier: str


class ClientResponse(BaseModel):
    """Resposta com dados do cliente"""
    client_id: str
    name: str
    email: str
    tier: str
    created_at: str
    updated_at: str
    metadata: Optional[Dict[str, Any]] = None


class StatsResponse(BaseModel):
    """Resposta com estatísticas"""
    total_clients: int
    by_tier: Dict[str, int]
    total_users: int
    last_updated: str


# Database simulada (em produção seria PostgreSQL)
class ClientDatabase:
    """Database simulada para clientes"""
    
    def __init__(self):
        self.clients: Dict[str, Dict[str, Any]] = {}
    
    def create_client(self, client_id: str, name: str, email: str, tier: str = "free") -> Dict[str, Any]:
        """Criar cliente"""
        if client_id in self.clients:
            raise ValueError(f"Cliente {client_id} já existe")
        
        client = {
            "client_id": client_id,
            "name": name,
            "email": email,
            "tier": tier,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {},
        }
        
        self.clients[client_id] = client
        return client
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Obter cliente"""
        return self.clients.get(client_id)
    
    def list_clients(self) -> List[Dict[str, Any]]:
        """Listar clientes"""
        return list(self.clients.values())
    
    def update_client(self, client_id: str, **kwargs) -> Dict[str, Any]:
        """Atualizar cliente"""
        if client_id not in self.clients:
            raise ValueError(f"Cliente {client_id} não encontrado")
        
        client = self.clients[client_id]
        client.update(kwargs)
        client["updated_at"] = datetime.utcnow().isoformat()
        
        return client
    
    def delete_client(self, client_id: str) -> bool:
        """Deletar cliente"""
        if client_id in self.clients:
            del self.clients[client_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas"""
        tiers = {}
        for client in self.clients.values():
            tier = client.get("tier", "free")
            tiers[tier] = tiers.get(tier, 0) + 1
        
        return {
            "total_clients": len(self.clients),
            "by_tier": tiers,
            "total_users": len(self.clients) * 10,  # Estimativa
            "last_updated": datetime.utcnow().isoformat(),
        }


# Instâncias globais
db = ClientDatabase()
jwt_manager = JWTManager()
router = APIRouter(prefix="/api/v3/admin", tags=["admin"])


# Dependências
async def require_admin_token(token: Optional[str] = None) -> TokenPayload:
    """Verificar se token é de admin"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )
    
    # Remover "Bearer " do token se presente
    if token.startswith("Bearer "):
        token = token[7:]
    
    is_valid, payload, error = jwt_manager.verify_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Token inválido"
        )
    
    # Apenas ENTERPRISE pode ser admin
    if payload.tier != TokenTier.ENTERPRISE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes ENTERPRISE podem acessar admin"
        )
    
    return payload


# Endpoints
@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    admin: TokenPayload = Depends(require_admin_token)
) -> ClientResponse:
    """Criar novo cliente"""
    try:
        client = db.create_client(
            client_id=client_data.client_id,
            name=client_data.name,
            email=client_data.email,
            tier=client_data.tier
        )
        
        if client_data.metadata:
            client["metadata"] = client_data.metadata
        
        return ClientResponse(**client)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    admin: TokenPayload = Depends(require_admin_token)
) -> List[ClientResponse]:
    """Listar clientes"""
    clients = db.list_clients()
    return [ClientResponse(**client) for client in clients]


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    admin: TokenPayload = Depends(require_admin_token)
) -> ClientResponse:
    """Obter cliente específico"""
    client = db.get_client(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} não encontrado"
        )
    
    return ClientResponse(**client)


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    admin: TokenPayload = Depends(require_admin_token)
) -> ClientResponse:
    """Atualizar cliente"""
    try:
        update_data = client_data.dict(exclude_unset=True)
        client = db.update_client(client_id, **update_data)
        return ClientResponse(**client)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: str,
    admin: TokenPayload = Depends(require_admin_token)
) -> Dict[str, str]:
    """Deletar cliente"""
    if db.delete_client(client_id):
        return {"message": f"Cliente {client_id} deletado"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cliente {client_id} não encontrado"
    )


@router.post("/clients/{client_id}/tier")
async def update_client_tier(
    client_id: str,
    tier_data: ClientTierUpdate,
    admin: TokenPayload = Depends(require_admin_token)
) -> ClientResponse:
    """Atualizar tier de cliente"""
    try:
        # Validar tier
        if tier_data.tier not in ["free", "pro", "enterprise"]:
            raise ValueError("Tier inválido. Use: free, pro ou enterprise")
        
        client = db.update_client(client_id, tier=tier_data.tier)
        return ClientResponse(**client)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    admin: TokenPayload = Depends(require_admin_token)
) -> StatsResponse:
    """Obter estatísticas"""
    stats = db.get_stats()
    return StatsResponse(**stats)


# Export
__all__ = ["router", "db", "jwt_manager"]
