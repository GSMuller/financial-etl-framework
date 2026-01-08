# Financial ETL Framework

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)]()

> Framework ETL robusto para Data Warehouse financeiro com PostgreSQL, focado em controladoria e análise de dados operacionais.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Características](#-características)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Contribuindo](#-contribuindo)

---

## 🎯 Sobre o Projeto

O **Financial ETL Framework** é uma solução completa para consolidação de dados financeiros e operacionais em um Data Warehouse PostgreSQL. Desenvolvido para suportar processos de controladoria, o framework integra dados de múltiplas fontes (BigQuery, planilhas, sistemas internos) aplicando transformações, validações e regras de negócio.

### Problema Resolvido

Centralizar e padronizar dados financeiros fragmentados em diferentes sistemas, garantindo:
- ✅ Integridade e rastreabilidade dos dados
- ✅ Automação de ingestões diárias
- ✅ Aplicação consistente de regras de negócio
- ✅ Suporte a relatórios e análises gerenciais

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      FONTES DE DADOS                         │
├─────────────────┬──────────────────┬────────────────────────┤
│   BigQuery      │  AppSheet/       │   Sistemas             │
│   (Operacional) │  Google Sheets   │   Internos             │
└────────┬────────┴────────┬─────────┴───────────┬────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAW LAYER (Bronze)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  raw_bq      │  │raw_cadastro  │  │  raw_manual  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ ETL Pipeline
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   STAGING LAYER (Silver)                     │
│        Limpeza • Normalização • Padronização                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  stg_faturamento  │  stg_cadastro  │  stg_bonus     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ Business Rules
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   MART LAYER (Gold)                          │
│           Views Analíticas • Agregações • KPIs               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  mart_controladoria  │  mart_incentivos  │  metrics │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  BI Dashboards  │
                    │    Relatórios   │
                    └─────────────────┘
```

### Pipeline de Dados

1. **Extração**: Coleta de dados de BigQuery, planilhas e sistemas
2. **Carga (Raw)**: Armazenamento bruto sem transformações
3. **Staging**: Limpeza, validação e normalização
4. **Transformação**: Aplicação de regras de negócio (triggers, funções)
5. **Mart**: Camada analítica otimizada para consumo

---

## ✨ Características

### Core Features
- 🔄 **ETL Automatizado**: Pipeline completo de Extract-Transform-Load
- 🗃️ **Arquitetura em Camadas**: Raw → Staging → Mart (Medalhão)
- 🔐 **Segurança**: Credenciais via variáveis de ambiente (.env)
- 📊 **Integração BigQuery**: Ingestão diária de dados operacionais
- 🧪 **Testes Automatizados**: Cobertura com pytest
- 📝 **Logging Completo**: Rastreamento de todas as operações

### Funcionalidades Específicas
- 💰 Cálculo automático de bonificações BYD
- 🔄 Sistema de triggers para propagação de dados
- 📈 Views materializadas para performance
- 🎯 Validação de integridade referencial
- 📅 Controle de versionamento de dados

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL 13 ou superior
- Git

### Passos

1. **Clone o repositório**
```bash
git clone https://github.com/GSMuller/financial-etl-framework.git
cd financial-etl-framework
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
# Instalação básica
pip install -e .

# Com ferramentas de desenvolvimento
pip install -e ".[dev]"

# Com suporte a notebooks
pip install -e ".[notebooks]"

# Instalação completa
pip install -e ".[dev,notebooks,excel]"
```

4. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_dw
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# BigQuery (opcional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
BQ_PROJECT_ID=seu-projeto
BQ_DATASET=seu_dataset
```

5. **Execute as migrações do banco de dados**
```bash
# Criar schemas
psql -h localhost -U seu_usuario -d financial_dw -f schemas/byd/tables/create/create_all.sql

# Criar triggers
psql -h localhost -U seu_usuario -d financial_dw -f schemas/byd/triggers/install_triggers.sql
```

---

## 💻 Uso

### Exemplo Básico

```python
from financial_etl import get_connection, db_connection

# Usando context manager (recomendado)
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mart_controladoria.bonus_summary")
    results = cursor.fetchall()
    
    for row in results:
        print(row)
```

### Executar ETL Completo

```python
from financial_etl.pipelines import run_daily_etl

# Executa o pipeline completo
result = run_daily_etl(date='2026-01-08')
print(f"Pipeline executado: {result['status']}")
print(f"Registros processados: {result['records_processed']}")
```

### Rollback de Transações

```bash
python src/financial_etl/rollback.py
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com relatório de cobertura
pytest --cov=financial_etl --cov-report=html

# Teste específico
pytest tests/test_conn.py -v
```

---

## 📁 Estrutura do Projeto

```
financial-etl-framework/
├── src/
│   └── financial_etl/          # Código fonte principal
│       ├── __init__.py
│       ├── config.py           # Configurações e logging
│       ├── conn.py             # Gerenciamento de conexões
│       └── rollback.py         # Utilitário de rollback
├── tests/                      # Testes automatizados
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_conn.py
│   └── test_rollback.py
├── schemas/                    # Schemas SQL
│   ├── byd/
│   │   ├── tables/
│   │   │   ├── create/        # Scripts de criação
│   │   │   ├── alter/         # Alterações de schema
│   │   │   ├── insert/        # Scripts de inserção
│   │   │   └── view&conults/  # Views e consultas
│   │   └── triggers/          # Triggers e funções PL/pgSQL
│   └── nd/
├── Datasets/                   # Dados de exemplo (não versionados)
├── controlling_postgreSQL/     # Scripts legados
├── docs/                       # Documentação adicional
├── .github/
│   └── workflows/              # CI/CD GitHub Actions
├── .gitignore
├── pyproject.toml              # Configuração do projeto
├── requirements.txt            # Dependências (legado)
├── pytest.ini                  # Configuração pytest
├── Dockerfile                  # Container Docker
├── .env.example                # Exemplo de variáveis de ambiente
├── CHANGELOG.md                # Histórico de mudanças
└── README.md                   # Este arquivo
```

---

## 🧪 Testes

O projeto utiliza **pytest** com cobertura de código:

```bash
# Executar todos os testes
pytest

# Com output verboso
pytest -v

# Gerar relatório de cobertura HTML
pytest --cov=financial_etl --cov-report=html

# Abrir relatório no navegador
# O arquivo estará em htmlcov/index.html
```

### Cobertura Atual

- `config.py`: 95%
- `conn.py`: 98%
- `rollback.py`: 92%

---

## 🐳 Docker

### Build da Imagem

```bash
docker build -t financial-etl-framework .
```

### Executar Container

```bash
docker run -d \
  --name financial-etl \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=financial_dw \
  -e DB_USER=usuario \
  -e DB_PASSWORD=senha \
  financial-etl-framework
```

---

## 📊 Métricas do Projeto

- **Linguagem**: Python 58.1%
- **SQL**: 5.7%
- **Jupyter Notebooks**: 36.2%
- **Cobertura de Testes**: ~95%
- **Linhas de Código**: ~5,000+

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Code Style

O projeto utiliza:
- **black** para formatação de código
- **isort** para organização de imports
- **flake8** para linting
- **mypy** para type checking

```bash
# Formatar código
black src/ tests/

# Organizar imports
isort src/ tests/

# Verificar qualidade
flake8 src/ tests/
```

---

## 📄 Licença

Projeto privado - Todos os direitos reservados.

---

## 👤 Autor

**Giovanni Muller**

- GitHub: [@GSMuller](https://github.com/GSMuller)
- LinkedIn: [Giovanni Muller](https://www.linkedin.com/in/giovanni-muller)

---

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões.

---

## 🙏 Agradecimentos

- Equipe de Controladoria Servopa
- Comunidade PostgreSQL
- Contribuidores open-source

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
