import asyncio
import aiohttp
import time
import json

BASE_URL = "http://localhost:8000"
TOKEN = "cp_executive_2025_premium"
ENDPOINT = f"{BASE_URL}/api/v8/intelligence/full"

CONCURRENT_REQUESTS = 10
TOTAL_REQUESTS = 30

payload = {
    "termo": "Inteligência Artificial no Brasil",
    "momentum": 85,
    "sentiment": 0.2,
    "volume": 1500,
    "plataforma": "linkedin"
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

async def fetch_intelligence(session, req_id):
    start = time.time()
    try:
        async with session.post(ENDPOINT, json=payload, headers=headers) as response:
            status = response.status
            data = await response.json()
            duration = time.time() - start
            print(f"Request {req_id:2d}: Status {status} | Time: {duration:.2f}s | Result: {'OK' if status == 200 else 'ERR'}")
            return status, duration
    except Exception as e:
        print(f"Request {req_id:2d}: Exception {str(e)}")
        return 500, time.time() - start

async def main():
    print(f"🚀 Iniciando Stress Test em {ENDPOINT}")
    print(f"Parâmetros: {CONCURRENT_REQUESTS} requests simultâneos, Total de {TOTAL_REQUESTS} requests.\n")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        full_start = time.time()
        
        # Estratégia de lotes para não sobrecarregar demais em um único loop local
        for i in range(TOTAL_REQUESTS):
            tasks.append(fetch_intelligence(session, i+1))
            
            # Executa em lotes de CONCURRENT_REQUESTS
            if len(tasks) >= CONCURRENT_REQUESTS:
                await asyncio.gather(*tasks)
                tasks = []
        
        if tasks:
            await asyncio.gather(*tasks)
            
    total_duration = time.time() - full_start
    print(f"\n📊 Resumo do Stress Test:")
    print(f"Tempo Total: {total_duration:.2f}s")
    print(f"Média por Lote: {total_duration / (TOTAL_REQUESTS / CONCURRENT_REQUESTS):.2f}s")
    print(f"Throughput: {TOTAL_REQUESTS / total_duration:.2f} req/s")

if __name__ == "__main__":
    asyncio.run(main())
