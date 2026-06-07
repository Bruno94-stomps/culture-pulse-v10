#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plans & Configuration Endpoint V9.9
Fornece metadados dinâmicos para o PlanGate.tsx e Dashboard
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

try:
    from config.plan_config import PLAN_CONFIG, VALID_TIERS
except ImportError:
    try:
        from src_v8.config.plan_config import PLAN_CONFIG, VALID_TIERS
    except ImportError:
        raise

try:
    from api.middleware.auth import get_current_client, ClientInfo
except ImportError:
    from src_v8.api.middleware.auth import get_current_client, ClientInfo

router = APIRouter(prefix="/plans", tags=["Configuration"])

@router.get("/")
async def get_plans_config():
    """
    Retorna a configuração completa de tiers para o frontend.
    Usado pelo PlanGate.tsx para renderizar limites e preços.
    """
    return {
        "tiers": PLAN_CONFIG,
        "valid_tiers": VALID_TIERS,
        "version": "9.9",
        "features_metadata": {
            "evidence_urls": "Visualização de links originais e provas de veracidade",
            "data_lag_hours": "Atraso na entrega de dados em relação ao tempo real",
            "reliability_visible": "Acesso aos scores de acurácia biográfica"
        }
    }

@router.get("/my-plan")
async def get_user_plan_details(current_client: ClientInfo = Depends(get_current_client)):
    """
    Retorna os detalhes do plano do usuário logado.
    """
    plan_details = PLAN_CONFIG.get(current_client.tier, PLAN_CONFIG.get("free"))
    return {
        "tier": current_client.tier,
        "details": plan_details,
        "user": {
            "id": current_client.id,
            "name": current_client.name,
            "email": current_client.email,
            "onboarding": current_client.onboarding,
        }
    }
