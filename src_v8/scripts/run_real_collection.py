#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 COLETA REAL — Culture Pulse V9
Executa coleta via APIs reais, detecta sinais fracos e persiste no Supabase.

Uso:
    python3 scripts/run_real_collection.py
    python3 scripts/run_real_collection.py --terms "funk,pagode,trap brasileiro"
    python3 scripts/run_real_collection.py --dry-run   # Mostra sinais sem salvar

Saída:
    - Exibe sinais fracos detectados no terminal
    - Persiste cultural_signals no Supabase (via REST API)
    - Salva relatório JSON em data/real_collection_<timestamp>.json
"""

import sys
import asyncio
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx

# ---------------------------------------------------------------------------
# Bootstrap de paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração Supabase
# ---------------------------------------------------------------------------
SUPABASE_URL = "https://wsizqmnnicpgblopmxyv.supabase.co"
SUPABASE_SERVICE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzaXpxbW5uaWNwZ2Jsb3BteHl2Iiwicm9sZSI6"
    "InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQ0MDExNiwiZXhwIjoyMDg3MDE2MTE2fQ."
    "ca8oGhfR1Ek7t5n9fmCS3O5UaaCBUhqRAIJtavc5QpE"
)
REST_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ---------------------------------------------------------------------------
# Termos padrão de coleta (16 círculos culturais)
# ---------------------------------------------------------------------------
DEFAULT_TERMS = [
    # Música / entretenimento
    "funk carioca", "pagode", "sertanejo universitário", "trap brasileiro",
    "forró", "brega funk", "piseiro",
    # Moda / lifestyle
    "streetwear brasil", "vintage moda", "hypebeast", "slow fashion",
    # Tecnologia / cultura digital
    "ia generativa", "chatgpt brasil", "deepfake", "crypto meme",
    # Gastronomia
    "smash burger", "comida de rua", "veganismo", "churrasco gourmet",
    # Comportamento / social
    "saúde mental jovens", "burnout", "quiet quitting", "gen z trabalho",
    # Política / sociedade
    "polarização brasil", "fake news", "ativismo climático",
]

# ---------------------------------------------------------------------------
# Helpers Supabase
# ---------------------------------------------------------------------------

async def upsert_signal(client: httpx.AsyncClient, signal_data: Dict[str, Any]) -> bool:
    """Persistir um sinal no Supabase via REST API."""
    try:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/cultural_signals",
            headers={**REST_HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"},
            json=signal_data,
        )
        if resp.status_code in (200, 201):
            return True
        else:
            logger.warning(f"  ⚠️  Supabase upsert {resp.status_code}: {resp.text[:120]}")
            return False
    except Exception as e:
        logger.warning(f"  ⚠️  Supabase upsert error: {e}")
        return False


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Converter para float com fallback seguro."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _inferir_circulo(termo: str) -> str:
    """
    Mapeia um termo cultural para o círculo correto.

    Estratégia em 2 camadas:
      1. Lookup exato pelo termo normalizado (minúsculas, sem acentos opcionais).
      2. Varredura por palavras-chave caso o termo não conste no mapa exato.
      3. Fallback: "cultura_geral".

    O mapeamento cobre os 26 DEFAULT_TERMS + termos futuros comuns.
    Sempre que novos termos forem adicionados a DEFAULT_TERMS, adicione-os aqui.
    """
    t = termo.lower().strip()

    # --- Mapa exato (termo completo → círculo) ---
    MAPA_EXATO: Dict[str, str] = {
        # Música / entretenimento
        "funk carioca":            "música",
        "pagode":                  "música",
        "sertanejo universitário": "música",
        "trap brasileiro":         "música",
        "forró":                   "música",
        "brega funk":              "música",
        "piseiro":                 "música",
        # Moda / lifestyle
        "streetwear brasil":       "moda",
        "vintage moda":            "moda",
        "hypebeast":               "moda",
        "slow fashion":            "moda",
        # Tecnologia / cultura digital
        "ia generativa":           "tecnologia",
        "chatgpt brasil":          "tecnologia",
        "deepfake":                "tecnologia",
        "crypto meme":             "tecnologia",
        # Gastronomia
        "smash burger":            "gastronomia",
        "comida de rua":           "gastronomia",
        "veganismo":               "gastronomia",
        "churrasco gourmet":       "gastronomia",
        # Comportamento / social
        "saúde mental jovens":     "saúde",
        "burnout":                 "saúde",
        "quiet quitting":          "comportamento",
        "gen z trabalho":          "comportamento",
        # Política / sociedade
        "polarização brasil":      "política",
        "fake news":               "política",
        "ativismo climático":      "sustentabilidade",
    }

    if t in MAPA_EXATO:
        return MAPA_EXATO[t]

    # --- Varredura por palavras-chave ---
    KEYWORDS: List[tuple] = [
        ("música",          ["funk", "pagode", "sertanejo", "samba", "rap", "trap", "brega", "forró", "piseiro", "baile", "música", "cantor", "banda", "show", "festival"]),
        ("moda",            ["moda", "fashion", "style", "roupa", "streetwear", "vintage", "hypebeast", "sneaker", "look", "outfit"]),
        ("tecnologia",      ["ia", "ai", "tech", "tecnologia", "startup", "crypto", "blockchain", "chatgpt", "deepfake", "app", "digital", "inteligência artificial"]),
        ("gastronomia",     ["burger", "food", "comida", "culinária", "vegan", "churrasco", "gastronomia", "receita", "restaurante"]),
        ("saúde",           ["saúde", "mental", "burnout", "wellness", "fitness", "ansiedade", "terapia", "bem-estar"]),
        ("comportamento",   ["comportamento", "geração", "gen z", "millennial", "trabalho", "quitting", "tendência social"]),
        ("política",        ["política", "governo", "eleição", "polarização", "fake news", "presidente", "congresso"]),
        ("sustentabilidade",["clima", "sustentabilidade", "ambiental", "carbono", "reciclagem", "esg", "verde", "ativismo"]),
        ("esporte",         ["esporte", "futebol", "atleta", "copa", "olimpíada", "basquete", "vôlei", "campeonato"]),
        ("games",           ["game", "gamer", "esport", "streamer", "twitch", "valorant", "free fire"]),
    ]

    for circulo, kws in KEYWORDS:
        if any(kw in t for kw in kws):
            return circulo

    return "cultura_geral"


def signal_to_supabase_row(
    termo: str,
    signal_data: Dict[str, Any],
    weak_signal: Optional[Any],
    business_synth: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Converter dados coletados + WeakSignal + BusinessSynthesizer em linha do Supabase."""
    # Determinar tipo do sinal e círculo cultural
    tipo = "sinal_fraco" if weak_signal else "sinal_cultural"
    ws_score = _safe_float(signal_data.get("weak_signal_score", 0))
    
    circulo = _inferir_circulo(termo)
    regiao = "Brasil"

    # Dados extras para raw_data
    raw: Dict[str, Any] = {
        "momentum": _safe_float(signal_data.get("momentum", 0)),
        "volume": int(signal_data.get("volume", 0) or 0),
        "sentiment": _safe_float(signal_data.get("sentiment", 0)),
        "cultural_relevance": _safe_float(signal_data.get("cultural_relevance", 0)),
        "is_real_data": True,
        "collection_source": "run_real_collection.py (V9.7)",
    }

    if weak_signal:
        # Tentar pegar atributos se for objeto, ou chaves se for dict
        is_obj = hasattr(weak_signal, 'weak_signal_score')
        raw["weak_signal_score"] = getattr(weak_signal, "weak_signal_score", 0) if is_obj else weak_signal.get("weak_signal_score", 0)
        raw["volume_spike"] = getattr(weak_signal, "volume_spike", False) if is_obj else weak_signal.get("volume_spike", False)
        raw["sentiment_shift"] = getattr(weak_signal, "sentiment_shift", False) if is_obj else weak_signal.get("sentiment_shift", False)
        raw["context_anomaly"] = getattr(weak_signal, "context_anomaly", False) if is_obj else weak_signal.get("context_anomaly", False)

    # Injetar dados do BusinessSynthesizer (P9/V9.7)
    if business_synth:
        raw.update({
            "authenticity_score": business_synth.get("authenticity_score"),
            "visual_proof_score": business_synth.get("visual_proof_score"),
            "is_verified_source": business_synth.get("is_verified_source"),
            "momentum_velocity": business_synth.get("momentum_velocity"),
            "context_tags": business_synth.get("context_tags"),
            "tension_score": business_synth.get("tension_score"),
            "campaign_fit": business_synth.get("campaign_fit"),
            "quality_label": business_synth.get("quality_label"),
            "recommendation": business_synth.get("recommendation"),
            "evidence": business_synth.get("evidence", [])
        })
        # Se verificado, marcar como tal na explicação
        v_prefix = "🛡️ [VERIFICADO] " if business_synth.get("is_verified_source") else ""
        raw["explicacao"] = f"{v_prefix}{business_synth.get('recommendation', '')}"

    score_normalizado = round(min(_safe_float(raw.get("momentum", 0)) / 100.0, 9.999), 3)

    return {
        "tipo": tipo,
        "circulo": circulo,
        "termo": termo,
        "score": score_normalizado,
        "regiao": regiao,
        "plataforma": signal_data.get("plataforma", "desconhecido"),
        "raw_data": raw,
    }

    return {
        "tipo": tipo,
        "circulo": circulo,
        "termo": termo,
        "score": score_normalizado,
        "regiao": regiao,
        "plataforma": getattr(signal, "plataforma", "desconhecido"),
        "raw_data": raw,
        # ts é preenchido automaticamente pelo default no Supabase
    }


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

