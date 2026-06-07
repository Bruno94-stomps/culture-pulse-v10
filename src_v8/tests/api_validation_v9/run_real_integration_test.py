
import asyncio
import json
import httpx
from datetime import datetime

async def test_brand_analysis_integration():
    url = "http://localhost:8000/api/v8/analysis/brand"
    
    payload = {
        "brand_name": "Havaianas",
        "segment": "calçados",
        "location": "São Paulo - Capital",
        "demographics": {
            "faixa_etaria": "16-25",
            "classe_social": "B",
            "genero": "Todos",
            "escolaridade": "Ensino Superior",
            "renda_familiar": "R$ 5.000 - R$ 15.000"
        },
        "business_goal": "Aumentar o market share na região Nordeste focando em autenticidade."
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer cp_demo_2025_free_tier"
    }

    print(f"🚀 Enviando requisição para {url}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                print("✅ Sucesso! Status 200")
                result = response.json()
                
                # Validar a presença do campo regional_analysis
                if "regional_analysis" in result:
                    print(f"📍 Regional Analysis encontrada! (Tipo: {type(result['regional_analysis'])})")
                    print(json.dumps(result["regional_analysis"], indent=2, ensure_ascii=False))
                    
                    # Verificar se contém cvi_score
                    if isinstance(result["regional_analysis"], list) and len(result["regional_analysis"]) > 0:
                        first = result["regional_analysis"][0]
                        if "cvi_score" in first:
                            print(f"✨ Campo 'cvi_score' presente: {first['cvi_score']}")
                        else:
                            print("❌ Erro: 'cvi_score' ausente na predição regional.")
                else:
                    print("❌ Erro: Campo 'regional_analysis' não encontrado no JSON de resposta.")
                
            else:
                print(f"❌ Erro! Status {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Exceção ao conectar: {e}")

if __name__ == "__main__":
    asyncio.run(test_brand_analysis_integration())
