# Configuração de Subdomínios (DNS) para Futurama.cc

Para que `https://app.futurama.cc/signup` e `https://app.futurama.cc/login` funcionem, você precisa configurar os registros DNS no painel onde você comprou o domínio `futurama.cc` (por exemplo: GoDaddy, Namecheap, Cloudflare ou Registro.br).

## 1. Mapeamento de DNS (Passo-a-passo)

Vá até a zona de DNS do seu domínio e adicione os seguintes registros:

| Tipo  | Nome (Host) | Valor (Alvo) | Objetivo |
| :--- | :--- | :--- | :--- |
| **CNAME** | `app` | `<valor Cloudflare Pages fornecido>` | Aponta o dashboard Next.js para o Cloudflare Pages |
| **A** | `api` | `[IP-DA-SUA-VPS]` | Aponta o backend Python (Docker) para o seu servidor |

> **Nota:** Se você usar o Cloudflare Pages, eles te darão o valor exato do CNAME após você adicionar o domínio `app.futurama.cc` nas configurações do projeto.

---

## 1. Passo a Passo no Hostinger (DNS)

Para conectar seu sistema ao domínio `futurama.cc` hospedado na **Hostinger**:

1. Acesse o **hPanel** da Hostinger.
2. Vá em **Domínios** -> selecione `futurama.cc`.
3. No menu lateral, clique em **DNS / Nameservers**.
4. Procure a seção **Gerenciar registros DNS** e adicione:

| Tipo | Nome (Host) | Valor (Alvo) | TTL |
| :--- | :--- | :--- | :--- |
| **CNAME** | `app` | `<valor Cloudflare Pages fornecido>` | 14400 |
| **A** | `api` | `[IP-DA-SUA-VPS]` | 14400 |

*   **Nota:** Se você for usar o Cloudflare Pages para o frontend, o valor será fornecido pela plataforma após adicionar o domínio.
*   **Nota:** O registro `api` só deve ser criado quando você tiver o IP do servidor onde o Python (Docker) vai rodar.

---

## 2. Configuração no Cloudflare Pages (Frontend)

1. Acesse o painel do seu projeto no **Cloudflare Pages**.
2. Vá em **Settings** -> **Custom domains**.
3. Clique em **Add custom domain** e digite `app.futurama.cc`.
4. O Cloudflare gerará o certificado SSL (HTTPS) automaticamente.

---

## 3. As rotas internas já existem!

Você não precisa "criar" as páginas de login e signup no código, pois eu verifiquei que elas já estão na estrutura do seu projeto:

- **Login:** Está em `culturepulse-web/app/(auth)/login/page.tsx`
  - URL Resultante: `app.futurama.cc/login`
- **Signup:** Está em `culturepulse-web/app/signup/page.tsx`
  - URL Resultante: `app.futurama.cc/signup`

---

## 4. Atualização de Segurança (Supabase)

**IMPORTANTE:** Para que o Login funcione no novo domínio, você deve autorizá-lo no Supabase:

1. Acesse [app.supabase.com](https://app.supabase.com).
2. Vá em **Authentication** -> **URL Configuration**.
3. Em **Site URL**, altere para `https://app.futurama.cc`.
4. Em **Redirect URLs**, adicione `https://app.futurama.cc/**`.

---

## Próximo Passo
Depois que os links estiverem funcionando, eu posso te ajudar a configurar as **Variáveis de Ambiente** no Cloudflare Pages para que o sistema pare de tentar conectar no `localhost` e use o banco de dados oficial!
