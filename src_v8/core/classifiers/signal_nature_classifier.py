#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Nature Classifier - Culture Pulse V9.1
Classifica a NATUREZA CULTURAL dos sinais fracos detectados

Foco: Detectar NUANCES CULTURAIS profundas além de palavras-chave
- Códigos linguísticos (gírias, regionalismos)
- Tensões culturais reais vs fabricadas
- Origem em círculos específicos vs difusa
- Crossovers genuínos vs forçados
- Crescimento orgânico vs artificial

5 Categorias:
1. ORGÂNICO - Movimento cultural autêntico com códigos próprios
2. RESONÂNCIA - Autêntico + amplificação que preserva códigos
3. COMERCIAL TRANSPARENTE - Campanha clara, não simula cultura
4. SIMULAÇÃO CULTURAL - Marketing que simula códigos sem vivência real
5. APROPRIAÇÃO - Uso descontextualizado de símbolos culturais
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import logging

logger = logging.getLogger(__name__)

@dataclass
class SignalNatureResult:
    """Resultado da classificação de natureza do sinal"""
    categoria: str  # ORGÂNICO, RESONÂNCIA, COMERCIAL, SIMULAÇÃO, APROPRIAÇÃO
    confianca: float  # 0-1
    score_organico: float  # 0-100
    score_comercial: float  # 0-100
    score_apropriacao: float  # 0-100
    evidencias: List[str]
    flags: List[str]
    nuances_detectadas: Dict[str, Any]


