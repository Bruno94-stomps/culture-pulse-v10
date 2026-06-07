import http.client, json
conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=20)
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer cp_demo_2025_free_tier'}
body = json.dumps({
    'project_id': 'test-proj',
    'brand_name': 'Teste de Marca',
    'segment': 'moda',
    'location': 'São Paulo - Capital',
    'demographics': {'faixa_etaria': '16-25', 'classe_social': 'B', 'genero': 'Todos', 'escolaridade': 'não especificado', 'renda_familiar': 'média'},
    'keywords': ['São Paulo', 'moda'],
    'regions': ['São Paulo'],
    'audiences': ['jovens'],
    'circles': ['moda', 'tecnologia'],
    'period_days': 30,
    'business_goal': 'Teste',
    'context_text': 'Teste de contexto',
    'outlier_mode': False,
})
conn.request('POST', '/api/v8/analysis/brand', body, headers)
res = conn.getresponse()
print('status', res.status)
print(res.read().decode('utf-8'))
