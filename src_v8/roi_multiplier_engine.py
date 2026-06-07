import json
import os

def calculate_regional_roi(alpha_gain, base_revenue, state):
    """
    Calcula o ROI preditivo baseado no Cultural Alpha Regional.
    Alpha Gain: % de crescimento na tração cultural.
    Base Revenue: Receita atual do segmento no estado.
    """
    # Multiplicadores de Eficiência Regional (V10.2)
    # Estados com maior momentum cultural convertem Alpha em ROI mais rápido.
    regional_multipliers = {
        "SP": 1.4,  # Alta competitividade, conversão sólida
        "RJ": 1.2,  # Conversão via estética e viralização
        "BA": 1.8,  # Maior eficiência: baixo custo de mídia / alta ressonância cultural
        "MG": 1.1   # Conversão estável e duradoura
    }
    
    multiplier = regional_multipliers.get(state, 1.0)
    
    # Lógica de ROI: Alpha Gain (ex: 0.25) * Multiplicador * Base
    projected_additional_revenue = (alpha_gain * multiplier) * base_revenue
    roi_percentage = (projected_additional_revenue / (base_revenue * 0.15)) * 100 # Assumindo custo de marketing de 15% da base
    
    return {
        "state": state,
        "alpha_impact": alpha_gain,
        "multiplier": multiplier,
        "projected_revenue_gain": round(projected_additional_revenue, 2),
        "roi_estimate": f"{round(roi_percentage, 1)}%"
    }

if __name__ == "__main__":
    # Simulação para a Natura (Exemplo do Snapshot anterior)
    states = ["SP", "RJ", "BA", "MG"]
    base_rev = 1000000 # 1 Milhão por estado
    alpha = 0.25 # 25% de ganho simulado
    
    results = [calculate_regional_roi(alpha, base_rev, s) for s in states]
    
    print("--- 💸 ROI MULTIPLIER ENGINE V10.2 ---")
    for res in results:
        print(f"Estado: {res['state']} | Ganho Projetado: R${res['projected_revenue_gain']} | ROI: {res['roi_estimate']}")
    
    with open("data/learning/regional_roi_projection.json", "w") as f:
        json.dump(results, f, indent=4)
