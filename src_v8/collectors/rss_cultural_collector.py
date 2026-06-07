#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS Cultural Collector — Culture Pulse V9.0  (Sprint S3.6 / P10)
=================================================================
Coleta sinais culturais de fontes RSS brasileiras confiáveis:
  • FAPESP Notícias  (ciência + cultura)
  • Agência Brasil / EBC  (cultura, educação, sociedade)
  • Portal IBGE Notícias  (dados demográficos, sociedade)
  • Folha de S.Paulo - Ilustrada  (cultura, entretenimento)
  • G1 Pop & Arte  (cultura pop, música, cinema)
  • Jornal da USP - Cultura  (academia + cultura)

Cada feed gera CulturalSignal com plataforma='rss_cultural'.
Auto-classifica círculo via keyword matching nos 16 círculos culturais.

Critério de aceite (S3.6-P10): ≥50 sinais/dia vindos de RSS.
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree

logger = logging.getLogger(__name__)

# ── Lazy imports ────────────────────────────────────────────────────────────
try:
    import aiohttp
    _AIOHTTP = True
except ImportError:
    _AIOHTTP = False

try:
    import feedparser  # type: ignore
    _FEEDPARSER = True
except ImportError:
    _FEEDPARSER = False

# ── Project imports (avoid core/__init__.py torch_geometric issue) ──────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from collectors.data_collectors import CulturalSignal
except ImportError:
    # Fallback: define minimal CulturalSignal
    @dataclass
    class CulturalSignal:
        plataforma: str = ""
        termo: str = ""
        momentum: float = 0.0
        volume: int = 0
        sentiment: float = 0.5
        relevancia_cultural: str = "MEDIA"
        dados_extras: dict = field(default_factory=dict)
        timestamp: str = ""
        score_qualidade: float = 0.0
        demographic_data: dict = None
        regional_data: dict = None
        tension_indicators: dict = None
        emerging_profile_signals: dict = None
        fonte_confiabilidade: str = "MEDIA"
        velocity: float = None
        interaction_type: str = None
        sequence_position: int = None
        temporal_delta_hours: float = None
        momentum_velocity: float = None


# ═══════════════════════════════════════════════════════════════════════════════
#  RSS FEED CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

