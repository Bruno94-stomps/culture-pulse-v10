"""
Graph Neural Networks para análise de propagação cultural
Baseado na pesquisa de Stanford (2024) sobre redes de simulação social
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv
from torch_geometric.data import Data, Batch
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CulturalPropagation:
    """Resultado da análise de propagação cultural"""
    influence_scores: Dict[str, float]
    community_structure: List[List[str]]
    central_nodes: List[str]
    propagation_paths: List[Tuple[str, str, float]]
    
@dataclass
class AgentBehavior:
    """Comportamento de um agente cultural"""
    agent_id: str
    cultural_vector: np.ndarray
    influence_radius: float
    adaptability: float
    social_connections: List[str]

class CulturalGNN(nn.Module):
    """Modelo GNN para análise de propagação cultural"""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super(CulturalGNN, self).__init__()
        
        # Camadas de convolução do grafo
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GATConv(hidden_dim, output_dim, heads=4, concat=False)
        
        # Camadas lineares para processamento final
        self.linear1 = nn.Linear(output_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x, edge_index, batch=None):
        # Aplicar convoluções do grafo
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.2, training=self.training)
        
        x = F.relu(self.conv2(x, edge_index))
        x = F.dropout(x, p=0.2, training=self.training)
        
        x = self.conv3(x, edge_index)
        
        # Processamento final
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        
        return x

class CulturalGraphAnalyzer:
    """Analisador de grafos culturais usando GNN"""
    
    def __init__(self, input_dim: int = 64):
        """Inicializar analisador com dimensões do modelo"""
        self.input_dim = input_dim
        self.hidden_dim = 128
        self.output_dim = 32
        
        # Inicializar modelo GNN
        self.model = CulturalGNN(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            output_dim=self.output_dim
        )
        
        # Criar grafo de propagação cultural
        self.cultural_graph = nx.Graph()
        
        # Sistema multi-agente
        self.agents = {}
        
    def add_cultural_node(self, node_id: str, features: np.ndarray, 
                         connections: List[Tuple[str, float]] = None):
        """Adicionar nó cultural ao grafo"""
        self.cultural_graph.add_node(node_id, features=features)
        
        if connections:
            for target, weight in connections:
                self.cultural_graph.add_edge(node_id, target, weight=weight)
                
    def add_cultural_agent(self, agent_id: str, cultural_vector: np.ndarray,
                          influence_radius: float = 0.5,
                          adaptability: float = 0.3,
                          connections: List[str] = None):
        """Adicionar agente cultural ao sistema"""
        agent = AgentBehavior(
            agent_id=agent_id,
            cultural_vector=cultural_vector,
            influence_radius=influence_radius,
            adaptability=adaptability,
            social_connections=connections or []
        )
        
        self.agents[agent_id] = agent
        
    def analyze_cultural_propagation(self, initial_state: Dict[str, float],
                                   steps: int = 10) -> CulturalPropagation:
        """Analisar propagação cultural no grafo"""
        try:
            if len(self.cultural_graph.nodes) < 2 or len(self.cultural_graph.edges) < 1:
                logger.warning("Grafo muito pequeno para análise de propagação")
                return None

            # Mapear nomes de nós para índices inteiros (PyG exige int)
            node_list = list(self.cultural_graph.nodes())
            node_to_idx = {node: i for i, node in enumerate(node_list)}

            # Converter edges para tensor de índices inteiros
            edges_idx = [
                (node_to_idx[u], node_to_idx[v])
                for u, v in self.cultural_graph.edges()
            ]
            # PyG edge_index: shape [2, num_edges], bidirecional
            src = [e[0] for e in edges_idx] + [e[1] for e in edges_idx]
            dst = [e[1] for e in edges_idx] + [e[0] for e in edges_idx]
            edge_index = torch.tensor([src, dst], dtype=torch.long)

            # Feature matrix: [num_nodes, input_dim]
            features_np = np.array([
                self.cultural_graph.nodes[node]['features']
                for node in node_list
            ], dtype=np.float32)
            x = torch.from_numpy(features_np)

            # Forward pass (3 camadas GNN internas já propagam informação)
            # Não fazer loop — o modelo tem 3 convoluções que fazem a propagação
            self.model.eval()
            with torch.no_grad():
                x_out = self.model(x, edge_index)
                    
            # Analisar resultados
            influence_scores = {}
            for i, node in enumerate(node_list):
                influence_scores[node] = float(torch.mean(x_out[i]))
                
            # Detectar comunidades
            communities = list(nx.community.greedy_modularity_communities(
                self.cultural_graph))
            community_structure = [
                [str(node) for node in comm] for comm in communities
            ]
            
            # Identificar nós centrais
            central_nodes = [
                node for node, cent in nx.eigenvector_centrality(
                    self.cultural_graph).items()
                if cent > 0.5
            ]
            
            # Calcular caminhos de propagação
            propagation_paths = []
            for source in central_nodes:
                for target in self.cultural_graph.nodes():
                    if source != target:
                        try:
                            path = nx.shortest_path(
                                self.cultural_graph, source, target, 
                                weight='weight'
                            )
                            if len(path) > 1:
                                propagation_paths.append(
                                    (source, target, 1.0/len(path))
                                )
                        except nx.NetworkXNoPath:
                            continue
                            
            return CulturalPropagation(
                influence_scores=influence_scores,
                community_structure=community_structure,
                central_nodes=central_nodes,
                propagation_paths=propagation_paths
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de propagação: {e}")
            return None
            
    def simulate_agent_behavior(self, timesteps: int = 10) -> List[Dict[str, np.ndarray]]:
        """Simular comportamento dos agentes culturais"""
        simulation_history = []
        
        try:
            for _ in range(timesteps):
                current_state = {}
                
                # Atualizar cada agente
                for agent_id, agent in self.agents.items():
                    # Calcular influência dos vizinhos
                    neighbor_influence = np.zeros_like(agent.cultural_vector)
                    neighbor_count = 0
                    
                    for neighbor_id in agent.social_connections:
                        if neighbor_id in self.agents:
                            neighbor = self.agents[neighbor_id]
                            distance = np.linalg.norm(
                                agent.cultural_vector - neighbor.cultural_vector
                            )
                            
                            if distance < agent.influence_radius:
                                neighbor_influence += neighbor.cultural_vector
                                neighbor_count += 1
                                
                    # Atualizar vetor cultural
                    if neighbor_count > 0:
                        average_influence = neighbor_influence / neighbor_count
                        agent.cultural_vector = (
                            (1 - agent.adaptability) * agent.cultural_vector +
                            agent.adaptability * average_influence
                        )
                        
                    current_state[agent_id] = agent.cultural_vector
                    
                simulation_history.append(current_state)
                
            return simulation_history
            
        except Exception as e:
            logger.error(f"Erro na simulação de agentes: {e}")
            return []
            
    def get_propagation_metrics(self) -> Dict[str, float]:
        """Calcular métricas de propagação cultural"""
        try:
            return {
                'density': nx.density(self.cultural_graph),
                'clustering': nx.average_clustering(self.cultural_graph),
                'diameter': nx.diameter(self.cultural_graph),
                'avg_path_length': nx.average_shortest_path_length(
                    self.cultural_graph
                )
            }
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {e}")
            return {}