#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V9.9 — Local SLM Bridge (Llama-3-8B via Ollama)
==============================================
Ponte de comunicação entre os motores de inteligência e o modelo local rodando no Mac Mini.
Responsável por:
  - Geração de narrativas culturais reais (Substitui templates estáticos)
  - Interpretação de feedbacks de usuários para Active Learning
  - Refinamento de objetivos no onboarding via Chat Interativo

Arquitetura:
  [Intelligence Module] -> [SLM Bridge] -> [Ollama API (localhost:11434)]
"""

import json
import logging
import requests
import hashlib
import os
import time
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class LocalSLMBridge:
    """Interface para o modelo Llama-3-8B rodando localmente no Mac Mini."""
    
    # Prompt de Refinamento de Sinais Fracos (V9.9.1)
    # Foca na identificação de anomalias e comportamentos de nicho com potencial mainstream.
    WEAK_SIGNALS_REFINEMENT = """
    FOCO EM SINAIS FRACOS (WEAK SIGNALS):
    Sinais fracos são ruídos em nichos digitais que indicam mudanças iminentes.
    1. Identifique anomalias: procure padrões em subreddits, comentários e playlists de nicho.
    2. Ignore o óbvio: não foque no que já é tendência consolidada.
    3. Conecte o 'Sussurro' ao 'Grito': como esse pequeno sinal pode impactar o mainstream em 6-12 meses?
    4. Analise o Engajamento Qualitativo: se o volume é baixo mas o sentimento é intenso, é um sinal fraco crítico.
    """

    # V9.5 Strategic Prompt Templates
    STRATEGIC_BOARD_READY_TEMPLATE = """
    ESTRATÉGIA BOARD-READY (V9.5):
    Ao gerar o manifesto ou blueprint, utilize obrigatoriamente as seguintes camadas técnicas convertidas para valor de negócio:
    
    1. ADERÊNCIA ESTÉTICA (Visão Computacional): Mencione como os códigos visuais detectados coincidem ou divergem do território.
    2. FILTRO DE VERDADE (Transformers): Identifique se a linguagem da marca está sendo lida como autêntica ou se há risco de detecção de ironia/sarcasmo no cluster.
    3. NUANCE GEOCULTURAL (Sabiá-2): Explique o termo principal (ex: 'O Corre') sob a ótica antropológica brasileira, evitando definições genéricas.
    
    O tom deve ser Executivo, mas fundamentado em dados multimodais reais.
    """
    
    def __init__(self, model_name: str = "llama3:8b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_url = f"{host}/api/generate"
        self._is_available = self._check_connection()
        
        # Configuração de Cache Local (V9.9) para evitar sobrecarga no Mac Mini
        self.cache_dir = "/Users/brmunizmoura/Documents/PULSO/cache/slm_cache"
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
            except Exception:
                pass
        
        # Cache TTL: 24 horas para narrativas culturais (tendem a ser estáveis no curto prazo)
        self.cache_ttl = 86400 

    def _get_cache_path(self, prompt: str) -> str:
        """Gera um path de arquivo único baseado no hash do prompt."""
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{prompt_hash}.json")

    def _read_cache(self, prompt: str) -> Optional[str]:
        """Lê resposta do cache se disponível e ainda válida."""
        cache_path = self._get_cache_path(prompt)
        if os.path.exists(cache_path):
            try:
                # Verificar se o arquivo expirou
                file_age = time.time() - os.path.getmtime(cache_path)
                if file_age < self.cache_ttl:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data.get("response")
                else:
                    os.remove(cache_path) # Limpeza de cache expirado
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler cache SLM: {e}")
        return None

    def _write_cache(self, prompt: str, response: str):
        """Salva a resposta no cache local."""
        cache_path = self._get_cache_path(prompt)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": time.time(),
                    "model": self.model_name,
                    "response": response
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar cache SLM: {e}")

    def _check_connection(self) -> bool:
        """Verifica se o Ollama está online no Mac Mini."""
        try:
            # Tenta um ping rápido na raiz do Ollama
            host_root = self.api_url.replace("/api/generate", "")
            response = requests.get(f"{host_root}/api/tags", timeout=2)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if self.model_name in models or f"{self.model_name}:latest" in models:
                    logger.info(f"✅ Ollama detectado: Usando {self.model_name} para inteligência local.")
                    return True
                else:
                    # Tentar sem o sufixo :8b se falhar, ou aceitar qualquer llama3
                    if any("llama3" in m for m in models):
                        self.model_name = [m for m in models if "llama3" in m][0]
                        logger.info(f"✅ Ollama detectado: Usando {self.model_name} (Auto-detected).")
                        return True
            return False
        except Exception:
            logger.warning("⚠️ Ollama não detectado ou modelo ausente.")
        return False

    @property
    def is_available(self) -> bool:
        return self._is_available

    def generate_insight(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Envia um prompt para o Llama-3 e retorna a narrativa gerada."""
        if not self.is_available:
            return ""

        # Garantir que o prompt seja uma string (V9.9 Fix para BusinessSynthesizer)
        if isinstance(prompt, dict):
            # Se for dicionário, formatar como prompt de instrução estruturado em PT-BR
            prompt_str = f"""
            Analise estes dados culturais e gere um conselho estratégico curto para o negócio.
            IMPORTANTE: Responda obrigatoriamente em PORTUGUÊS (Brasil).
            
            DADOS DO SINAL:
            {json.dumps(prompt, indent=2, ensure_ascii=False)}
            """
        else:
            prompt_str = f"{prompt}\nResponda em PORTUGUÊS."

        system_instruction = system_prompt or "Você é um consultor especializado em cultura brasileira e estratégia de marca. Responda sempre em Português do Brasil."
        
        full_prompt = f"System: {system_instruction}\nUser: {prompt_str}"

        # 1. Verificar Cache Local (V9.9) - Reduzir carga no CPU/GPU do Mac Mini
        cached_response = self._read_cache(full_prompt)
        if cached_response:
            print(f"📦 Resposta SLM em cache detectada ({len(cached_response)} chars). Pulando Ollama.")
            return cached_response

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500
            }
        }

        try:
            print(f"🤖 Enviando prompt para Ollama ({self.model_name})...")
            response = requests.post(self.api_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                print(f"✅ Resposta recebida do Ollama ({len(result)} chars)")
                
                # 2. Salvar no Cache Local (V9.9)
                self._write_cache(full_prompt, result)
                return result
            else:
                print(f"❌ Erro HTTP do Ollama: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar insight via SLM Local: {e}")
            print(f"❌ Exceção na chamada ao Ollama: {e}")
        
        return ""

    def synthesize_narrative(self, signal_data: Dict[str, Any], business_context: Dict[str, Any]) -> str:
        """Gera uma narrativa conectando o sinal cultural ao objetivo do negócio com foco em sinais fracos."""
        
        prompt = f"""
        {self.WEAK_SIGNALS_REFINEMENT}

        Analise este SINAL CULTURAL para o contexto de NEGÓCIO fornecido.
        
        SINAL: {signal_data.get('termo', 'Desconhecido')}
        DESCRIÇÃO: {signal_data.get('texto', 'Sem descrição disponível')}
        STATUS: {signal_data.get('stability_context', {}).get('status', 'sem_dados')}
        CIRCLE: {signal_data.get('circulo', 'Cultura Geral')}
        
        CONTÉXTO DE NEGÓCIO: {business_context.get('business_objective', 'Melhorar presença')}
        PÚBLICO-ALVO: {business_context.get('target_audience', 'Brasil')}
        
        TAREFA: Escreva UM parágrafo (máx 350 caracteres) explicando por que este sinal é uma oportunidade real de antecipação estratégica.
        1. Aplique a metodologia "ALMA DO BRASILEIRO": Conecte o sinal às raízes comportamentais e identitárias do Brasil.
        2. Adapte o tom ao DESAFIO específico transcrito pelo usuário no Onboarding.
        3. FOCO EM SINAIS FRACOS: Explique a capacidade disruptiva antes de virar mainstream.

        REGRAS CRÍTICAS: 
        - Responda OBRIGATORIAMENTE em PORTUGUÊS (PT-BR).
        - NÃO use frases genéricas ou clichês de IA.
        - SEJA DIRETO, visceral e estratégico.
        """
        
        system_prompt = "Você é o BusinessSynthesizer V9.9, um expert em sinais culturais e estratégia de antecipação de tendências no mercado brasileiro."
        
        return self.generate_insight(prompt, system_prompt)

    def generate_strategic_advice(self, auth: Any, threshold: Dict, semantic: Dict, narrative: Dict = None) -> str:
        """
        Gera uma recomendação estratégica estruturada em PT-BR.
        
        Args:
            auth: Objeto de autenticidade (pode ser None)
            threshold: Dicionário com scores de relevância
            semantic: Contexto semântico do sinal
            narrative: Narrativa cultural já gerada
            
        Returns:
            str: Conselho estratégico gerado pelo Llama-3
        """
        cultural_context = narrative.get('cultural', '') if narrative else ""
        signal_text = semantic.get('text', '')
        score = threshold.get('score', 0)

        prompt = f"""
        Como um consultor de negócios especialista em cultura brasileira:
        
        CONTEXTO CULTURAL: {cultural_context}
        SINAL BRUTO: {signal_text}
        RELEVÂNCIA: {score}

        Forneça uma recomendação estratégica de negócio dividida em:
        1. O QUE FAZER: Ação imediata.
        2. POR QUE FAZER: Valor cultural agregado.
        3. MÉTRICA DE SUCESSO: Como medir.

        RESPONDA EM PORTUGUÊS (PT-BR). SEJA DIRETO E ESTRATÉGICO.
        """
        
        system_prompt = "Você é um Business Strategist sênior especializado em mercado brasileiro."
        
        return self.generate_insight(prompt, system_prompt)

# Singleton para uso em todo o projeto
_bridge = None
def get_slm_bridge():
    global _bridge
    if _bridge is None:
        _bridge = LocalSLMBridge()
    return _bridge
