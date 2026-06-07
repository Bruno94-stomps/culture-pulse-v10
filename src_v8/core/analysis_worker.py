#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Worker — Culture Pulse V9.1
======================================
Worker assíncrono que escuta sinais crus do Redis (canal `signals:raw`),
executa uma cadeia de análise configurável (engines plugáveis), e publica
o resultado enriquecido de volta no Redis para que o WebSocket entregue
como evento `enrichment`.

Arquitetura:
    ┌───────────────┐     signals:raw      ┌──────────────────┐
    │ SignalPublisher│ ──────────────────── │  AnalysisWorker  │
    │ (coleta/write) │                      │  ├── Engine A    │
    └───────────────┘                      │  ├── Engine B    │
                                           │  └── Engine N    │
                                           └──────┬───────────┘
                                                  │ enriched
                                                  ▼
                                     signals:enriched:{plan}
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │  WebSocket   │
                                           │  (streaming) │
                                           └─────────────┘

Pipeline Registry:
    Cada engine é uma callable que recebe um dict (sinal) e retorna um dict
    (sinal enriquecido). Engines são registradas no worker e executadas em
    ordem. Se uma engine falha, o sinal prossegue sem aquele enriquecimento.

    worker = AnalysisWorker()
    worker.register("circles", circles_enricher, priority=10)
    worker.register("tfidf", tfidf_enricher, priority=20)
    worker.register("sentiment", sentiment_enricher, priority=30)
    await worker.start()

Canais Redis:
    signals:raw                     — sinais crus (publicados pelo SignalPublisher)
    signals:enriched:free           — sinais enriquecidos para plano Free
    signals:enriched:pro            — sinais enriquecidos para plano Pro
    signals:enriched:enterprise     — sinais enriquecidos para plano Enterprise

Env vars:
    REDIS_URL           = redis://localhost:6379/0
    WORKER_CONCURRENCY  = 4  (máx sinais processados em paralelo)
    WORKER_TIMEOUT      = 10 (timeout por engine em segundos)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# ── Redis import ─────────────────────────────────────────────────────────────
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis  # type: ignore
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logger.warning("⚠️  Redis não disponível — AnalysisWorker inativo")

# ── Constantes ────────────────────────────────────────────────────────────────

RAW_CHANNEL = "signals:raw"

ENRICHED_CHANNELS: Dict[str, str] = {
    "free":       "signals:enriched:free",
    "pro":        "signals:enriched:pro",
    "enterprise": "signals:enriched:enterprise",
}

ENRICHED_BUFFERS: Dict[str, str] = {
    "free":       "buffer:enriched:free",
    "pro":        "buffer:enriched:pro",
    "enterprise": "buffer:enriched:enterprise",
}

ENRICHED_BUFFER_MAX: Dict[str, int] = {
    "free":       50,
    "pro":        500,
    "enterprise": 5000,
}

ENRICHED_BUFFER_TTL: Dict[str, int] = {
    "free":       3600,
    "pro":        86400,
    "enterprise": 0,
}

DEFAULT_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
DEFAULT_TIMEOUT = float(os.getenv("WORKER_TIMEOUT", "10"))


# ── Engine Registration ──────────────────────────────────────────────────────

# Engine callable: recebe (signal_dict) → retorna (signal_dict enriquecido)
# Pode ser sync ou async
EngineFn = Union[
    Callable[[dict], dict],
    Callable[[dict], Coroutine[Any, Any, dict]],
]


@dataclass
class RegisteredEngine:
    """Engine registrada no pipeline do worker."""
    name: str
    fn: EngineFn
    priority: int = 50          # menor = executa primeiro
    timeout: float = DEFAULT_TIMEOUT
    required: bool = False      # se True, falha interrompe pipeline
    enabled: bool = True

    def __lt__(self, other):
        return self.priority < other.priority


# ── INT-B: Multiplicadores de velocidade por círculo cultural ────────────────
# >1.0 = velocidade nesse círculo é naturalmente maior (ajustar para baixo)
# <1.0 = velocidade nesse círculo é naturalmente mais lenta (ajustar para cima)
CIRCLE_VELOCITY_BASELINE = {
    "Humor & Memes": 1.4,       # viral é o normal
    "Esporte": 1.3,             # eventos geram spikes
    "Música Popular": 1.2,      # trends rápidos
    "Festas & Eventos": 1.2,    # sazonal + picos
    "Cinema & Séries": 1.1,     # lançamentos viralizam
    "Tecnologia": 1.1,          # hype cycles
    "Moda & Estilo": 1.0,       # baseline
    "Gastronomia": 0.9,         # tendências mais lentas
    "Arte Urbana": 0.9,         # nicho porém persistente
    "Empreendedorismo": 0.9,    # ciclos mais longos
    "Saúde & Bem-Estar": 0.85,  # adoção gradual
    "Educação": 0.8,            # transformação lenta
    "Mobilidade Urbana": 0.8,   # mudanças estruturais
    "Literatura": 0.75,         # movimentos lentos
    "Natureza": 0.75,           # awareness gradual
    "Religiosidade": 0.7,       # mudanças muito lentas
}


# ── AnalysisWorker ───────────────────────────────────────────────────────────

