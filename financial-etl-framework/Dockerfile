# Dockerfile para Financial ETL Framework
# Multi-stage build para otimizar tamanho da imagem

# Stage 1: Build
FROM python:3.11-slim as builder

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml ./
COPY requirements.txt ./

# Criar diretório para wheels
RUN pip install --upgrade pip setuptools wheel

# Instalar dependências em um diretório separado
RUN pip install --user --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar usuário não-root
RUN useradd -m -u 1000 etluser && \
    mkdir -p /app /app/logs && \
    chown -R etluser:etluser /app

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências instaladas do builder
COPY --from=builder --chown=etluser:etluser /root/.local /home/etluser/.local

# Copiar código do projeto
COPY --chown=etluser:etluser . .

# Adicionar .local/bin ao PATH
ENV PATH=/home/etluser/.local/bin:$PATH

# Mudar para usuário não-root
USER etluser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from financial_etl import get_connection; get_connection()" || exit 1

# Comando padrão (pode ser sobrescrito)
CMD ["python", "-m", "financial_etl"]

# Labels para metadata
LABEL maintainer="Giovanni Muller <your.email@example.com>" \
      version="1.0.0" \
      description="Financial ETL Framework - PostgreSQL Data Warehouse" \
      org.opencontainers.image.source="https://github.com/GSMuller/financial-etl-framework"
