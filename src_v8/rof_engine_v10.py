import json
import math

def calculate_rof(alpha_slope, cultural_noise, state, tension_index):
    """
    Calcula o ROF (Return on Future) baseado na Teoria de Opções Reais.
    Em vez de ROI (passado/presente), medimos o valor da 'opção cultural' criada.
    
    Alpha Slope: Velocidade da transição cultural.
    Cultural Noise: Volatilidade/Incerteza do sinal.
    Tension Index: Nível de fricção tribal (Collision).
    """
    
    # 1. Cultural Option Value (Black-Scholes simplificado para cultura)
    # Se o Alpha Slope > Noise, a opção está "In the Money"
    option_value = (alpha_slope * (1 - cultural_noise)) * (1 + (tension_index * 0.5))
    
    # 2. Brand Elasticity (V10.2)
    # A capacidade da marca de esticar seu equity sem quebrar a autenticidade regional
    regional_elasticities = {
        "SP": 0.65, # Mercado saturado, elasticidade moderada
        "RJ": 0.85, # Alta elasticidade via 'estética do fluxo'
        "BA": 0.95, # Máxima elasticidade: a cultura absorve e ressignifica a marca
        "MG": 0.55  # Baixa elasticidade: resistência a mudanças rápidas
    }
    elasticity = regional_multipliers = regional_elasticities.get(state, 0.5)
    
    # 3. ROF Score (0-100)
    # Mede o 'Equity de Antecipação'
    rof_score = (option_value * elasticity) * 100
    
    # Narrativas de ROF
    if rof_score > 75:
        verdict = "Dominância Fugaz (Alta Recompensa, Requer Agilidade)"
    elif rof_score > 50:
        verdict = "Resiliência Cultural (Equity Seguro)"
    else:
        verdict = "Risco de Irrelevância (Descompasso com o Futuro)"

    return {
        "state": state,
        "rof_score": round(rof_score, 1),
        "brand_elasticity": f"{int(elasticity*100)}%",
        "option_value": round(option_value, 2),
        "verdict": verdict,
        "indicator": "ROF (Return on Future) v10.2"
    }

if __name__ == "__main__":
    # Simulação V10.2: O Valor do Futuro em cada estado
    scenarios = [
        {"state": "SP", "slope": 0.12, "noise": 0.05, "tension": 0.8}, # Colisão GenZ+Uber
        {"state": "RJ", "slope": 0.09, "noise": 0.15, "tension": 0.7}, # Trap+Luxo
        {"state": "BA", "slope": 0.18, "noise": 0.02, "tension": 0.9}, # Ancestral+Tech
        {"state": "MG", "slope": 0.05, "noise": 0.45, "tension": 0.4}  # Agritech+Sabor
    ]
    
    print("--- 🧠 ROF ENGINE (RETURN ON FUTURE) V10.2 ---")
    results = []
    for s in scenarios:
        res = calculate_rof(s["slope"], s["noise"], s["state"], s["tension"])
        results.append(res)
        print(f"Estado: {res['state']} | ROF: {res['rof_score']} | Elasticidade: {res['brand_elasticity']} | {res['verdict']}")

    with open("data/learning/rof_projections_v10.json", "w") as f:
        json.dump(results, f, indent=4)