async def run_collection(terms: List[str], dry_run: bool = False) -> Dict[str, Any]:
    """Executar coleta real e detecção de sinais fracos."""

    # --- Importar coletores e detector ---
    from collectors.data_collectors import create_unified_collectors
    try:
        from autonomous_agent.weak_signals_detector import WeakSignalsDetector as WeakSignalDetector
    except ImportError:
        from autonomous_agent.weak_signals_detector import WeakSignalsDetector as WeakSignalDetector
    
    from core.intelligence.business_synthesizer import BusinessSynthesizer as SignalSynthesizer

    collectors = create_unified_collectors()
    # WeakSignalsDetector V9.0 não recebe argumentos no __init__
    detector = WeakSignalDetector()
    
    # Orquestrador necessário para coleta
    from collectors.orchestrator import collect_cultural_data
    # Definimos uma função helper para manter a interface de uso original se possível
    async def get_results(term):
        # A função collect_cultural_data do orchestrator.py retorna uma lista de dicionários/objetos
        # Na V8 agora ele chama orchestrator.collect_comprehensive_data internamente
        # que retorna o dicionário bruto plataforma -> CulturalSignal
        from collectors.orchestrator import cultural_orchestrator
        raw_signals = await cultural_orchestrator.collect_comprehensive_data(term)
        # Retornamos o dicionário de sinais brutos (objetos CulturalSignal)
        return raw_signals

    logger.info(f"🚀  Coletores ativos: {list(collectors.keys())}")
    # logger.info(f"🔍  Thresholds: {detector.THRESHOLDS}")
    logger.info(f"📋  Termos: {len(terms)}")
    logger.info("=" * 70)

    # --- Coletar sinais para todos os termos ---
    all_signals = []
    for term in terms:
        logger.info(f"  ▶  Coletando: {term}")
        results = await get_results(term)
        
        # O CulturalDataOrchestrator V8 retorna um DICT de plataforma -> CulturalSignal
        # ou uma lista se vier de outro lugar.
        raw_signals_list = []
        if isinstance(results, dict):
            # Se for um dicionário de sinais (platform -> signal)
            raw_signals_list = list(results.values())
            # Se results for o output de analyze_collected_signals, ele tem status, metrix, etc.
            # No V8 orchestrator.py: a função analyze_collected_signals retorna um dict com metadados.
            # Mas nós precisamos dos objetos CulturalSignal originais.
            if 'status' in results and 'metadados' in results:
                 # Aqui pode ser que o orchestrator não esteja retornando os sinais crus no dict final
                 # Vamos tentar re-coletar ou extrair se existir uma chave escondida
                 pass
        elif isinstance(results, list):
            raw_signals_list = results
        
        # Converter objetos CulturalSignal para dicionários antes do detector
        processed_results = []
        for s in raw_signals_list:
            if hasattr(s, 'to_dict'):
                processed_results.append(s.to_dict())
            elif isinstance(s, dict):
                # Validar se parece um sinal ou apenas metadados
                if 'plataforma' in s or 'momentum' in s:
                    processed_results.append(s)
            else:
                # Fallback manual se não tiver to_dict
                processed_results.append({
                    "termo": getattr(s, "termo", term),
                    "sentiment": getattr(s, "sentiment", 0),
                    "momentum": getattr(s, "momentum", 0),
                    "volume": getattr(s, "volume", 0),
                    "plataforma": getattr(s, "plataforma", "desconhecido"),
                    "timestamp": getattr(s, "ts", datetime.now().isoformat()),
                })
        
        if not processed_results:
            logger.warning(f"    ⚠️  Aviso: Nenhum sinal bruto processável encontrado para '{term}'.")
            # Injetar sinal sintético se for necessário para o pipeline não morrer? 
            # Não, melhor investigar o retorno real.
        
        all_signals.extend(processed_results)
        logger.info(f"    → {len(processed_results)} sinais brutos prontos para análise profunda")

    logger.info(f"\n📊  Total de sinais consolidados: {len(all_signals)}")
    logger.info("=" * 70)

    # --- Detectar sinais fracos ---
    logger.info("🔬  Rodando WeakSignalDetector nos sinais coletados...")
    if not all_signals:
        logger.warning("⚠️  Nenhum sinal coletado para processar.")
        weak_signals = []
    else:
        weak_signals = detector.detect_weak_signals(all_signals)

    # Mapear termo → WeakSignal
    ws_map: Dict[str, Any] = {}
    for ws in weak_signals:
        if hasattr(ws, 'termo'):
            ws_map[ws.termo] = ws
        elif isinstance(ws, dict) and 'termo' in ws:
            ws_map[ws['termo']] = ws
        elif isinstance(ws, str):
            # Se o detector retornar apenas strings
            ws_map[ws] = ws

    logger.info(f"⚡  Sinais fracos detectados: {len(weak_signals)}")
    logger.info("=" * 70)

    # Exibir sinais fracos
    if weak_signals:
        # Sanitizar para casos onde o detector retorna listas mistas ou strings
        safe_ws = []
        for ws in weak_signals:
            if hasattr(ws, 'weak_signal_score'):
                safe_ws.append(ws)
            elif isinstance(ws, dict) and 'weak_signal_score' in ws:
                # Criar objeto mock se necessário para compatibilidade com o loop abaixo
                class MockWS:
                    def __init__(self, d):
                        self.__dict__.update(d)
                safe_ws.append(MockWS(ws))
        
        if safe_ws:
            for ws in sorted(safe_ws, key=lambda x: getattr(x, 'weak_signal_score', 0), reverse=True):
                badge = getattr(ws, "badge", "OBSERVAR")
                logger.info(
                    f"  [{badge:>10}]  {getattr(ws, 'termo', 'N/A'):<30}  score={getattr(ws, 'weak_signal_score', 0):.1f}"
                    f"  vol={getattr(ws, 'volume_atual', 0)}  mom={getattr(ws, 'current_momentum', 0):.1f}"
                )
        else:
            logger.info(f"  ({len(weak_signals)} sinais detectados, mas sem métricas de score detalhadas)")
    else:
        logger.info("  (nenhum sinal fraco detectado com os thresholds atuais)")

    logger.info("=" * 70)

    # --- Sintetizar sinais (P9: keyword → fenômeno cultural) ---
    logger.info("🧠  Sintetizando insights de negócio (V9.7 Context)...")
    
    # Adaptar para o BusinessSynthesizer V9.7
    from core.intelligence.business_synthesizer import BusinessSynthesizer, BusinessContext
    biz_synthesizer = BusinessSynthesizer()
    
    # Criar um contexto padrão para garantir que temos sinais mesmo em dry-run
    context = BusinessContext(
        scenario_type="Pesquisa de Mercado",
        target_audience="Diversos (Geográfico: SP/RJ)",
        business_objective="Mapear tendências culturais emergentes",
        opportunities_sought=["Inovação", "Diferenciação", "Conexão"],
        constraints=["Ética de dados", "Privacidade"],
        success_metrics=["Precisão", "Alcance", "Engajamento"]
    )
    
    # Se all_signals estiver vazio, vamos injetar os termos brutos como sinais base para teste 
    # apenas se estivermos em DRY-RUN e o orquestrador não trouxe nada filtrado
    if not all_signals and dry_run:
        logger.info("🧪  Modo Teste: Injetando termos de busca como sinais base para síntese...")
        for term in terms:
            all_signals.append({
                "termo": term,
                "plataforma": "cross-platform",
                "momentum": 50.0,
                "volume": 100,
                "sentiment": 0.1,
                "relevancia_cultural": 0.5,
                "dados_extras": {"evidence": []}
            })
    
    # all_signals já são dicionários conforme conversão anterior
    enriched_signals = biz_synthesizer.analyze_cultural_signals(all_signals, context)
    enriched_map = {s.get('termo'): s for s in enriched_signals}

    if enriched_signals:
        logger.info(f"🧠  BusinessSynthesizer: {len(enriched_signals)} insights gerados")
        logger.info("─" * 70)
        # Exibir top insights baseados em momentum/qualidade
        for sr in sorted(enriched_signals, key=lambda x: x.get('momentum', 0), reverse=True)[:5]:
            logger.info(f"  🎯  {sr.get('termo')} [{sr.get('quality_label')}]")
            logger.info(f"       Fit: {sr.get('campaign_fit', 0)*100:.1f}% | Tension: {sr.get('tension_score', 0):.2f}")
            logger.info(f"       R: {sr.get('recommendation')}")
            logger.info("")
    else:
        logger.info("🧠  BusinessSynthesizer: nenhum insight sintetizado")

    logger.info("=" * 70)

    # --- Mapear termo → SynthesizedSignal para enriquecer Supabase rows ---
    # synth_map: Dict[str, Any] = {}
    # for sr in synthesized:
    #     synth_map[sr.termo] = sr  # último synthesized por termo (1:1 na prática)

    # --- Persistir no Supabase ---
    saved = 0
    skipped = 0
    report_rows = []

    if not dry_run:
        async with httpx.AsyncClient(timeout=15) as http:
            for signal_data in all_signals:
                termo = signal_data.get("termo", "desconhecido")
                ws = ws_map.get(termo)
                synth_data = enriched_map.get(termo)
                
                # Adaptado para V9.7: passamos synth_data como dict
                row = signal_to_supabase_row(termo, signal_data, ws, business_synth=synth_data)
                report_rows.append(row)
                ok = await upsert_signal(http, row)
                if ok:
                    saved += 1
                else:
                    skipped += 1

        logger.info(f"💾  Supabase: {saved} salvos, {skipped} erros")
    else:
        logger.info("🔴  DRY-RUN — nenhum dado enviado ao Supabase")
        for signal_data in all_signals:
            termo = signal_data.get("termo", "desconhecido")
            ws = ws_map.get(termo)
            synth_data = enriched_map.get(termo)
            report_rows.append(signal_to_supabase_row(termo, signal_data, ws, business_synth=synth_data))

    # --- Salvar relatório JSON local ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = PROJECT_ROOT / "data" / f"real_collection_{timestamp}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "total_signals": len(all_signals),
        "weak_signals_detected": len(weak_signals),
        "synthesized_insights": len(enriched_signals),
        "saved_to_supabase": saved,
        "terms": terms,
        "weak_signals": [
            {
                "termo": getattr(ws, 'termo', str(ws)),
                "score": getattr(ws, 'weak_signal_score', 0),
            }
            for ws in weak_signals
        ],
        "business_insights": enriched_signals[:10],
        "all_signals_preview": report_rows[:20],
    }

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    logger.info(f"📄  Relatório salvo em: {report_path.relative_to(PROJECT_ROOT)}")

    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Coleta real via APIs + detecção de sinais fracos")
    parser.add_argument(
        "--terms",
        type=str,
        default=None,
        help="Termos separados por vírgula. Ex: 'funk,pagode,trap'",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executar coleta e detecção sem persistir no Supabase",
    )
    args = parser.parse_args()

    terms = [t.strip() for t in args.terms.split(",")] if args.terms else DEFAULT_TERMS
    report = asyncio.run(run_collection(terms=terms, dry_run=args.dry_run))

    # Resumo final
    print("\n" + "=" * 70)
    print(f"  ✅  Coleta concluída")
    print(f"  📡  Sinais coletados       : {report['total_signals']}")
    print(f"  ⚡  Sinais fracos           : {report['weak_signals_detected']}")
    print(f"  🧠  Fenômenos sintetizados  : {report.get('synthesized_insights', 0)}")
    print(f"  💾  Salvos no Supabase     : {report.get('saved_to_supabase', False)}")
    if report.get("business_insights"):
        top = report["business_insights"][0]
        print(f"  🏆  Top Insight Business   : {top.get('label', 'N/A')}")
        print(f"       └─ Ação Recomendada   : {top.get('recommendation', 'N/A')}")
    elif report.get("weak_signals"):
        top = report["weak_signals"][0]
        print(f"  🏆  Top sinal fraco        : {top['termo']} (score={top['score']:.1f}, badge={top['badge']})")
    print("=" * 70)


if __name__ == "__main__":
    main()
