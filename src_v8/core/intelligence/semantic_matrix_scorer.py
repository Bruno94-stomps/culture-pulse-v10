import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import Dict, List, Optional
import os

class SemanticMatrixScorer:
    """
    Core Intelligence Layer for dynamic signal-context similarity.
    Implements Gutsche (2018) 'P75 Adaptive Threshold' for Weak Signal detection.
    """
    
    def __init__(self, model_name: str = "neuralmind/bert-base-portuguese-cased"):
        self.device = torch.device("cpu") # Optimized for currently installed torch+cpu
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.p75_threshold = 0.454 # Gutsche (2018) calibrated threshold for BERTimbau
        self._initial_load = False

    def _lazy_load(self):
        """Load model only when needed to save memory."""
        if not self._initial_load:
            # Note: In a production server, this should point to a local path (cache/ml_models/)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device).eval()
            self._initial_load = True

    def get_embedding(self, text: str) -> torch.Tensor:
        self._lazy_load()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling of the last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding

    def calculate_similarity(self, term1: str, term2: str) -> float:
        """Calculates cosine similarity between two terms."""
        emb1 = self.get_embedding(term1)
        emb2 = self.get_embedding(term2)
        
        cos = torch.nn.CosineSimilarity(dim=1)
        similarity = cos(emb1, emb2).item()
        return float(similarity)

    def get_discovery_multiplier(self, context_theme: str, signal_name: str, user_intent: str = "default") -> float:
        """
        Determines the intensity of a Weak Signal vs Noise based on semantic distance.
        V10.1: Adicionado filtro de "Identidade Dinâmica" baseado na intenção do Usuário (Onboarding).
        
        Logic:
        - Similarity > 0.8: Cliché/Noise (Multiplier 0.5)
        - Similarity < 0.454 (P75): Authentic Weak Signal/Outlier (Multiplier 1.5)
        - Transition Zone: Normalized linear scale.
        - User Intent: If user seeks "inovação", signals with LOW similarity to the "traditional"
          segment get an extra boost (Dynamic Relevance Filter).
        """
        try:
            sim = self.calculate_similarity(context_theme, signal_name)
            
            # Base Multiplier Calculation
            if sim > 0.8:
                multiplier = 0.5
            elif sim < self.p75_threshold:
                multiplier = 1.5
            else:
                # Linear map from [0.454, 0.8] to [1.5, 0.5]
                multiplier = 1.5 - (sim - self.p75_threshold) * (1.0 / (0.8 - self.p75_threshold))
                multiplier = max(0.6, min(1.4, multiplier))

            # 🚀 DINAMIC IDENTITY FILTER (Innovation Boost)
            # Se o usuário quer inovação, valorizamos sinais distantes (baixa sim)
            if user_intent.lower() in ["inovação", "innovation", "tendências", "ruptura"]:
                if sim < 0.6: # Sinais que já são moderadamente distantes
                    # Bônus proporcional: quanto mais longe, maior o bônus de inovação
                    innovation_bonus = (0.6 - sim) * 0.5 
                    multiplier += innovation_bonus
            
            return round(multiplier, 3)
            
        except Exception as e:
            print(f"Error calculating dynamic similarity: {e}")
            return 1.0

# Singleton instance for the system
dynamic_scorer = SemanticMatrixScorer()