RSS_FEEDS: List[Dict[str, Any]] = [
    {
        "name": "FAPESP Notícias",
        "url": "https://revistapesquisa.fapesp.br/feed/",
        "category": "ciencia_cultura",
        "reliability": "ALTA",
        "language": "pt-BR",
    },
    {
        "name": "Agência Brasil - Cultura",
        "url": "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml",
        "category": "cultura_geral",
        "reliability": "ALTA",
        "language": "pt-BR",
    },
    {
        "name": "IBGE Notícias",
        "url": "https://agenciadenoticias.ibge.gov.br/agencia-noticias.feed",
        "category": "dados_sociedade",
        "reliability": "ALTA",
        "language": "pt-BR",
    },
    {
        "name": "G1 Pop & Arte",
        "url": "https://g1.globo.com/rss/g1/pop-arte/",
        "category": "cultura_pop",
        "reliability": "MEDIA",
        "language": "pt-BR",
    },
    {
        "name": "Folha Ilustrada",
        "url": "https://feeds.folha.uol.com.br/ilustrada/rss091.xml",
        "category": "entretenimento",
        "reliability": "MEDIA",
        "language": "pt-BR",
    },
    {
        "name": "Jornal da USP - Cultura",
        "url": "https://jornal.usp.br/cultura/feed/",
        "category": "academia_cultura",
        "reliability": "ALTA",
        "language": "pt-BR",
    },
    {
        "name": "UOL Entretenimento",
        "url": "https://rfrss.uol.com.br/noticias/entretenimento/index.xml",
        "category": "entretenimento",
        "reliability": "MEDIA",
        "language": "pt-BR",
    },
    {
        "name": "BBC Brasil",
        "url": "https://feeds.bbci.co.uk/portuguese/rss.xml",
        "category": "geral",
        "reliability": "ALTA",
        "language": "pt-BR",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  CIRCLE CLASSIFICATION KEYWORDS
# ═══════════════════════════════════════════════════════════════════════════════

CIRCLE_KEYWORDS: Dict[str, List[str]] = {
    "MUSICA": [
        "música", "samba", "funk", "rap", "mpb", "sertanejo", "forró", "pagode",
        "bossa nova", "axé", "rock", "hip hop", "reggae", "jazz", "cantora",
        "cantor", "show", "festival", "álbum", "spotify", "playlist", "baile",
    ],
    "GASTRONOMIA": [
        "comida", "culinária", "receita", "restaurante", "chef", "gastronomia",
        "feijoada", "acarajé", "cozinha", "alimento", "sabor", "prato",
        "ingrediente", "cachaça", "café", "cerveja", "vinho",
    ],
    "MODA": [
        "moda", "estilo", "fashion", "roupa", "vestuário", "tendência",
        "grife", "desfile", "costura", "tecido", "designer", "coleção",
    ],
    "TECNOLOGIA": [
        "tecnologia", "inteligência artificial", "ia", "startup", "digital",
        "inovação", "app", "software", "dados", "algoritmo", "internet",
        "deepfake", "blockchain", "criptomoeda", "robô", "automação",
    ],
    "ARTE": [
        "arte", "exposição", "museu", "galeria", "pintura", "escultura",
        "fotografia", "cinema", "filme", "documentário", "série", "teatro",
        "dança", "performance", "artista", "obra", "bienal",
    ],
    "ESPORTE": [
        "futebol", "esporte", "olimpíada", "copa", "atleta", "campeonato",
        "seleção", "gol", "jogo", "arena", "torcida", "corrida", "surf",
        "capoeira", "mma", "vôlei", "basquete",
    ],
    "POLITICA": [
        "política", "governo", "eleição", "congresso", "senado", "câmara",
        "presidente", "ministro", "democracia", "protesto", "manifestação",
        "lei", "votação", "reforma", "partido",
    ],
    "SAUDE": [
        "saúde", "medicina", "hospital", "vacina", "pandemia", "sus",
        "doença", "tratamento", "bem-estar", "mental", "terapia", "fitness",
        "nutrição", "psicologia",
    ],
    "EDUCACAO": [
        "educação", "escola", "universidade", "enem", "vestibular", "ensino",
        "professor", "estudante", "pesquisa", "acadêmico", "bolsa", "ciência",
    ],
    "COMPORTAMENTO": [
        "comportamento", "tendência", "geracao", "geração z", "millennial",
        "identidade", "diversidade", "inclusão", "gênero", "representatividade",
        "redes sociais", "influenciador", "viral",
    ],
    "SUSTENTABILIDADE": [
        "sustentabilidade", "meio ambiente", "clima", "reciclagem", "ecologia",
        "desmatamento", "amazônia", "biodiversidade", "poluição", "energia",
        "renovável", "carbono",
    ],
    "RELIGIAO": [
        "religião", "fé", "igreja", "terreiro", "umbanda", "candomblé",
        "evangélico", "católico", "espírita", "sincretismo", "orixá",
    ],
    "ECONOMIA": [
        "economia", "mercado", "emprego", "inflação", "pib", "dólar",
        "bolsa", "investimento", "renda", "desigualdade", "pobreza",
    ],
    "TURISMO": [
        "turismo", "viagem", "destino", "hotel", "praia", "ecoturismo",
        "patrimônio", "carnaval", "festa junina", "são joão",
    ],
    "JUVENTUDE": [
        "jovem", "juventude", "adolescente", "tiktok", "meme", "gíria",
        "periferia", "favela", "comunidade", "batalha de rima", "slam",
    ],
    "FAMILIA": [
        "família", "maternidade", "paternidade", "criança", "idoso",
        "envelhecimento", "casamento", "moradia", "habitação",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  RSS CULTURAL COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class RSSCulturalCollector:
    """
    Async RSS collector for Brazilian cultural sources.
    Returns List[CulturalSignal] with plataforma='rss_cultural'.
    """

    PLATFORM = "rss_cultural"

    def __init__(
        self,
        feeds: Optional[List[Dict]] = None,
        max_items_per_feed: int = 25,
        max_age_hours: int = 72,
        timeout: int = 15,
    ):
        self.feeds = feeds or RSS_FEEDS
        self.max_items_per_feed = max_items_per_feed
        self.max_age_hours = max_age_hours
        self.timeout = timeout
        self._is_real_api = True
        self._seen_hashes: set = set()

    # ──────────────────────────────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────────────────────────────

    async def collect_all(self) -> List[CulturalSignal]:
        """Fetch all feeds and return merged list of CulturalSignal."""
        all_signals: List[CulturalSignal] = []
        tasks = [self._fetch_feed(feed) for feed in self.feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for feed_cfg, result in zip(self.feeds, results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️  RSS feed '{feed_cfg['name']}' failed: {result}")
                continue
            all_signals.extend(result)

        # Deduplicate by title hash
        unique: List[CulturalSignal] = []
        for sig in all_signals:
            h = sig.dados_extras.get("title_hash", "")
            if h and h in self._seen_hashes:
                continue
            self._seen_hashes.add(h)
            unique.append(sig)

        logger.info(
            f"📡 RSS: {len(unique)} unique signals from {len(self.feeds)} feeds "
            f"(raw={len(all_signals)})"
        )
        return unique

    async def collect_cultural_data(
        self, termo: str, context: Dict[str, Any] = None
    ) -> Optional[CulturalSignal]:
        """
        Interface compatible with other V8 collectors.
        Collects all RSS and returns the first signal matching `termo`.
        Considers Tier (V9.9) for historical filtering.
        """
        user_tier = context.get('user_tier', 'free').lower() if context else 'free'
        tier_days = {
            'free': 1,
            'pro': 7,
            'executive': 30,
            'enterprise': 90
        }
        max_days = tier_days.get(user_tier, 1)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)

        signals = await self.collect_all()
        termo_lower = termo.lower()
        
        filtered_signals = []
        for sig in signals:
            # RSS signals might not have a full timestamp as float/int, check isoformat
            try:
                sig_ts = datetime.fromisoformat(sig.timestamp.replace("Z", "+00:00"))
                if sig_ts < cutoff:
                    continue
            except:
                pass # If timestamp is invalid, keep it (fallback)

            text = (sig.termo + " " + sig.dados_extras.get("title", "")).lower()
            if termo_lower in text:
                filtered_signals.append(sig)
        
        # Return first matches
        return filtered_signals[0] if filtered_signals else (signals[0] if signals else None)

    # ──────────────────────────────────────────────────────────────────────
    #  FEED FETCHING
    # ──────────────────────────────────────────────────────────────────────

    async def _fetch_feed(self, feed_cfg: Dict) -> List[CulturalSignal]:
        """Fetch a single RSS feed and convert entries to CulturalSignal."""
        url = feed_cfg["url"]
        name = feed_cfg["name"]
        signals: List[CulturalSignal] = []

        try:
            if _AIOHTTP:
                raw_xml = await self._fetch_with_aiohttp(url)
            else:
                raw_xml = await self._fetch_with_urllib(url)

            if not raw_xml:
                logger.warning(f"⚠️  Empty response from {name}")
                return signals

            entries = self._parse_feed(raw_xml)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours)

            for i, entry in enumerate(entries[: self.max_items_per_feed]):
                sig = self._entry_to_signal(entry, feed_cfg, cutoff)
                if sig is not None:
                    sig.sequence_position = i + 1
                    signals.append(sig)

            logger.info(f"  ✅ {name}: {len(signals)} signals")

        except Exception as e:
            logger.warning(f"⚠️  Feed {name}: {e}")

        return signals

    async def _fetch_with_aiohttp(self, url: str) -> Optional[str]:
        """Fetch RSS XML using aiohttp."""
        headers = {
            "User-Agent": "CulturePulse/9.0 (RSS Cultural Collector; +https://culturepulse.ai)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    # Handle encoding: some BR feeds use ISO-8859-1
                    raw_bytes = await resp.read()
                    for enc in ("utf-8", "latin-1", "iso-8859-1", "cp1252"):
                        try:
                            return raw_bytes.decode(enc)
                        except (UnicodeDecodeError, LookupError):
                            continue
                    return raw_bytes.decode("utf-8", errors="replace")
                logger.warning(f"HTTP {resp.status} from {url}")
                return None

    async def _fetch_with_urllib(self, url: str) -> Optional[str]:
        """Fallback: fetch using urllib (sync in thread)."""
        import urllib.request

        def _do():
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "CulturePulse/9.0 (RSS Cultural Collector)",
                },
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _do)

    # ──────────────────────────────────────────────────────────────────────
    #  PARSING
    # ──────────────────────────────────────────────────────────────────────

    def _parse_feed(self, raw_xml: str) -> List[Dict]:
        """Parse RSS/Atom XML into list of entry dicts."""
        if _FEEDPARSER:
            feed = feedparser.parse(raw_xml)
            return [
                {
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", e.get("description", "")),
                    "published": e.get("published_parsed") or e.get("updated_parsed"),
                    "tags": [t.get("term", "") for t in e.get("tags", [])],
                }
                for e in feed.entries
            ]

        # Fallback: manual XML parsing
        return self._parse_xml_manual(raw_xml)

    def _parse_xml_manual(self, raw_xml: str) -> List[Dict]:
        """Minimal RSS parser without feedparser."""
        entries = []
        try:
            root = ElementTree.fromstring(raw_xml)
            # RSS 2.0
            for item in root.iter("item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                desc = (item.findtext("description") or "").strip()
                pub = (item.findtext("pubDate") or "").strip()
                entries.append({
                    "title": title,
                    "link": link,
                    "summary": desc,
                    "published": self._parse_date_string(pub),
                    "tags": [],
                })
            # Atom
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry_el in root.findall(".//atom:entry", ns):
                title = (entry_el.findtext("atom:title", "", ns) or "").strip()
                link_el = entry_el.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
                summary = (entry_el.findtext("atom:summary", "", ns) or "").strip()
                pub = (entry_el.findtext("atom:published", "", ns) or
                       entry_el.findtext("atom:updated", "", ns) or "").strip()
                entries.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": self._parse_date_string(pub),
                    "tags": [],
                })
        except ElementTree.ParseError as e:
            logger.warning(f"XML parse error: {e}")
        return entries

    # ──────────────────────────────────────────────────────────────────────
    #  SIGNAL CONVERSION
    # ──────────────────────────────────────────────────────────────────────

    def _entry_to_signal(
        self, entry: Dict, feed_cfg: Dict, cutoff: datetime
    ) -> Optional[CulturalSignal]:
        """Convert one RSS entry into a CulturalSignal."""
        title = self._clean_html(entry.get("title", ""))
        summary = self._clean_html(entry.get("summary", ""))
        link = entry.get("link", "")
        pub = entry.get("published")

        if not title:
            return None

        # Parse and filter by age
        pub_dt = self._to_datetime(pub)
        if pub_dt and pub_dt < cutoff:
            return None  # Too old

        # Combined text for classification
        full_text = f"{title} {summary}"

        # Classify circle
        circulo, circle_score = self._classify_circle(full_text)

        # Extract main term (most relevant keyword)
        termo = self._extract_termo(full_text, circulo)

        # Compute momentum (based on source reliability + recency)
        momentum = self._compute_momentum(feed_cfg, pub_dt)

        # Simple sentiment (neutral for news; could be enhanced with NLP)
        sentiment = self._estimate_sentiment(full_text)

        # Title hash for dedup
        title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:12]

        # Relevance classification
        if circle_score >= 3:
            relevancia = "ALTA"
        elif circle_score >= 1:
            relevancia = "MEDIA"
        else:
            relevancia = "BAIXA"

        ts = pub_dt.isoformat() if pub_dt else datetime.now(timezone.utc).isoformat()

        return CulturalSignal(
            plataforma=self.PLATFORM,
            termo=termo,
            momentum=momentum,
            volume=1,  # Each article = 1 unit
            sentiment=sentiment,
            relevancia_cultural=relevancia,
            dados_extras={
                "title": title,
                "summary": summary[:500],
                "link": link,
                "source": feed_cfg["name"],
                "source_category": feed_cfg.get("category", "geral"),
                "circulo": circulo,
                "circle_score": circle_score,
                "tags": entry.get("tags", []),
                "title_hash": title_hash,
            },
            timestamp=ts,
            score_qualidade=min(1.0, circle_score * 0.2 + 0.3),
            is_verified=True,  # RSS de fontes oficiais é verificado
            accuracy_score=0.9 if feed_cfg.get("reliability") == "ALTA" else 0.7,
            reliability=feed_cfg.get("reliability", "MEDIA"),
            source_url=link,
            source_category=feed_cfg.get("category", "geral"),
            image_url=None,  # RSS básico não traz imagem, mas campo existe
            interaction_type="view",  # RSS = passive consumption
        )

    # ──────────────────────────────────────────────────────────────────────
    #  CLASSIFICATION HELPERS
    # ──────────────────────────────────────────────────────────────────────

    def _classify_circle(self, text: str) -> Tuple[str, int]:
        """Match text against circle keywords. Returns (circle, score)."""
        text_lower = text.lower()
        best_circle = "COMPORTAMENTO"  # default
        best_score = 0

        for circle, keywords in CIRCLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_circle = circle

        return best_circle, best_score

    def _extract_termo(self, text: str, circulo: str) -> str:
        """Extract the most representative keyword as the 'termo'."""
        text_lower = text.lower()
        keywords = CIRCLE_KEYWORDS.get(circulo, [])

        # Find first matching keyword in text
        for kw in keywords:
            if kw in text_lower:
                return kw

        # Fallback: use first 2 words of title
        words = text.split()[:3]
        return " ".join(words).lower().strip()[:30] if words else circulo.lower()

    def _compute_momentum(
        self, feed_cfg: Dict, pub_dt: Optional[datetime]
    ) -> float:
        """
        Momentum = base_reliability * recency_factor.
        More recent = higher momentum. Reliable sources get a boost.
        """
        reliability_map = {"ALTA": 80.0, "MEDIA": 60.0, "BAIXA": 40.0}
        base = reliability_map.get(feed_cfg.get("reliability", "MEDIA"), 60.0)

        if pub_dt:
            hours_ago = max(
                0.1,
                (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600,
            )
            # Exponential decay: half-life = 24h
            recency = 2.0 ** (-hours_ago / 24.0)
        else:
            recency = 0.5

        return round(base * recency, 2)

    def _estimate_sentiment(self, text: str) -> float:
        """Very simple keyword-based sentiment. Returns 0..1 (0.5=neutral)."""
        text_lower = text.lower()

        positive = [
            "sucesso", "conquista", "inovação", "avanço", "crescimento",
            "celebra", "premiado", "recorde", "vitória", "destaque",
        ]
        negative = [
            "crise", "problema", "violência", "queda", "perda",
            "desastre", "mortes", "conflito", "denúncia", "escândalo",
        ]

        pos = sum(1 for w in positive if w in text_lower)
        neg = sum(1 for w in negative if w in text_lower)

        if pos + neg == 0:
            return 0.5
        return round(0.5 + 0.5 * (pos - neg) / (pos + neg), 3)

    # ──────────────────────────────────────────────────────────────────────
    #  UTILITIES
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _clean_html(text: str) -> str:
        """Remove HTML tags and decode entities."""
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _to_datetime(pub) -> Optional[datetime]:
        """Convert parsed time struct or string to datetime."""
        if pub is None:
            return None
        if hasattr(pub, "tm_year"):
            # time.struct_time from feedparser
            import calendar
            ts = calendar.timegm(pub)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        if isinstance(pub, str):
            return RSSCulturalCollector._parse_date_string(pub)
        if isinstance(pub, datetime):
            return pub if pub.tzinfo else pub.replace(tzinfo=timezone.utc)
        return None

    @staticmethod
    def _parse_date_string(s: str) -> Optional[datetime]:
        """Try several date formats common in RSS."""
        if not s:
            return None
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",      # RFC 822
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",            # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  SUPABASE PERSISTENCE HELPER
# ═══════════════════════════════════════════════════════════════════════════════

async def persist_rss_signals(signals: List[CulturalSignal]) -> Dict[str, int]:
    """Write RSS signals to Supabase cultural_signals via supabase_writer."""
    try:
        from collectors.supabase_writer import SupabaseWriter
        writer = SupabaseWriter()
        written = 0
        errors = 0
        for sig in signals:
            try:
                writer.write_signal(sig)
                written += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    logger.warning(f"  write error: {e}")
        return {"written": written, "errors": errors}
    except ImportError:
        logger.warning("supabase_writer not available; skipping persistence")
        return {"written": 0, "errors": 0, "note": "writer_unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

async def _self_test():
    """Quick module validation."""
    print("=" * 65)
    print("  S3.6 — RSS Cultural Collector: module check")
    print("=" * 65)

    collector = RSSCulturalCollector(max_items_per_feed=5, max_age_hours=168)
    signals = await collector.collect_all()

    print(f"\n  Feeds configured: {len(collector.feeds)}")
    print(f"  Signals collected: {len(signals)}")

    if signals:
        # Distribution by circle
        circles: Dict[str, int] = {}
        sources: Dict[str, int] = {}
        for s in signals:
            c = s.dados_extras.get("circulo", "?")
            src = s.dados_extras.get("source", "?")
            circles[c] = circles.get(c, 0) + 1
            sources[src] = sources.get(src, 0) + 1

        print("\n  By circle:")
        for c, n in sorted(circles.items(), key=lambda x: -x[1]):
            print(f"    {c:20s}: {n}")

        print("\n  By source:")
        for src, n in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"    {src:30s}: {n}")

        print("\n  Sample signals:")
        for s in signals[:5]:
            title = s.dados_extras.get("title", "")[:50]
            print(
                f"    [{s.dados_extras.get('circulo', '?'):15s}] "
                f"mom={s.momentum:6.1f} rel={s.relevancia_cultural:5s} "
                f"'{title}'"
            )

    ok = len(signals) > 0
    print(f"\n  {'✅' if ok else '❌'} Module loads OK — {len(signals)} signals collected")
    return signals


if __name__ == "__main__":
    asyncio.run(_self_test())