class SignalNatureClassifier:
    """
    Classificador de Natureza Cultural de Sinais Fracos
    Detecta nuances culturais profundas além de palavras-chave
    """
    
    def __init__(self):
        # Marcadores linguísticos brasileiros AUTÊNTICOS (gírias/regionalismos)
        self.authentic_codes = {
            'sp_periferia': ['rolê', 'quebrada', 'corre', 'mano', 'truta', 'tapioca', 'breck'],
            'rio_favela': ['bonde', 'papo reto', 'suave', 'valeu', 'responsa', 'piseiro'],
            'nordeste': ['oxente', 'vixe', 'massa', 'arretado', 'cabra', 'danado', 'trem'],
            'sul': ['tchê', 'bah', 'guri', 'prenda', 'capaz', 'barbaridade'],
            'nacional': ['cara', 'tipo assim', 'né', 'sério?', 'cê é loko', 'massa']
        }
        
        # Marcadores SIMULAÇÃO (gírias forçadas/deslocadas)
        self.simulation_markers = [
            r'\bpeople\b.*\bvery\b',  # Mistura artificial EN-PT
            r'\bmano\b.*(luxo|premium|exclusive)',  # Gíria + contexto elite
            r'(favela|periferia).*(empoderamento|resiliência)',  # Jargão NGO
            r'(autêntico|genuíno|raiz).{0,30}(marca|produto|campanha)',  # Auto-declaração
            r'\b(cool|hipster|descolado)\b',  # Coolhunting superficial
        ]
        
        # Marcadores COMERCIAIS óbvios
        self.commercial_markers = [
            r'#\w+Oficial',  # Hashtag oficial
            r'(patrocinado|publi|publicidade|ad)',
            r'(lançamento|nova coleção|disponível)',
            r'(compre|adquira|garanta|aproveite)',
            r'www\.\w+\.com',  # Links comerciais
            r'(desconto|promoção|oferta)',
        ]
        
        # Marcadores APROPRIAÇÃO cultural
        self.appropriation_markers = {
            'simbolos_sagrados': ['cocar', 'mandala', 'cruz', 'estrela de davi', 'yin yang'],
            'religiosos_afro': ['orixá', 'candomblé', 'umbanda', 'axé', 'guia', 'santo'],
            'indigenas': ['índio', 'tribal', 'primitivo', 'selvagem', 'exótico'],
            'estereotipos': ['sambista', 'malandro', 'sensual', 'tropical paradise'],
        }
        
        # Palavras que indicam TENSÃO CULTURAL REAL
        self.real_tension_markers = [
            'ostentação', 'periferia', 'centro', 'favela', 'classe', 
            'desigualdade', 'racismo', 'preconceito', 'exclusão',
            'resistência', 'representatividade', 'invisibilidade'
        ]
        
        logger.info("✅ SignalNatureClassifier inicializado com dicionários culturais BR")
    
    def classify(self, 
                 termo: str,
                 mencoes: List[str],
                 contextos: List[str],
                 plataformas: List[str],
                 tensoes: List[Dict[str, Any]],
                 demografico: Dict[str, Any],
                 velocity: float,
                 volume: int,
                 sentiment: float) -> SignalNatureResult:
        """
        Classifica a natureza cultural de um sinal fraco
        
        Args:
            termo: Termo do sinal
            mencoes: Lista de menções/textos exemplos
            contextos: Contextos culturais detectados
            plataformas: Plataformas de origem
            tensoes: Tensões culturais detectadas
            demografico: Dados demográficos (regiões, etc)
            velocity: Velocidade de crescimento
            volume: Volume de menções
            sentiment: Sentimento geral
        
        Returns:
            SignalNatureResult com classificação e evidências
        """
        texto_completo = f"{termo} " + " ".join(mencoes[:10])  # Amostra
        texto_lower = texto_completo.lower()
        
        evidencias = []
        flags = []
        nuances = {}
        
        # ============================================
        # 1. DETECTAR CÓDIGOS LINGUÍSTICOS AUTÊNTICOS
        # ============================================
        authentic_score = 0
        codes_found = []
        
        for regiao, codes in self.authentic_codes.items():
            found = [code for code in codes if code in texto_lower]
            if found:
                authentic_score += len(found) * 10
                codes_found.extend(found)
                evidencias.append(f"Códigos autênticos {regiao}: {', '.join(found)}")
        
        nuances['codigos_autenticidade'] = codes_found
        
        # ============================================
        # 2. DETECTAR SIMULAÇÃO (gírias forçadas)
        # ============================================
        simulation_score = 0
        
        for pattern in self.simulation_markers:
            if re.search(pattern, texto_lower):
                simulation_score += 20
                flags.append(f"Simulação detectada: {pattern[:30]}...")
        
        # Mistura artificial de registros
        if ('mano' in texto_lower and 'premium' in texto_lower):
            simulation_score += 15
            flags.append("Mistura artificial: gíria + contexto elite")
        
        # ============================================
        # 3. DETECTAR MARCADORES COMERCIAIS
        # ============================================
        commercial_score = 0
        
        for pattern in self.commercial_markers:
            matches = re.findall(pattern, texto_lower)
            if matches:
                commercial_score += len(matches) * 15
                evidencias.append(f"Marcador comercial: {matches[0]}")
        
        # Hashtags oficiais
        hashtags = re.findall(r'#\w+', texto_completo)
        if any('oficial' in h.lower() for h in hashtags):
            commercial_score += 25
            evidencias.append("Hashtag oficial detectada")
        
        # ============================================
        # 4. DETECTAR APROPRIAÇÃO CULTURAL
        # ============================================
        appropriation_score = 0
        
        for categoria, termos in self.appropriation_markers.items():
            found = [t for t in termos if t in texto_lower]
            if found:
                appropriation_score += len(found) * 15
                flags.append(f"Apropriação {categoria}: {', '.join(found)}")
        
        # Contexto de uso: se usa termos sagrados/indígenas em contexto comercial
        if appropriation_score > 0 and commercial_score > 20:
            appropriation_score += 30
            flags.append("ALERTA: Símbolos culturais em contexto comercial")
        
        # ============================================
        # 5. TENSÕES CULTURAIS REAIS vs FABRICADAS
        # ============================================
        tension_score = 0
        
        if tensoes and len(tensoes) > 0:
            for tensao in tensoes:
                tipo = tensao.get('type', '').lower()
                intensidade = tensao.get('intensity', 0)
                
                # Tensões autênticas
                if any(marker in tipo for marker in self.real_tension_markers):
                    tension_score += intensidade * 20
                    evidencias.append(f"Tensão cultural real: {tipo} ({intensidade:.0%})")
        
        nuances['tensoes_reais'] = len([t for t in tensoes if t.get('intensity', 0) > 0.5])
        
        # ============================================
        # 6. ORIGEM GEOGRÁFICA/SOCIAL ESPECÍFICA
        # ============================================
        origin_score = 0
        
        if demografico:
            regioes = demografico.get('regioes', {})
            if regioes:
                # Origem concentrada (orgânico) vs difusa (fabricado)
                concentracao = max(regioes.values()) if regioes else 0
                
                if concentracao > 0.7:  # >70% de uma região
                    origin_score += 25
                    regiao_principal = max(regioes, key=regioes.get)
                    evidencias.append(f"Origem concentrada: {regiao_principal} ({concentracao:.0%})")
                elif concentracao < 0.3:  # Muito difuso
                    simulation_score += 15
                    flags.append("Origem difusa/fabricada (sem concentração regional)")
        
        nuances['origem_especifica'] = origin_score > 15
        
        # ============================================
        # 7. CROSSOVERS CULTURAIS (dissonância)
        # ============================================
        crossover_score = 0
        
        # Detectar crossover genuíno (contextos diferentes)
        contextos_unicos = set(contextos)
        if len(contextos_unicos) >= 2:
            # Ex: "político" + "moda" = crossover genuíno brasileiro
            crossover_score += 20
            evidencias.append(f"Crossover cultural: {', '.join(list(contextos_unicos)[:3])}")
        
        nuances['crossover_detectado'] = len(contextos_unicos) >= 2
        
        # ============================================
        # 8. CRESCIMENTO TEMPORAL (orgânico vs spike)
        # ============================================
        growth_score = 0
        
        # Velocidade gradual = orgânico, spike = artificial
        if velocity < 3.0:  # Crescimento gradual
            growth_score += 20
            evidencias.append(f"Crescimento orgânico (velocity: {velocity:.1f})")
        elif velocity > 8.0:  # Spike artificial
            simulation_score += 20
            flags.append(f"Spike suspeito (velocity: {velocity:.1f})")
        
        # Volume moderado de weak signal (<1000) = orgânico
        if volume < 1000:
            growth_score += 15
            evidencias.append(f"Volume típico de weak signal ({volume} menções)")
        
        nuances['crescimento_organico'] = velocity < 3.0 and volume < 1000
        
        # ============================================
        # 9. PLATAFORMAS DE ORIGEM
        # ============================================
        platform_score = 0
        
        # TikTok/Reddit = mais autêntico, muitos ads = comercial
        if 'tiktok' in [p.lower() for p in plataformas]:
            platform_score += 15
        if 'reddit' in [p.lower() for p in plataformas]:
            platform_score += 10
        
        nuances['plataformas_autenticidade'] = platform_score
        
        # ============================================
        # CALCULAR SCORES FINAIS
        # ============================================
        
        # Score Orgânico
        score_organico = min(100, 
            authentic_score +  # Códigos autênticos
            tension_score +    # Tensões reais
            origin_score +     # Origem específica
            crossover_score +  # Crossover genuíno
            growth_score +     # Crescimento gradual
            platform_score     # Plataformas autênticas
        )
        
        # Score Comercial
        score_comercial = min(100, commercial_score)
        
        # Score Apropriação
        score_apropriacao = min(100, appropriation_score)
        
        # Score Simulação (subset de comercial)
        score_simulacao = min(100, simulation_score)
        
        # ============================================
        # CLASSIFICAR CATEGORIA FINAL
        # ============================================
        
        categoria, confianca = self._determine_category(
            score_organico,
            score_comercial,
            score_apropriacao,
            score_simulacao,
            evidencias,
            flags
        )
        
        nuances['scores'] = {
            'organico': score_organico,
            'comercial': score_comercial,
            'apropriacao': score_apropriacao,
            'simulacao': score_simulacao
        }
        
        return SignalNatureResult(
            categoria=categoria,
            confianca=confianca,
            score_organico=score_organico,
            score_comercial=score_comercial,
            score_apropriacao=score_apropriacao,
            evidencias=evidencias,
            flags=flags,
            nuances_detectadas=nuances
        )
    
    def _determine_category(self,
                          score_organico: float,
                          score_comercial: float,
                          score_apropriacao: float,
                          score_simulacao: float,
                          evidencias: List[str],
                          flags: List[str]) -> Tuple[str, float]:
        """
        Determina categoria final e confiança
        
        Prioridade:
        1. APROPRIAÇÃO (se score > 50, crítico)
        2. SIMULAÇÃO CULTURAL (se simulação > 40)
        3. COMERCIAL TRANSPARENTE (se comercial > 50 e simulação < 20)
        4. RESONÂNCIA (se orgânico > 40 e comercial > 20)
        5. ORGÂNICO (se orgânico > 40 e comercial < 20)
        """
        
        # 1. APROPRIAÇÃO (prioridade máxima - crítico)
        if score_apropriacao > 50:
            confianca = min(0.95, score_apropriacao / 100)
            return "APROPRIAÇÃO", confianca
        
        # 2. SIMULAÇÃO CULTURAL (astroturfing)
        if score_simulacao > 40:
            confianca = min(0.90, score_simulacao / 100)
            return "SIMULAÇÃO", confianca
        
        # 3. COMERCIAL TRANSPARENTE (campanha clara)
        if score_comercial > 50 and score_simulacao < 20:
            confianca = min(0.85, score_comercial / 100)
            return "COMERCIAL", confianca
        
        # 4. RESONÂNCIA (autêntico + amplificação)
        if score_organico > 40 and 20 < score_comercial < 50:
            # Tem códigos autênticos MAS também amplificação comercial
            confianca = min(0.80, score_organico / 150)
            return "RESONÂNCIA", confianca
        
        # 5. ORGÂNICO (padrão para weak signals reais)
        if score_organico > 40:
            confianca = min(0.90, score_organico / 100)
            return "ORGÂNICO", confianca
        
        # Caso ambíguo: usar score dominante
        scores = {
            'ORGÂNICO': score_organico,
            'COMERCIAL': score_comercial,
            'APROPRIAÇÃO': score_apropriacao,
            'SIMULAÇÃO': score_simulacao
        }
        categoria_dominante = max(scores, key=scores.get)
        confianca = min(0.60, scores[categoria_dominante] / 100)  # Baixa confiança
        
        return categoria_dominante, confianca
    
    def get_recommendation(self, result: SignalNatureResult, bot_risk_level: str) -> Dict[str, Any]:
        """
        Gera recomendação baseada em natureza + bot risk
        
        Args:
            result: Resultado da classificação
            bot_risk_level: "HIGH", "MEDIUM", "LOW"
        
        Returns:
            Dict com prioridade, ação e justificativa
        """
        categoria = result.categoria
        bot = bot_risk_level
        
        # Matriz de prioridade
        matrix = {
            # CRÍTICO (revisar imediatamente)
            ('APROPRIAÇÃO', 'HIGH'): ('CRÍTICO', '🔴 Apropriação + Bots - Alerta máximo'),
            ('APROPRIAÇÃO', 'MEDIUM'): ('CRÍTICO', '🔴 Apropriação suspeita - Investigar'),
            ('SIMULAÇÃO', 'HIGH'): ('CRÍTICO', '🔴 Astroturfing com bots - Fake grassroots'),
            
            # ALTA (investigar)
            ('SIMULAÇÃO', 'MEDIUM'): ('ALTA', '🟡 Simulação cultural - Verificar autenticidade'),
            ('APROPRIAÇÃO', 'LOW'): ('ALTA', '🟡 Apropriação sutil - Validar contexto'),
            ('ORGÂNICO', 'HIGH'): ('ALTA', '🟡 Códigos autênticos + alto bot risk - Validar'),
            
            # MÉDIA (monitorar)
            ('COMERCIAL', 'HIGH'): ('MÉDIA', '🟢 Campanha com bots - Normal'),
            ('COMERCIAL', 'MEDIUM'): ('MÉDIA', '🟢 Campanha mista - Monitorar'),
            ('RESONÂNCIA', 'MEDIUM'): ('MÉDIA', '🟢 Amplificação típica - OK'),
            ('SIMULAÇÃO', 'LOW'): ('MÉDIA', '🟡 Simulação sutil - Observar'),
            
            # BAIXA (apenas catalogar)
            ('COMERCIAL', 'LOW'): ('BAIXA', '🟢 Campanha transparente - OK'),
            ('RESONÂNCIA', 'LOW'): ('BAIXA', '🟢 Amplificação legítima - OK'),
            
            # AUTÊNTICO (prioridade máxima para análise!)
            ('ORGÂNICO', 'LOW'): ('AUTÊNTICO', '✅ WEAK SIGNAL PURO - Priorizar análise!'),
            ('ORGÂNICO', 'MEDIUM'): ('AUTÊNTICO', '✅ Provável autêntico - Analisar contexto'),
            ('RESONÂNCIA', 'HIGH'): ('MÉDIA', '🟡 Amplificação com bots - Verificar preservação cultural'),
        }
        
        key = (categoria, bot)
        prioridade, mensagem = matrix.get(key, ('MÉDIA', '🟡 Classificação ambígua - Revisar'))
        
        # Ações sugeridas
        acoes = {
            'CRÍTICO': 'Revisar imediatamente e considerar alerta automático',
            'ALTA': 'Agendar revisão manual nas próximas 24h',
            'MÉDIA': 'Monitorar evolução, revisar se escalar',
            'BAIXA': 'Catalogar e arquivar, sem revisão necessária',
            'AUTÊNTICO': 'PRIORIZAR para análise de weak signal! Nuances culturais genuínas detectadas'
        }
        
        return {
            'prioridade': prioridade,
            'mensagem': mensagem,
            'acao': acoes[prioridade],
            'confianca_classificacao': result.confianca,
            'evidencias_principais': result.evidencias[:3],
            'flags_atencao': result.flags if result.flags else ['Nenhum flag de atenção']
        }

    def get_stability_recommendation(
        self,
        result: SignalNatureResult,
        stability_status: str,
        bot_risk_level: str = "LOW",
    ) -> Dict[str, Any]:
        """
        Gera recomendação cruzando Nature × Stability × Bot Risk.

        Combina a classificação de natureza (ORGÂNICO/COMERCIAL/etc.) com
        o status de estabilidade de cluster (estável/emergindo/fragmentando/
        instável/sem_dados) para produzir uma decisão integrada.

        Args:
            result:           SignalNatureResult da classificação
            stability_status: Valor de StabilityStatus (str): estável, emergindo,
                              fragmentando, instável, sem_dados
            bot_risk_level:   "HIGH", "MEDIUM", "LOW"

        Returns:
            Dict com prioridade, mensagem, ação, nature_label, stability_label
        """
        categoria = result.categoria
        stab = stability_status

        # ── Matriz 5×5: Nature × Stability ──────────────────────────────
        # Chave: (categoria, stability_status)
        # Valor: (prioridade, emoji + mensagem)
        stability_matrix: Dict[tuple, tuple] = {
            # ── ORGÂNICO ─────────────────────────────────────────────────
            ("ORGÂNICO", "estável"):       ("VALIDADO",     "✅ Weak signal autêntico em cluster estável — confiável"),
            ("ORGÂNICO", "emergindo"):     ("OPORTUNIDADE", "🔵 Weak signal puro em cluster emergente — janela de oportunidade!"),
            ("ORGÂNICO", "fragmentando"):  ("INVESTIGAR",   "⚠️ Sinal orgânico em cluster fragmentando — investigar causa"),
            ("ORGÂNICO", "instável"):      ("ALERTA",       "🔴 Sinal autêntico em caos cultural — alto risco de perda"),
            ("ORGÂNICO", "sem_dados"):     ("MONITORAR",    "⚪ Sinal orgânico sem contexto de cluster — coletar mais dados"),
            # ── RESONÂNCIA ───────────────────────────────────────────────
            ("RESONÂNCIA", "estável"):     ("VALIDADO",     "✅ Amplificação saudável preservando códigos culturais"),
            ("RESONÂNCIA", "emergindo"):   ("OPORTUNIDADE", "🔵 Amplificação acelerando cluster emergente — surfar onda"),
            ("RESONÂNCIA", "fragmentando"):("INVESTIGAR",   "⚠️ Amplificação em audiência que se dispersa — ajustar tom"),
            ("RESONÂNCIA", "instável"):    ("ALERTA",       "🔴 Narrativa amplificada perdendo coerência — risco reputacional"),
            ("RESONÂNCIA", "sem_dados"):   ("MONITORAR",    "⚪ Amplificação sem mapa de clusters — observar evolução"),
            # ── COMERCIAL ────────────────────────────────────────────────
            ("COMERCIAL", "estável"):      ("OK",           "🟢 Campanha em território cultural estável — prosseguir"),
            ("COMERCIAL", "emergindo"):    ("MONITORAR",    "🟡 Campanha surfando emergência cultural — monitorar autenticidade"),
            ("COMERCIAL", "fragmentando"): ("INVESTIGAR",   "⚠️ Campanha em terreno fragmentando — considerar reposicionamento"),
            ("COMERCIAL", "instável"):     ("CRÍTICO",      "🔴 ABORT — campanha em território culturalmente volátil"),
            ("COMERCIAL", "sem_dados"):    ("MONITORAR",    "⚪ Campanha sem contexto cultural — coletar dados antes de escalar"),
            # ── SIMULAÇÃO ────────────────────────────────────────────────
            ("SIMULAÇÃO", "estável"):      ("INVESTIGAR",   "⚠️ Astroturfing mascarando estabilidade — verificar autenticidade"),
            ("SIMULAÇÃO", "emergindo"):    ("ALERTA",       "🔴 Astroturfing fabricando emergência cultural — fake grassroots"),
            ("SIMULAÇÃO", "fragmentando"): ("CRÍTICO",      "🔴 CRÍTICO — manipulação em cluster fragmentando"),
            ("SIMULAÇÃO", "instável"):     ("CRÍTICO",      "🔴 MÁXIMO — simulação pode ser causa da instabilidade"),
            ("SIMULAÇÃO", "sem_dados"):    ("INVESTIGAR",   "⚠️ Simulação sem contexto — investigar intenção"),
            # ── APROPRIAÇÃO ──────────────────────────────────────────────
            ("APROPRIAÇÃO", "estável"):    ("CRÍTICO",      "🔴 Apropriação de cultura estável — alto risco reputacional"),
            ("APROPRIAÇÃO", "emergindo"):  ("CRÍTICO",      "🔴 Apropriação de emergência cultural — oportunismo detectado"),
            ("APROPRIAÇÃO", "fragmentando"):("CRÍTICO",     "🔴 MÁXIMO — apropriação acelera fragmentação cultural"),
            ("APROPRIAÇÃO", "instável"):   ("CRÍTICO",      "🔴 MÁXIMO — apropriação causando dano cultural ativo"),
            ("APROPRIAÇÃO", "sem_dados"):  ("ALERTA",       "🔴 Apropriação sem contexto — assumir risco alto"),
        }

        key = (categoria, stab)
        prioridade, mensagem = stability_matrix.get(
            key, ("MONITORAR", "🟡 Combinação não mapeada — revisar manualmente")
        )

        # ── Ações por prioridade ─────────────────────────────────────────
        acoes_map = {
            "OPORTUNIDADE": "PRIORIZAR análise imediata — possível tendência cultural nascendo",
            "VALIDADO":     "Sinal confirmado — integrar ao relatório executivo",
            "OK":           "Prosseguir normalmente — nenhuma ação necessária",
            "MONITORAR":    "Acompanhar evolução nas próximas 48h",
            "INVESTIGAR":   "Agendar revisão manual nas próximas 24h — cruzar com outras fontes",
            "ALERTA":       "Ativar monitoramento intensivo — preparar plano de contingência",
            "CRÍTICO":      "AÇÃO IMEDIATA — revisar, pausar campanhas se necessário, escalar",
        }

        # ── Merge com bot risk (do método original) ──────────────────────
        bot_modifier = ""
        if bot_risk_level == "HIGH":
            if prioridade in ("MONITORAR", "OK", "VALIDADO"):
                prioridade = "INVESTIGAR"
                bot_modifier = " [escalado por bot risk HIGH]"
            elif prioridade == "INVESTIGAR":
                prioridade = "ALERTA"
                bot_modifier = " [escalado por bot risk HIGH]"

        return {
            "prioridade": prioridade,
            "mensagem": mensagem + bot_modifier,
            "acao": acoes_map.get(prioridade, "Revisar manualmente"),
            "nature_label": categoria,
            "stability_label": stab,
            "bot_risk_level": bot_risk_level,
            "confianca_classificacao": result.confianca,
            "score_organico": result.score_organico,
            "score_comercial": result.score_comercial,
            "score_apropriacao": result.score_apropriacao,
            "evidencias_principais": result.evidencias[:3],
            "flags_atencao": result.flags[:5] if result.flags else [],
        }

    @staticmethod
    def get_stability_matrix_full() -> List[Dict[str, str]]:
        """Return the full 5×5 matrix as a list of dicts for API/dashboard."""
        natures = ["ORGÂNICO", "RESONÂNCIA", "COMERCIAL", "SIMULAÇÃO", "APROPRIAÇÃO"]
        stabilities = ["estável", "emergindo", "fragmentando", "instável", "sem_dados"]
        badges = {
            "estável": "🟢", "emergindo": "🔵", "fragmentando": "🟡",
            "instável": "🔴", "sem_dados": "⚪",
        }
        classifier = SignalNatureClassifier()
        rows = []
        for nat in natures:
            for stab in stabilities:
                dummy_result = SignalNatureResult(
                    categoria=nat, confianca=0.8,
                    score_organico=50, score_comercial=50, score_apropriacao=0,
                    evidencias=[], flags=[], nuances_detectadas={},
                )
                rec = classifier.get_stability_recommendation(dummy_result, stab)
                rows.append({
                    "nature": nat,
                    "stability": stab,
                    "stability_badge": badges.get(stab, ""),
                    "prioridade": rec["prioridade"],
                    "mensagem": rec["mensagem"],
                    "acao": rec["acao"],
                })
        return rows
