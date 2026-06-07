#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FastAPI endpoints para perfis emergentes no dashboard."""

import logging
import os
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from collectors.supabase_writer import _get_client as _get_supabase_client, health_check as _supabase_health_check
from core.intelligence.emerging_profiles_engine import detect_emerging_profiles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v8/dashboard/emerging-profiles", tags=["Emerging Profiles"])


class EmergingProfile(BaseModel):
    name: str = Field(..., description="Nome do perfil emergente")
    category: Optional[str] = Field(None, description="Categoria ou segmento do perfil")
    emergence_score: float = Field(..., description="Score de emergência do perfil")
    growth_velocity: Optional[float] = Field(None, description="Velocidade de crescimento")
    uniqueness_index: Optional[float] = Field(None, description="Índice de unicidade")
    stability_score: Optional[float] = Field(None, description="Score de estabilidade do perfil")
    summary: Optional[str] = Field(None, description="Resumo curto do perfil")


class EmergingProfilesResponse(BaseModel):
    status: str = Field(..., description="Status da requisição")
    data: List[EmergingProfile] = Field(..., description="Lista de perfis emergentes")
    count: int = Field(..., description="Quantidade de perfis retornados")
    plan: str = Field(..., description="Plano usado para geração dos perfis")
    top_n: int = Field(..., description="Número máximo de perfis retornados")


class EmergingProfilesStatusResponse(BaseModel):
    status: str = Field(..., description="Status do serviço de perfis emergentes")
    available: bool = Field(..., description="Se o serviço está disponível")
    last_refresh: Optional[str] = Field(None, description="Timestamp da última atualização")
    message: Optional[str] = Field(None, description="Mensagem de diagnóstico")
    supabase_health: Optional[str] = Field(None, description="Estado do Supabase")
    supabase_dns: Optional[str] = Field(None, description="Resultado do DNS para SUPABASE_URL")
    redis_health: Optional[str] = Field(None, description="Estado do Redis local")


def _load_project_context(project_id: Optional[str]) -> Dict[str, Any]:
    if not project_id:
        return {}

    client = _get_supabase_client()
    if not client:
        return {}

    try:
        result = client.table("projects").select("*").eq("id", project_id).limit(1).execute()
        if result.data and len(result.data) > 0:
            project = result.data[0]
            return {
                "id": project.get("id"),
                "name": project.get("name"),
                "brand": project.get("brand"),
                "segment": project.get("segment"),
                "keywords": project.get("keywords") or [],
                "regions": project.get("regions") or [],
                "audiences": project.get("audiences") or [],
                "circles": project.get("circles") or [],
                "period_days": project.get("period_days"),
            }
    except Exception as exc:
        logger.warning("Falha ao carregar contexto de projeto Supabase: %s", exc)

    return {}


def _load_enriched_signals(plan: str, count: int, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    try:
        from core.intelligence.enriched_reader import EnrichedDataReader

        reader = EnrichedDataReader()
        signals = reader.get_signals(plan=plan, count=count, context=context, use_realtime_api=True)
        if signals is None:
            return []
        return signals
    except Exception as exc:
        logger.error("Erro ao carregar dados enriquecidos para perfis emergentes: %s", exc)
        raise HTTPException(status_code=500, detail="Falha ao carregar dados de sinais enriquecidos")


def _normalize_profile(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": item.get("name", "Perfil emergente"),
        "category": item.get("category") or item.get("circle") or "Emergente",
        "emergence_score": float(item.get("relevance", 0)) / 100.0,
        "growth_velocity": float(item.get("growth", "+0%" ).strip("+%")) if item.get("growth") else None,
        "uniqueness_index": None,
        "stability_score": None,
        "summary": item.get("description") or item.get("summary") or "Perfil derivado de sinais culturais.",
    }


def _resolve_supabase_dns(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or url
        ip = socket.gethostbyname(host)
        return f"{host} -> {ip}"
    except Exception as exc:
        return f"DNS lookup failed: {exc}"


def _check_redis_health() -> str:
    try:
        from core.intelligence.enriched_reader import EnrichedDataReader
        reader = EnrichedDataReader()
        redis_client = reader._get_sync_redis()
        if redis_client is None:
            return "Redis unavailable or disconnected"
        return "Redis available"
    except Exception as exc:
        return f"Redis health check failed: {exc}"


@router.get("/", response_model=EmergingProfilesResponse)
async def get_emerging_profiles(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    top_n: int = Query(6, ge=1, le=50),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
):
    """Retorna perfis emergentes derivados de dados enriquecidos."""
    try:
        project_context = _load_project_context(project_id)
        context = {
            "project_id": project_id,
            "user_tier": plan,
            "onboarding": project_context,
            "keywords": project_context.get("keywords", []),
        }

        signals = _load_enriched_signals(plan, count, context)
        if project_id:
            signals = [s for s in signals if str(s.get("project_id")) == str(project_id)]

        result = detect_emerging_profiles(signals, top_n=top_n)

        return EmergingProfilesResponse(
            status="success",
            data=[EmergingProfile(**_normalize_profile(item)) for item in result],
            count=len(result),
            plan=plan,
            top_n=top_n,
        )
    except Exception as exc:
        logger.error("GET /api/v8/dashboard/emerging-profiles error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/refresh", response_model=EmergingProfilesResponse)
async def refresh_emerging_profiles(
    plan: str = Query("free"),
    count: int = Query(50, ge=1, le=500),
    top_n: int = Query(6, ge=1, le=50),
    project_id: Optional[str] = Query(None, description="ID do projeto para filtrar sinais relacionados"),
):
    """Recalcula perfis emergentes a partir dos dados mais recentes."""
    try:
        project_context = _load_project_context(project_id)
        context = {
            "project_id": project_id,
            "user_tier": plan,
            "onboarding": project_context,
            "keywords": project_context.get("keywords", []),
        }

        signals = _load_enriched_signals(plan, count, context)
        result = detect_emerging_profiles(signals, top_n=top_n)

        return EmergingProfilesResponse(
            status="refreshed",
            data=[EmergingProfile(**_normalize_profile(item)) for item in result],
            count=len(result),
            plan=plan,
            top_n=top_n,
        )
    except Exception as exc:
        logger.error("POST /api/v8/dashboard/emerging-profiles/refresh error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/status", response_model=EmergingProfilesStatusResponse)
async def emerging_profiles_status():
    """Retorna o status do serviço de perfis emergentes."""
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    dns_result = _resolve_supabase_dns(supabase_url) if supabase_url else "SUPABASE_URL not configured"
    try:
        health = _supabase_health_check()
        supabase_health = f"{health.get('status')} - {health.get('details', '')}"
    except Exception as exc:
        supabase_health = f"health check failed: {exc}"

    redis_health = _check_redis_health()

    return EmergingProfilesStatusResponse(
        status="ready",
        available=True,
        last_refresh=None,
        message="Serviço de perfis emergentes disponível",
        supabase_health=supabase_health,
        supabase_dns=dns_result,
        redis_health=redis_health,
    )
