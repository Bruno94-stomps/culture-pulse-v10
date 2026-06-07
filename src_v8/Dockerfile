# 🐳 CULTURE PULSE V9.0 - DOCKER CONFIGURATION
# Dockerfile otimizado para produção

FROM python:3.11-slim

# Metadados
LABEL maintainer="Culture Pulse Team"
LABEL version="9.0"
LABEL description="Culture Pulse V9.0 - Inteligência Cultural Brasileira"

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEPLOYMENT_PLATFORM=docker \
    PRODUCTION=true \
    CULTURE_PULSE_VERSION=9.0

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
    && chown -R user:user /home/user
USER user
WORKDIR /home/user/app

# Copiar requirements primeiro (para cache de layers)
COPY --chown=user:user requirements.txt .

# Instalar dependências Python
RUN pip install --user -r requirements.txt

# Copiar código da aplicação
COPY --chown=user:user . .

# Expor porta padrão do backend FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v8/health || exit 1

# Comando para iniciar a aplicação
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
