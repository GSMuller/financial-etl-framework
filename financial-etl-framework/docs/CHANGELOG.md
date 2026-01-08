# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-01-08

### Lançamento Inicial

Primeira versão estável do Financial ETL Framework com arquitetura completa de Data Warehouse.

### Adicionado

#### Infraestrutura
- **Arquitetura em camadas** (Raw → Staging → Mart) seguindo padrão Medalhão
- **Conexão PostgreSQL** com gerenciamento seguro via context managers
- **Sistema de logging** centralizado para rastreamento de operações
- **Configuração via variáveis de ambiente** (.env) para segurança
- **Docker support** com multi-stage build otimizado
- **CI/CD Pipeline** com GitHub Actions (testes, linting, Docker)

#### Funcionalidades Core
- Módulo `conn.py` para gerenciamento de conexões PostgreSQL
- Módulo `config.py` para configuração e logging
- Script `rollback.py` para reversão de transações
- Suporte a context managers (`db_connection()`)
- Validação automática de credenciais obrigatórias

#### Schemas SQL
- **Schema BYD** completo com:
  - Tabelas de faturamento e cadastro
  - Views analíticas para controladoria
  - Triggers para cálculo automático de bonificações
  - Triggers para propagação de dados entre tabelas
  - Funções PL/pgSQL para regras de negócio
  
#### Testes
- Suite completa de testes com pytest
- Cobertura de código > 95%
- Testes de conexão, configuração e rollback
- Relatórios HTML de cobertura

#### Documentação
- README.md completo com:
  - Diagrama de arquitetura visual
  - Instruções de instalação detalhadas
  - Exemplos de uso práticos
  - Badges de status
- pyproject.toml com metadados do projeto
- .env.example com template de configuração
- Este CHANGELOG.md

#### Qualidade de Código
- Configuração Black para formatação
- Configuração isort para organização de imports
- Configuração flake8 para linting
- Configuração mypy para type checking

#### DevOps
- Dockerfile multi-stage otimizado
- GitHub Actions para CI/CD
- Healthcheck para containers
- Non-root user para segurança

### Estrutura do Projeto

```
financial-etl-framework/
├── src/financial_etl/      # Código fonte modular
├── tests/                  # Testes automatizados
├── schemas/                # SQL schemas e triggers
├── Datasets/               # Dados de exemplo
├── docs/                   # Documentação
├── .github/workflows/      # CI/CD
└── pyproject.toml          # Configuração moderna
```

### Tecnologias

- Python 3.9+
- PostgreSQL 13+
- psycopg2 para conexão DB
- SQLAlchemy para ORM
- pandas para manipulação de dados
- pytest para testes
- Docker para containerização
- GitHub Actions para CI/CD

### Métricas

- **Cobertura de Testes**: ~95%
- **Linhas de Código**: ~5,000+
- **Python**: 58.1%
- **SQL**: 5.7%
- **Notebooks**: 36.2%

---

## [Unreleased]

### Em Desenvolvimento

- Integração com BigQuery
- Pipeline automatizado de ETL diário
- API REST para consultas
- Dashboard web para monitoramento
- Alertas e notificações
- Documentação de APIs

### Planejado

- Suporte a múltiplos ambientes (dev, staging, prod)
- Versionamento de schemas com Alembic
- Testes de integração end-to-end
- Performance benchmarks
- Documentação técnica detalhada (Sphinx)
- Exemplos de notebooks Jupyter

---

## Tipos de Mudanças

- **Adicionado** - Para novas funcionalidades
- **Modificado** - Para mudanças em funcionalidades existentes
- **Depreciado** - Para funcionalidades que serão removidas
- **Removido** - Para funcionalidades removidas
- **Corrigido** - Para correção de bugs
- **Segurança** - Para correções de vulnerabilidades

---

## Referências

- [Semantic Versioning](https://semver.org/lang/pt-BR/)
- [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
- [Conventional Commits](https://www.conventionalcommits.org/pt-br/)