class AnalysisWorker:
    """
    Worker assíncrono: escuta signals:raw → executa pipeline → publica enriched.

    Uso:
        worker = AnalysisWorker()
        worker.register("circles", circles_enricher, priority=10)
        worker.register("tfidf", tfidf_enricher, priority=20)
        await worker.start()   # bloqueia até Ctrl+C ou stop()
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        concurrency: int = DEFAULT_CONCURRENCY,
        default_timeout: float = DEFAULT_TIMEOUT,
    ):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._concurrency = concurrency
        self._default_timeout = default_timeout
        self._engines: List[RegisteredEngine] = []
        self._running = False
        self._redis: Optional[object] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._stats: Dict[str, Any] = {
            "processed": 0,
            "enriched": 0,
            "errors": 0,
            "engine_stats": {},
            "started_at": None,
        }

    # ── Registry ─────────────────────────────────────────────────────────

    def register(
        self,
        name: str,
        fn: EngineFn,
        priority: int = 50,
        timeout: Optional[float] = None,
        required: bool = False,
        enabled: bool = True,
    ) -> "AnalysisWorker":
        """
        Registra uma engine no pipeline.
        Engines são executadas em ordem de prioridade (menor = primeiro).

        Args:
            name:     Identificador da engine (ex: "circles", "tfidf")
            fn:       Callable(signal_dict) → signal_dict enriquecido (sync ou async)
            priority: Ordem de execução (10, 20, 30...). Menor executa primeiro.
            timeout:  Timeout em segundos para esta engine. None = default.
            required: Se True, falha nesta engine aborta o pipeline todo.
            enabled:  Se False, engine é ignorada (útil para toggle dinâmico).

        Returns:
            self (para chaining)
        """
        engine = RegisteredEngine(
            name=name,
            fn=fn,
            priority=priority,
            timeout=timeout or self._default_timeout,
            required=required,
            enabled=enabled,
        )
        self._engines.append(engine)
        self._engines.sort()  # ordena por prioridade
        self._stats["engine_stats"][name] = {
            "calls": 0, "success": 0, "errors": 0, "total_time": 0.0
        }
        logger.info(f"🔧 Engine registrada: {name} (prioridade={priority})")
        return self

    def unregister(self, name: str) -> "AnalysisWorker":
        """Remove engine do pipeline."""
        self._engines = [e for e in self._engines if e.name != name]
        return self

    def enable(self, name: str) -> "AnalysisWorker":
        """Ativa engine por nome."""
        for e in self._engines:
            if e.name == name:
                e.enabled = True
        return self

    def disable(self, name: str) -> "AnalysisWorker":
        """Desativa engine por nome."""
        for e in self._engines:
            if e.name == name:
                e.enabled = False
        return self

    @property
    def pipeline_info(self) -> List[dict]:
        """Retorna info das engines registradas (em ordem de execução)."""
        return [
            {"name": e.name, "priority": e.priority, "enabled": e.enabled,
             "required": e.required, "timeout": e.timeout}
            for e in self._engines
        ]

    # ── Pipeline execution ───────────────────────────────────────────────

    async def _run_engine(self, engine: RegisteredEngine, signal: dict) -> dict:
        """Executa uma engine com timeout e error handling."""
        stats = self._stats["engine_stats"].get(engine.name, {})
        stats["calls"] = stats.get("calls", 0) + 1
        t0 = time.time()

        try:
            result = engine.fn(signal)
            if asyncio.iscoroutine(result) or asyncio.isfuture(result):
                result = await asyncio.wait_for(result, timeout=engine.timeout)
            elif asyncio.iscoroutinefunction(engine.fn):
                result = await asyncio.wait_for(engine.fn(signal), timeout=engine.timeout)

            elapsed = time.time() - t0
            stats["success"] = stats.get("success", 0) + 1
            stats["total_time"] = stats.get("total_time", 0.0) + elapsed
            return result if isinstance(result, dict) else signal

        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Engine {engine.name} timeout ({engine.timeout}s)")
            stats["errors"] = stats.get("errors", 0) + 1
            if engine.required:
                raise
            return signal

        except Exception as exc:
            logger.warning(f"⚠️ Engine {engine.name} falhou: {exc}")
            stats["errors"] = stats.get("errors", 0) + 1
            if engine.required:
                raise
            return signal

    async def enrich(self, signal: dict) -> dict:
        """
        Executa o pipeline completo sobre um sinal.
        Pode ser chamado diretamente (sem Redis) para testes.
        """
        enriched = {**signal}
        enriched["_enrichment"] = {
            "started_at": time.time(),
            "engines_applied": [],
            "engines_failed": [],
        }

        for engine in self._engines:
            if not engine.enabled:
                continue
            try:
                enriched = await self._run_engine(engine, enriched)
                enriched["_enrichment"]["engines_applied"].append(engine.name)
            except Exception:
                enriched["_enrichment"]["engines_failed"].append(engine.name)
                break  # engine required falhou — interrompe pipeline

        enriched["_enrichment"]["finished_at"] = time.time()
        enriched["_enrichment"]["duration"] = (
            enriched["_enrichment"]["finished_at"] - enriched["_enrichment"]["started_at"]
        )
        return enriched

    # ── Redis connection ─────────────────────────────────────────────────

    async def _get_redis(self):
        """Obtém ou cria conexão Redis."""
        if self._redis is not None:
            try:
                await self._redis.ping()  # type: ignore
                return self._redis
            except Exception:
                self._redis = None

        if not REDIS_AVAILABLE:
            return None

        try:
            self._redis = await aioredis.from_url(
                self._redis_url, decode_responses=True
            )
            await self._redis.ping()  # type: ignore
            logger.info(f"✅ AnalysisWorker conectado ao Redis: {self._redis_url}")
            return self._redis
        except Exception as exc:
            logger.warning(f"⚠️ Redis indisponível: {exc}")
            return None

    # ── Publish enriched ─────────────────────────────────────────────────

    async def _publish_enriched(self, enriched: dict):
        """Publica sinal enriquecido em todos os canais enriched + buffers."""
        r = await self._get_redis()
        if r is None:
            return

        payload_json = json.dumps(enriched, ensure_ascii=False, default=str)

        try:
            # Pub/Sub — publish em canais enriched
            for plan, channel in ENRICHED_CHANNELS.items():
                await r.publish(channel, payload_json)  # type: ignore

            # Buffer List — LPUSH + LTRIM para cada plano
            for plan, buffer_key in ENRICHED_BUFFERS.items():
                await r.lpush(buffer_key, payload_json)  # type: ignore
                await r.ltrim(buffer_key, 0, ENRICHED_BUFFER_MAX[plan] - 1)  # type: ignore
                ttl = ENRICHED_BUFFER_TTL[plan]
                if ttl > 0:
                    await r.expire(buffer_key, ttl)  # type: ignore

            self._stats["enriched"] += 1
        except Exception as exc:
            logger.warning(f"⚠️ Erro ao publicar enriched: {exc}")

    # ── Process single signal ────────────────────────────────────────────

    async def _process_signal(self, raw_json: str):
        """Processa um sinal cru: parse → enrich → publish."""
        async with self._semaphore:  # type: ignore
            try:
                signal = json.loads(raw_json)
                enriched = await self.enrich(signal)
                await self._publish_enriched(enriched)
                self._stats["processed"] += 1
            except json.JSONDecodeError as exc:
                logger.warning(f"⚠️ JSON inválido em signals:raw: {exc}")
                self._stats["errors"] += 1
            except Exception as exc:
                logger.warning(f"⚠️ Erro ao processar sinal: {exc}")
                self._stats["errors"] += 1

    # ── Main loop ────────────────────────────────────────────────────────

    async def start(self):
        """
        Inicia o worker: subscribe em signals:raw e processa sinais.
        Bloqueia até stop() ou interrupção.
        """
        if not REDIS_AVAILABLE:
            logger.error("❌ Redis indisponível — AnalysisWorker não pode iniciar")
            return

        r = await self._get_redis()
        if r is None:
            logger.error("❌ Não foi possível conectar ao Redis")
            return

        self._running = True
        self._semaphore = asyncio.Semaphore(self._concurrency)
        self._stats["started_at"] = time.time()

        engines_str = ", ".join(
            f"{e.name}(p={e.priority})" for e in self._engines if e.enabled
        )
        logger.info(
            f"🚀 AnalysisWorker iniciado | "
            f"canal={RAW_CHANNEL} | concurrency={self._concurrency} | "
            f"engines=[{engines_str}]"
        )

        pubsub = r.pubsub()  # type: ignore
        await pubsub.subscribe(RAW_CHANNEL)

        try:
            async for message in pubsub.listen():
                if not self._running:
                    break
                if message["type"] == "message":
                    # Processa em background (limitado pelo semáforo)
                    asyncio.create_task(self._process_signal(message["data"]))
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error(f"❌ Worker loop error: {exc}")
        finally:
            await pubsub.unsubscribe(RAW_CHANNEL)
            self._running = False
            logger.info("🛑 AnalysisWorker parado")

    async def stop(self):
        """Para o worker."""
        self._running = False

    @property
    def stats(self) -> dict:
        """Retorna estatísticas do worker."""
        uptime = time.time() - self._stats["started_at"] if self._stats["started_at"] else 0
        return {
            **self._stats,
            "uptime_seconds": round(uptime, 1),
            "running": self._running,
            "engines": len(self._engines),
            "engines_enabled": sum(1 for e in self._engines if e.enabled),
        }

    # ── Health check ─────────────────────────────────────────────────────

    async def health_check(self) -> dict:
        """Retorna status de saúde do worker."""
        r = await self._get_redis()
        return {
            "status": "running" if self._running else "stopped",
            "redis": r is not None,
            "pipeline": self.pipeline_info,
            "stats": self.stats,
        }


# ── Enriched buffer replay (para streaming.py) ──────────────────────────────

async def get_enriched_buffer(plan: str = "free", count: int = 20) -> List[dict]:
    """
    Lê os últimos N sinais enriquecidos do buffer do plano.
    Usado pelo WebSocket para replay de enrichments na reconexão.
    """
    if not REDIS_AVAILABLE:
        return []

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = await aioredis.from_url(redis_url, decode_responses=True)
        buffer_key = ENRICHED_BUFFERS.get(plan, ENRICHED_BUFFERS["free"])
        max_allowed = ENRICHED_BUFFER_MAX.get(plan, 50)
        count = min(count, max_allowed)
        items = await r.lrange(buffer_key, 0, count - 1)  # type: ignore
        await r.aclose()  # type: ignore
        return [json.loads(item) for item in items]
    except Exception as exc:
        logger.warning(f"⚠️ Erro ao ler enriched buffer: {exc}")
        return []


# ── Factory: criar worker com engines padrão ─────────────────────────────────

def create_default_worker(
    redis_url: Optional[str] = None,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> AnalysisWorker:
    """
    Cria worker com engines padrão do Culture Pulse.
    Cada engine é carregada sob demanda (lazy) para não puxar dependências pesadas.
    """
    worker = AnalysisWorker(redis_url=redis_url, concurrency=concurrency)

    # ── Engine: Circles classifier ───────────────────────────────────────
    def circles_enricher(signal: dict) -> dict:
        """
        Classifica sinal em um dos 16 círculos culturais.
        S4.3: usa classify_signal_circle() que retorna 'emergente_desconhecido'
        quando nenhum círculo atinge o threshold (em vez de cair em "geral").
        """
        try:
            from core.intelligence.circles_processor import create_circles_processor
            processor = create_circles_processor()
            termo = signal.get("termo", "")
            if not termo:
                return signal

            texto = signal.get("texto", signal.get("descricao", termo))
            plataforma = signal.get("plataforma", "reddit").lower()

            # S4.3: classify_signal_circle retorna circulo + is_unknown + top_scores
            result = processor.classify_signal_circle(
                text=texto,
                plataforma=plataforma,
            )

            signal["circulo"] = result.get("circulo", "geral")
            signal["circle_score"] = result.get("circle_score", 0)
            signal["circles_detail"] = result.get("circles_detail", {})
            signal["is_unknown_circle"] = result.get("is_unknown", False)
            signal["top_circle_scores"] = result.get("top_scores", [])
            if result.get("rejection_reason"):
                signal["circle_rejection_reason"] = result["rejection_reason"]

        except Exception as exc:
            logger.warning(f"⚠️ circles_enricher: {exc}")
        return signal

    # ── Engine: Unknown circle detector (S4.3) ───────────────────────────
    def unknown_detector_enricher(signal: dict) -> dict:
        """
        S4.3: Se sinal foi classificado como emergente_desconhecido,
        enfileira na fila de sinais desconhecidos para clustering periódico.
        Opera de forma síncrona com asyncio.run() pois o Worker chama
        engines sync, e a fila push é async.
        """
        try:
            if not signal.get("is_unknown_circle", False):
                return signal

            import asyncio
            from core.classifiers.unknown_circle_detector import get_unknown_circle_detector
            detector = get_unknown_circle_detector()

            # Push assíncrono — criar novo event loop se necessário
            try:
                loop = asyncio.get_running_loop()
                # Já dentro de um loop (Worker async) — agendar como task
                asyncio.ensure_future(detector.push_unknown_signal(signal))
            except RuntimeError:
                # Sem loop ativo (sync context) — criar um
                asyncio.run(detector.push_unknown_signal(signal))

            signal["_unknown_queued"] = True
            logger.info(
                f"🆕 Sinal desconhecido enfileirado: '{signal.get('termo', '?')}' "
                f"(score={signal.get('circle_score', 0):.3f})"
            )

        except Exception as exc:
            logger.warning(f"⚠️ unknown_detector_enricher: {exc}")
        return signal

    # ── Engine: Sentiment analysis ───────────────────────────────────────
    def sentiment_enricher(signal: dict) -> dict:
        """Enriquece com análise de sentimento via Alma Brasileira."""
        try:
            from core.intelligence.alma_brasileira import create_alma_analyzer
            analyzer = create_alma_analyzer()
            termo = signal.get("termo", "")
            if not termo:
                return signal
            # analyze_alma_brasileira espera raw_data (formato plataforma)
            # + circles_analysis. Montamos raw_data igual ao circles_enricher.
            texto = signal.get("texto", signal.get("descricao", termo))
            plataforma = signal.get("plataforma", "reddit").lower()
            if plataforma == "youtube":
                raw_data = {"youtube": {"comments": [{"text": texto}]}}
            elif plataforma in ("instagram",):
                raw_data = {"instagram": {"posts": [{"caption": texto}]}}
            elif plataforma in ("news", "newsapi"):
                raw_data = {"news": {"articles": [{"title": termo, "content": texto}]}}
            else:
                raw_data = {"reddit": {"posts": [{"title": termo, "content": texto}]}}
            circles_analysis = {
                "circles_scores": signal.get("circles_detail", {}),
                "dominant_circles": [signal.get("circulo", "geral")],
                "overall_score": signal.get("circle_score", 0),
            }
            result = analyzer.analyze_alma_brasileira(raw_data, circles_analysis)
            if result:
                summary = result.get("summary", {})
                signal["sentiment_detail"] = {
                    "alma_score": result.get("alma_score", 0),
                    "alma_intensity": summary.get("alma_intensity", ""),
                    "authenticity_level": summary.get("cultural_authenticity", ""),
                    "dominant_values": summary.get("dominant_values", []),
                    "regional_connection": summary.get("regional_connection", ""),
                }
        except Exception as exc:
            logger.warning(f"⚠️ sentiment_enricher: {exc}")
        return signal

    # ── Engine: Authenticity scoring ─────────────────────────────────────
    def authenticity_enricher(signal: dict) -> dict:
        """
        Calcula score de autenticidade do sinal.

        INT-A: Após calcular authenticity, calibra signal_nature se já existir.
        Se appropriation_risk alto e nature diz ORGÂNICO, reclassifica ou
        ajusta confiança. Evita falsos positivos de "orgânico" em sinais
        com alto risco de apropriação.
        """
        try:
            from core.classifiers.authenticity_analyzer import AuthenticityAnalyzer
            analyzer = AuthenticityAnalyzer()
            # analyze_authenticity espera content: str
            content = signal.get("texto", signal.get("descricao", signal.get("termo", "")))
            if not content:
                return signal
            result = analyzer.analyze_authenticity(content)
            if result:
                signal["authenticity_score"] = result.authenticity_score
                signal["authenticity_label"] = (
                    "alta" if result.authenticity_score > 0.6
                    else "media" if result.authenticity_score > 0.3
                    else "baixa"
                )
                signal["appropriation_risk"] = result.appropriation_risk
                signal["authenticity_indicators"] = result.key_indicators

                # ── INT-A: Cross-calibrate signal_nature ─────────────────
                nature = signal.get("signal_nature")
                if nature and isinstance(nature, dict):
                    cat = nature.get("categoria", "")
                    # Se appropriation_risk alto mas nature diz ORGÂNICO → baixar confiança
                    if result.appropriation_risk > 0.6 and cat == "ORGÂNICO":
                        nature["confianca"] = round(
                            nature.get("confianca", 0.5) * 0.6, 3
                        )
                        nature["flags"] = nature.get("flags", []) + [
                            "INT-A: confiança reduzida por appropriation_risk alto"
                        ]
                    # Se authenticity_score muito alto → reforçar orgânico
                    elif result.authenticity_score > 0.8 and cat == "ORGÂNICO":
                        nature["confianca"] = round(
                            min(1.0, nature.get("confianca", 0.5) * 1.15), 3
                        )
                    # Se appropriation_risk alto e nature é COMERCIAL → flag de apropriação
                    if result.appropriation_risk > 0.7 and cat == "COMERCIAL":
                        nature["score_apropriacao"] = max(
                            nature.get("score_apropriacao", 0),
                            int(result.appropriation_risk * 100),
                        )
                        nature["flags"] = nature.get("flags", []) + [
                            "INT-A: score_apropriacao elevado via authenticity"
                        ]
                    signal["signal_nature"] = nature

        except Exception as exc:
            logger.warning(f"⚠️ authenticity_enricher: {exc}")
        return signal

    # ── Engine: Graph propagation (GNN) — INT-4C refactored ────────────
    def graph_enricher(signal: dict) -> dict:
        """
        Enriquece sinal com análise de propagação cultural via GNN.

        INT-4C: Uses real co-occurrence graph from CulturalGraphBuilder
        when sufficient data is available. Falls back to static affinity
        if fewer than MIN_REAL_EDGES co-occurrences exist.

        The builder accumulates signals across calls (singleton), so the
        graph improves over time as more signals are processed.
        """
        try:
            from core.engines.graph_builder import get_graph_builder

            termo = signal.get("termo", "")
            circulo = signal.get("circulo", "geral")
            if not termo or circulo == "geral":
                return signal

            builder = get_graph_builder()

            # Feed current signal into the builder (accumulates over time)
            builder.add_signal(signal)

            # Run analysis using the real (or fallback) graph
            result = builder.analyze(signal)

            graph_data = builder.build()

            graph_result = {
                "graph_nodes": graph_data.node_count,
                "graph_edges": graph_data.edge_count,
                "graph_is_real": graph_data.is_real,
                "graph_stats": graph_data.stats,
                "graph_neighbors": [
                    e.target for e in graph_data.edges
                    if e.source == circulo and e.edge_type in ("co-occurrence", "affinity")
                ][:5],
            }

            if result.influence_scores:
                graph_result["influence_scores"] = result.influence_scores
                graph_result["community_count"] = len(result.communities)
                graph_result["central_nodes"] = result.central_nodes
                graph_result["propagation_paths_count"] = len(result.propagation_paths)

            signal["graph_analysis"] = graph_result

        except Exception as exc:
            logger.warning(f"⚠️ graph_enricher: {exc}")
        return signal

    # ── Engine: Signal nature classification ────────────────────────────
    def nature_enricher(signal: dict) -> dict:
        """
        Classifica a NATUREZA CULTURAL do sinal:
        ORGÂNICO / RESONÂNCIA / COMERCIAL / SIMULAÇÃO / APROPRIAÇÃO.
        Usa dicionários de marcadores linguísticos brasileiros para detectar
        autenticidade, astroturfing, e apropriação cultural.
        Integrado: S4.3+ (23/Fev/2026)
        """
        try:
            try:
                from core.classifiers.signal_nature_classifier import SignalNatureClassifier
            except ImportError:
                from src_v8.core.classifiers.signal_nature_classifier import SignalNatureClassifier

            termo = signal.get("termo", "")
            if not termo:
                return signal

            classifier = SignalNatureClassifier()

            # Montar inputs a partir dos dados já enriquecidos pelo pipeline
            texto = signal.get("texto", signal.get("descricao", termo))
            plataforma = signal.get("plataforma", "unknown")
            volume = 0
            raw = signal.get("raw_data", {})
            if isinstance(raw, dict):
                volume = int(raw.get("volume", 0) or 0)

            # Extrair dados de enrichers anteriores
            velocity = 0.0
            velocity_data = signal.get("velocity_features", {})
            if velocity_data:
                velocity = velocity_data.get("velocity", 0.0)

            sentiment = 0.5
            sent_detail = signal.get("sentiment_detail", {})
            if sent_detail:
                alma = sent_detail.get("alma_score", 50)
                sentiment = alma / 100.0 if alma > 1 else alma

            result = classifier.classify(
                termo=termo,
                mencoes=[texto],
                contextos=[signal.get("circulo", "geral")],
                plataformas=[plataforma],
                tensoes=[],
                demografico={},
                velocity=velocity,
                volume=volume,
                sentiment=sentiment,
            )

            signal["signal_nature"] = {
                "categoria": result.categoria,
                "confianca": round(result.confianca, 3),
                "score_organico": result.score_organico,
                "score_comercial": result.score_comercial,
                "score_apropriacao": result.score_apropriacao,
                "evidencias": result.evidencias[:5],
                "flags": result.flags[:5],
            }

        except Exception as exc:
            logger.warning(f"⚠️ nature_enricher: {exc}")
        return signal

    # ── Engine: Velocity & positional features ───────────────────────────
    def velocity_enricher(signal: dict) -> dict:
        """
        Computa velocity, acceleration, interaction_type, temporal_delta
        para o sinal. Usa VelocityComputer (S3.5 P8+P15).
        Integrado: S4.3+ (23/Fev/2026)

        INT-B: Usa circulo para aplicar multiplicador contextual de velocidade.
        "Viral" em Humor & Memes é comum; "viral" em Religiosidade é raro.
        Multiplicadores normalizam a velocidade pelo baseline do círculo.
        """
        try:
            from core.engines.velocity_computer import VelocityComputer, infer_interaction_type

            termo = signal.get("termo", "")
            if not termo:
                return signal

            raw = signal.get("raw_data", {})
            if isinstance(raw, str):
                import json as _json
                try:
                    raw = _json.loads(raw)
                except (ValueError, TypeError):
                    raw = {}

            plataforma = signal.get("plataforma", "unknown")
            momentum = float(raw.get("momentum", 0) or 0)
            volume = int(raw.get("volume", 0) or 0)

            # Interaction type (always computable per signal)
            int_type = infer_interaction_type(plataforma, volume, momentum)

            # For single-signal enrichment, velocity/acceleration require
            # previous signal data. We store what we can and mark for
            # batch backfill later.
            velocity_data = {
                "velocity": float(raw.get("velocity", 0.0) or 0.0),
                "interaction_type": int_type,
                "momentum_velocity": float(raw.get("momentum_velocity", 0.0) or 0.0),
                "temporal_delta_hours": float(raw.get("temporal_delta_hours", 0.0) or 0.0),
                "momentum_snapshot": momentum,
                "volume_snapshot": volume,
                "s35_enricher": True,
            }

            # ── INT-B: Contextualizar velocidade por círculo ─────────────
            circulo = signal.get("circulo", "geral")
            baseline = CIRCLE_VELOCITY_BASELINE.get(circulo, 1.0)
            raw_vel = velocity_data["velocity"]
            if baseline != 1.0 and raw_vel > 0:
                velocity_data["velocity_raw"] = raw_vel
                velocity_data["velocity"] = round(raw_vel / baseline, 4)
                velocity_data["circle_baseline"] = baseline
                velocity_data["circle_context"] = circulo

            signal["velocity_features"] = velocity_data

        except Exception as exc:
            logger.warning(f"⚠️ velocity_enricher: {exc}")
        return signal

    # ── Engine: Tension detection (H-1) ──────────────────────────────────
    def tension_enricher(signal: dict) -> dict:
        """
        Detecta tensões culturais no sinal: conflitos geracionais, regionais,
        ideológicos, socioeconômicos, tradição vs modernidade.
        Usa keyword matching + sentiment polarization para score 0–1.

        Integrado: H-1 FASE 2 (23/Fev/2026)
        Source: core/tension_engine.py (slim adapter de dormant/tension_detection_engine)
        """
        try:
            from core.engines.tension_engine import get_tension_engine

            termo = signal.get("termo", "")
            if not termo:
                return signal

            engine = get_tension_engine()
            texto = signal.get("texto", signal.get("descricao", termo))
            full_text = f"{termo} {texto}"

            # Extract sentiment from previous enricher if available
            sentiment = 0.5
            sent_detail = signal.get("sentiment_detail", {})
            if sent_detail:
                alma = sent_detail.get("alma_score", 50)
                sentiment = alma / 100.0 if alma > 1 else alma

            circle = signal.get("circulo", "")
            plataforma = signal.get("plataforma", "")

            result = engine.analyze(
                full_text,
                sentiment=sentiment,
                circle=circle,
                plataforma=plataforma,
            )
            signal["tension_analysis"] = result.to_dict()

        except Exception as exc:
            logger.warning(f"⚠️ tension_enricher: {exc}")
        return signal

    # ── Engine: Feedback quality prediction (INT-1) ──────────────────────
    def feedback_enricher(signal: dict) -> dict:
        """
        Predict quality score for the signal based on accumulated user feedback.
        Also adds the signal text to the feedback engine's feature context.

        Integrado: INT-1 FASE 2 (23/Fev/2026)
        Source: core/feedback_engine.py (slim adapter de feedback_learning.py)
        """
        try:
            from core.intelligence.learning.InsightLearner import get_feedback_engine

            engine = get_feedback_engine()
            prediction = engine.predict(signal)
            signal["feedback_prediction"] = prediction

        except Exception as exc:
            logger.warning(f"⚠️ feedback_enricher: {exc}")
        return signal

    # ── Engine: Topic assignment (INT-2) ─────────────────────────────────
    def topic_enricher(signal: dict) -> dict:
        """
        Assign signal to a macro-topic using incremental LDA.
        Adds signal text to topic buffer for future refitting.

        Integrado: INT-2 FASE 2 (23/Fev/2026)
        Source: core/topic_engine.py (slim adapter de hierarchical_topic_modeler.py)
        """
        try:
            from core.intelligence.topic_engine import get_topic_engine

            engine = get_topic_engine()

            termo = signal.get("termo", "")
            texto = signal.get("texto", signal.get("descricao", ""))
            full_text = f"{termo} {texto}".strip()

            if full_text:
                # Add to buffer (may trigger auto-refit)
                engine.add_document(full_text)

                # Predict topic assignment
                assignment = engine.predict(full_text)
                signal["topic_assignment"] = assignment.to_dict()

        except Exception as exc:
            logger.warning(f"⚠️ topic_enricher: {exc}")
        return signal

    # ── Engine: PEST classification (F-5) ────────────────────────────────
    def pest_enricher(signal: dict) -> dict:
        """
        Classifica o sinal em dimensão PEST: Political / Economic / Social /
        Technological usando keyword matching PT-BR.

        INT-D: Agora usa classify_signal() que também lê tension_analysis
        e signal_nature do pipeline para boost/confirmar scores PEST.

        Integrado: F-5 FASE 2 + INT-D (24/Fev/2026)
        Source: core/pest_engine.py
        """
        try:
            from core.engines.pest_engine import get_pest_engine

            termo = signal.get("termo", "")
            if not termo:
                return signal

            engine = get_pest_engine()
            result = engine.classify_signal(signal)
            signal["pest_classification"] = result.to_dict()

        except Exception as exc:
            logger.warning(f"⚠️ pest_enricher: {exc}")
        return signal

    # ── Registrar engines com prioridades ────────────────────────────────
    worker.register("circles", circles_enricher, priority=10, timeout=5)
    worker.register("unknown_detector", unknown_detector_enricher, priority=15, timeout=3)
    worker.register("sentiment", sentiment_enricher, priority=20, timeout=5)
    worker.register("tension", tension_enricher, priority=22, timeout=5)
    worker.register("nature", nature_enricher, priority=25, timeout=5)
    worker.register("authenticity", authenticity_enricher, priority=30, timeout=5)
    worker.register("velocity", velocity_enricher, priority=35, timeout=5)
    worker.register("graph", graph_enricher, priority=40, timeout=15, required=False)
    worker.register("feedback", feedback_enricher, priority=45, timeout=5)
    worker.register("topics", topic_enricher, priority=48, timeout=5)
    worker.register("pest", pest_enricher, priority=50, timeout=5)

    # ── FASE 3 engines (H-9): vulnerability, alerts, actions, scenarios, opportunities

    def vulnerability_enricher(signal: dict) -> dict:
        """Avalia vulnerabilidade cultural do sinal. Source: core/vulnerability_engine.py"""
        try:
            from core.engines.vulnerability_engine import get_vulnerability_engine
            engine = get_vulnerability_engine()
            signal["vulnerability"] = engine.assess_signal(signal)
        except Exception as exc:
            logger.warning(f"⚠️ vulnerability_enricher: {exc}")
        return signal

    def alerts_enricher(signal: dict) -> dict:
        """Gera alertas culturais para o sinal. Source: alerts/cultural_alerts_engine.py"""
        try:
            from alerts.cultural_alerts_engine import get_alerts_engine
            engine = get_alerts_engine()
            signal["cultural_alerts"] = engine.evaluate_dict(signal)
        except Exception as exc:
            logger.warning(f"⚠️ alerts_enricher: {exc}")
        return signal

    def actions_enricher(signal: dict) -> dict:
        """Gera ação estratégica recomendada. Source: core/strategic_actions_engine.py"""
        try:
            from core.intelligence.strategic_actions_engine import get_strategic_engine
            engine = get_strategic_engine()
            signal["strategic_action"] = engine.recommend_dict(signal)
        except Exception as exc:
            logger.warning(f"⚠️ actions_enricher: {exc}")
        return signal

    def scenarios_enricher(signal: dict) -> dict:
        """Gera cenários futuros (otimista/base/pessimista). Source: core/scenario_engine.py"""
        try:
            from core.engines.scenario_engine import get_scenario_engine
            engine = get_scenario_engine()
            signal["scenarios"] = engine.generate_dict(signal)
        except Exception as exc:
            logger.warning(f"⚠️ scenarios_enricher: {exc}")
        return signal

    def opportunities_enricher(signal: dict) -> dict:
        """Detecta oportunidades culturais. Source: core/opportunity_engine.py"""
        try:
            from core.intelligence.opportunity_engine import get_opportunity_engine
            engine = get_opportunity_engine()
            signal["opportunities"] = engine.detect_dict(signal)
        except Exception as exc:
            logger.warning(f"⚠️ opportunities_enricher: {exc}")
        return signal

    worker.register("vulnerability", vulnerability_enricher, priority=52, timeout=5)
    worker.register("alerts", alerts_enricher, priority=54, timeout=5)
    worker.register("actions", actions_enricher, priority=56, timeout=5)
    worker.register("scenarios", scenarios_enricher, priority=58, timeout=5)
    worker.register("opportunities", opportunities_enricher, priority=60, timeout=5)

    # ── FASE 4 engine (V9.9): Narrativa e Estratégia via SLM Local (Ollama) ────

    def slm_narrative_enricher(signal: dict) -> dict:
        """
        Enriquece sinal com Narrativa Cultural e Estratégia de Negócio real
        usando o Llama-3-8B local.
        """
        try:
            from core.intelligence.context_enricher_v2 import get_dashboard_context_enricher
            enricher = get_dashboard_context_enricher(use_llm=True)

            onboarding_context = signal.get('onboarding_context') or signal.get('contexto_onboarding')
            if onboarding_context:
                signal['onboarding_context'] = onboarding_context

            # Executar enriquecimento completo (que agora usa SLM bridge)
            # Nota: O contexto de onboarding default é usado se não houver um específico por sinal
            return enricher.enrich_weak_signal(signal, contexto_onboarding=onboarding_context)
            
        except Exception as exc:
            logger.warning(f"⚠️ slm_narrative_enricher: {exc}")
        return signal

    worker.register("slm_narrative", slm_narrative_enricher, priority=70, timeout=120)

    # ── INTEGRATION: Stability × Nature × Risk (Caminhos 1+2+3) ─────────

    def stability_enricher(signal: dict) -> dict:
        """
        Cruza Cluster Stability (F-2) × Signal Nature × Risk (F-6) para
        produzir um contexto integrado de estabilidade-risco.

        Requer enrichers anteriores: nature(25), vulnerability(52), alerts(54).
        Lê signal['signal_nature'] e consulta o ClusterStabilityAnalyzer singleton
        para obter o status atual de estabilidade dos clusters.

        Injeta signal['stability_context'] com:
          - status: StabilityStatus value
          - ari_score / nmi_score
          - recommendation: resultado da matriz Nature×Stability (Caminho 2)
          - risk_assessment: RiskEngine com 5 fatores incluindo stability (Caminho 1)

        Integrado: Caminhos 1+2+3 (24/Fev/2026)
        """
        try:
            from core.clustering import get_stability_analyzer, StabilityStatus
            from core.classifiers.signal_nature_classifier import SignalNatureClassifier, SignalNatureResult
            from core.engines.risk_engine import get_risk_engine

            analyzer = get_stability_analyzer()
            latest = analyzer.latest_comparison()

            stability_status = latest.status.value  # e.g. "estável"

            # Inject stability status so RiskEngine can pick it up
            signal["stability_context"] = {
                "status": stability_status,
                "badge": latest.badge_emoji,
                "description": latest.badge_description,
                "ari_score": latest.ari_score,
                "nmi_score": latest.nmi_score,
                "n_clusters_prev": latest.n_clusters_prev,
                "n_clusters_curr": latest.n_clusters_curr,
                "new_clusters": latest.new_clusters,
                "lost_clusters": latest.lost_clusters,
                "sample_size": latest.sample_size,
            }

            # Caminho 2: Nature × Stability matrix recommendation
            nature_data = signal.get("signal_nature", {})
            if nature_data:
                classifier = SignalNatureClassifier()
                nature_result = SignalNatureResult(
                    categoria=nature_data.get("categoria", "ORGÂNICO"),
                    confianca=nature_data.get("confianca", 0.5),
                    score_organico=nature_data.get("score_organico", 0),
                    score_comercial=nature_data.get("score_comercial", 0),
                    score_apropriacao=nature_data.get("score_apropriacao", 0),
                    evidencias=nature_data.get("evidencias", []),
                    flags=nature_data.get("flags", []),
                    nuances_detectadas={},
                )
                rec = classifier.get_stability_recommendation(
                    nature_result, stability_status, bot_risk_level="LOW"
                )
                signal["stability_context"]["recommendation"] = rec

            # Caminho 1: Risk assessment with 5 factors (including stability)
            risk_engine = get_risk_engine()
            risk_result = risk_engine.assess_dict(signal)
            signal["stability_context"]["risk_assessment"] = risk_result

        except Exception as exc:
            logger.warning(f"⚠️ stability_enricher: {exc}")
        return signal

    worker.register("stability_risk", stability_enricher, priority=62, timeout=8)

    return worker


# ── CLI standalone: executar worker diretamente ──────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

    print("🚀 Culture Pulse — Analysis Worker V9.1")
    print("=" * 50)

    worker = create_default_worker()
    print(f"📋 Pipeline: {[e['name'] for e in worker.pipeline_info]}")
    print(f"🔌 Redis: {worker._redis_url}")
    print(f"⚡ Concurrency: {worker._concurrency}")
    print(f"📡 Canal: {RAW_CHANNEL}")
    print(f"📤 Enriched: {list(ENRICHED_CHANNELS.values())}")
    print("\nCtrl+C para parar\n")

    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        print("\n🛑 Worker encerrado")
        sys.exit(0)
