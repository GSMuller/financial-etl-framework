# Servopa Data Warehouse — Controladoria  

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-documented-brightgreen.svg)]()

Migração, padronização e consolidação de dados operacionais e administrativos  
**PostgreSQL • BigQuery • ETL • Python • RDBMS**

---

Este repositório contém a arquitetura, scripts e pipelines utilizados na criação do
Data Warehouse da Controladoria Servopa. O objetivo é integrar as fontes de dados
operacionais (BigQuery) e administrativas (cadastros manuais), consolidando tudo em
um ambiente PostgreSQL padronizado e confiável para suporte ao processo financeiro
e análise de incentivos.

---

## Objetivos do Projeto

- Centralizar dados operacionais e administrativos em um único servidor PostgreSQL.  
- Garantir integridade, versionamento e rastreabilidade no fluxo de dados.  
- Automatizar ingestões diárias do BigQuery e dos cadastros manuais.  
- Aplicar regras de negócio (ex.: bonificação BYD, status de faturamento).  
- Criar camadas estruturadas (RAW → STG → MART) para simplificar consumo da Controladoria.  
- Suportar relatórios, fechamentos mensais e indicadores internos!

---

## Arquitetura de Dados

```text
BigQuery (faturamento diário)
        │
        ▼
RAW_BQ (tabelas espelho brutas)
        │
        ├── Cadastramento Manual (AppSheet / Sheets)
        ▼
RAW_CADASTRO
        │
        ▼
STG (padronização, limpeza, normalização)
        │
        ▼
MART_CONTROLADORIA
        │
        ▼
Dashboards, relatórios e controles financeiros

---

## Estrutura do Repositório

```
controlling_postgreSQL/
├── conn.py                  # Conexão com banco PostgreSQL
├── daily_report/            # Relatórios diários e notebooks
├── rollback.py              # Scripts de rollback
├── Datasets/                # Dados de entrada (CSV)
├── notebooks/               # Jupyter Notebooks de análise
├── schemas/                 # Schemas SQL (criação, alteração, views, triggers)
│   └── byd/                 # Schemas específicos BYD
│       └── tables/
│           ├── create/      # Criação de tabelas e views
│           ├── insert/      # Scripts de inserção
│           ├── alter/       # Alterações de schema
│           ├── remove/      # Remoção de colunas
│           └── view&conults/# Views e consultas
│       └── triggers/        # Triggers e funções
└── scripts/                 # Scripts utilitários
```

---

## Como Usar

1. Clone o repositório:
        ```bash
        git clone https://github.com/SeuUsuario/controlling_postgreSQL.git
        ```
2. Instale os requisitos (Python 3.9+):
        ```bash
        pip install -r requirements.txt
        ```
3. Configure o acesso ao banco PostgreSQL em `conn.py`.
4. Execute os scripts conforme a necessidade:
        - Ingestão de dados: scripts em `Datasets/` e `schemas/byd/tables/insert/`
        - Criação de tabelas/views: scripts em `schemas/byd/tables/create/`
        - Relatórios: notebooks em `daily_report/` ou `notebooks/`

---

## Requisitos

- Python 3.9+
- PostgreSQL 13+
- Bibliotecas: pandas, psycopg2, sqlalchemy, jupyter, etc.

---

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b feature/nome-da-feature`
3. Commit suas alterações: `git commit -m 'feat: nova feature'`
4. Push para o fork: `git push origin feature/nome-da-feature`
5. Abra um Pull Request

---

## Licença

Este projeto é privado e de uso interno da Controladoria Servopa.
