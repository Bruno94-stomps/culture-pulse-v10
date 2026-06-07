# GUIA DE DEPLOY E REDIRECIONAMENTO [ESTRATÉGICO V9.9]
Este guia detalha como conectar seu site principal (`futurama.cc`) ao sistema **CulturePulse V9.9**.

## 1. Arquitetura de Domínios (Recomendada)
Para maior segurança e performance, separe o Site do Sistema:
- **Site Institucional:** `https://futurama.cc` (Landing Page)
- **Dashboard Next.js:** `https://app.futurama.cc` (Hospedado no Cloudflare Pages)
- **API Backend Python:** `https://api.futurama.cc` (Hospedado no Railway ou em VPS/Docker)

---

## 2. Configurações de Redirecionamento (Landing Page)
No seu site principal, os botões devem seguir este padrão de links externos:

### Botão "Começar Grátis"
- **Link:** `https://app.futurama.cc/onboarding`
- **Objetivo:** Iniciar o fluxo de Briefing -> Scenario -> Dashboard.

### Botão "Login"
- **Link:** `https://app.futurama.cc/login`
- **Objetivo:** Acessar o sistema via Supabase Auth.

---

## 3. Configurações de Produção (Next.js)
No arquivo `.env.production` do Dashboard (`culturepulse-web`), você deve configurar:

```env
# URLs do sistema em produção
NEXT_PUBLIC_SITE_URL=https://app.futurama.cc
NEXT_PUBLIC_LANDING_PAGE=https://futurama.cc

# Endereço da API Backend (Sua VPS)
NEXT_PUBLIC_API_BRIDGE_URL=https://api.futurama.cc/api/v1

# Supabase (Atenção: Não use localhost!)
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[SUA-KEY-PUBLIC-DO-PAINEL]
```

---

## 4. Checklist no Supabase (Obrigatório)
Para o login funcionar fora do localhost:
1. Acesse o painel do **Supabase** -> **Authentication** -> **URL Configuration**.
2. No campo **Site URL**, coloque `https://app.futurama.cc`.
3. Em **Redirect URLs**, adicione `https://app.futurama.cc/**`.

---

## 5. Deploy do Backend (Docker/Nginx)
No seu servidor (VPS), você deve rodar o container e expô-lo via HTTPS com Nginx:

```bash
# No seu servidor
git clone [seu-repo]
cd culturepulse-v9
docker-compose up -d --build
```

### Configuração Nginx (Resumo):
```nginx
server {
    server_name api.futurama.cc;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 6. Próximos Passos
1. Conectar seu repositório ao Cloudflare Pages para o Frontend.
2. Implantar o Backend FastAPI no Railway ou usar uma VPS/Docker se preferir.
3. Configurar os registros DNS no painel do seu domínio (`futurama.cc`).
