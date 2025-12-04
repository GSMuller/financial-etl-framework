# Servopa Data Warehouse — Controladoria  
Migração, padronização e consolidação de dados operacionais e administrativos  
PostgreSQL • BigQuery • ETL • Python • RDBMS  

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
