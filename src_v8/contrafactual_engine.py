
import time

def run_contrafactual_simulation(scenario_name, current_alpha=0.15, current_dissonance=0.10):
    """
    Simula um cenário contrafactual (O que acontece se...?) 
    baseado no Framework V9.5 (Mirroring vs. Proposta).
    """
    print(f"🕵️‍♂️ INICIANDO MOTOR CONTRAFACTUAL (V9.5)")
    print(f"📉 Cenário: {scenario_name}")
    print(f"📊 Baseline: Alpha {current_alpha:.2f} | Dissonância {current_dissonance:.2f}")
    print("-" * 50)

    time.sleep(1)
    
    scenarios = {
        "ATAQUE_CONCORRENTE": {
            "description": "Principal concorrente lança campanha 'Realismo Visceral' com investimento massivo.",
            "alpha_impact": -0.04,  # Perda de exclusividade no sinal
            "dissonance_impact": +0.08, # Confusão de categoria
            "verdict": "RISCO DE COMODITIZAÇÃO DO 'CORRE'",
            "counter_action": "Migrar para o sub-sinal 'Hackerismo Técnico' (Ganbiarra) onde o concorrente não tem permissão de marca."
        },
        "CHOQUE_ECONOMICO_NEGATIVO": {
            "description": "Inflação de alimentos sobe 15%, reduzindo poder de compra do cluster Y.",
            "alpha_impact": +0.06,  # O 'Corre' se torna a única saída (Hiper-tração)
            "dissonance_impact": -0.02, # Marca que ajuda no 'corre' ganha autenticidade extrema
            "verdict": "OPORTUNIDADE DE RESILIÊNCIA",
            "counter_action": "Lançar embalagens 'Refil Econômico' focadas na continuidade do micro-empreendedor."
        },
        "REJEIÇÃO_ESTÉTICA_GERAL": {
            "description": "Trend de 'Quiet Luxury' (asséptico) volta ao mainstream, gerando cansaço da estética de rua.",
            "alpha_impact": -0.07,
            "dissonance_impact": +0.15,
            "verdict": "PIVOTAMENTO NECESSÁRIO",
            "counter_action": "Refinar o visual para o 'Corre Premium' (Nostalgia 90s organizada)."
        }
    }

    result = scenarios.get(scenario_name, {
        "description": "Cenário desconhecido.",
        "alpha_impact": 0.0,
        "dissonance_impact": 0.0,
        "verdict": "N/A",
        "counter_action": "Monitorar."
    })

    new_alpha = current_alpha + result["alpha_impact"]
    new_dissonance = current_dissonance + result["dissonance_impact"]

    print(f"🔍 ANÁLISE PEST-CULTURAL:")
    print(f"📝 {result['description']}")
    print(f"⚠️ Veredito: {result['verdict']}")
    print(f"🚀 Sugestão Estratégica: {result['counter_action']}")
    print("-" * 50)
    print(f"📈 PROJEÇÃO PÓS-CENÁRIO:")
    print(f"💎 Novo Alpha: {new_alpha:.2f} (Delta {result['alpha_impact']})")
    print(f"⚡ Nova Dissonância: {new_dissonance:.2f} (Delta {result['dissonance_impact']})")
    
    return {"alpha": new_alpha, "dissonance": new_dissonance, "action": result["counter_action"]}

if __name__ == "__main__":
    # Simula o ataque do concorrente que tenta imitar a nossa "Narrativa de Conquista"
    run_contrafactual_simulation("ATAQUE_CONCORRENTE")
    print("\n\n")
    # Simula o efeito de uma crise econômica na tração do 'Corre'
    run_contrafactual_simulation("CHOQUE_ECONOMICO_NEGATIVO")
