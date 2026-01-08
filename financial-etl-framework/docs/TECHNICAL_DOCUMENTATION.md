# Sistema de Processamento Automatizado de Divergências

## Documentação Técnica v1.0.0

**Autor:** Financial ETL Framework Team  
**Data:** Janeiro 2026  
**Status:** Produção

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Componentes Principais](#componentes-principais)
4. [Instalação e Configuração](#instalação-e-configuração)
5. [Guia de Uso](#guia-de-uso)
6. [Troubleshooting](#troubleshooting)
7. [Manutenção](#manutenção)

---

## Visão Geral

### Propósito

Este sistema substitui o processo manual de detecção e correção de divergências realizado em notebooks Jupyter, oferecendo:

- Detecção automática de inconsistências em dados de bônus
- Aplicação automatizada ou assistida de correções
- Rastreabilidade completa via sistema de auditoria
- Notificações proativas por email
- API REST para integração com ferramentas de BI

### Problema Resolvido

**Antes (Manual):**
- Execução manual de notebooks
- 2-3 horas/dia de trabalho repetitivo
- Risco de erro humano
- Sem rastreabilidade adequada
- Sem alertas proativos

**Depois (Automatizado):**
- Execução automática diária
- 10-15 minutos/dia de revisão
- Correções consistentes e auditadas
- Histórico completo de todas operações
- Alertas automáticos por email

---

## Arquitetura do Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ Looker Studio  │  │  Email Alerts  │  │  CLI Scripts   ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      CAMADA DE API                           │
│           FastAPI REST API (porta 8000)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ /api/v1/divergencias  │ /api/v1/auditoria           │   │
│  │ /api/v1/relatorios    │ /api/v1/metricas            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  CAMADA DE SERVIÇOS                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ DivergenceProc.  │  │  AuditLogger     │  │Notifier   │ │
│  │ - Detecção       │  │  - Tracking      │  │- Email    │ │
│  │ - Correção       │  │  - Rollback      │  │- Alerts   │ │
│  │ - Relatórios     │  │  - Histórico     │  │           │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 CAMADA DE DADOS                              │
│                  PostgreSQL Database                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Schema: byd           │ Schema: audit                │   │
│  │ - controladoria       │ - operacoes                  │   │
│  │ - bonus_view          │ - divergencias_processadas   │   │
│  │                       │ - sessoes_processamento      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Processamento

```
┌─────────────┐
│  Scheduler  │ (Windows Task Scheduler / Cron)
│  07:00 AM   │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────────────┐
│  daily_processor.py                        │
│  1. Inicia sessão de auditoria            │
│  2. Detecta divergências (regras)         │
│  3. Aplica correções (auto/manual)        │
│  4. Gera relatório CSV                    │
│  5. Envia email com resumo                │
│  6. Finaliza sessão (métricas)            │
└────────────────────────────────────────────┘
```

---

## Componentes Principais

### 1. Sistema de Auditoria

**Arquivo:** `src/financial_etl/services/audit_logger.py`  
**Schema SQL:** `schemas/audit/create_audit_tables.sql`

**Responsabilidades:**
- Registro de todas as operações executadas
- Captura de dados antes/depois para rollback
- Tracking de sessões de processamento
- Histórico de divergências detectadas e resolvidas

**Tabelas principais:**
- `audit.operacoes`: Log de todas operações
- `audit.divergencias_processadas`: Divergências detectadas
- `audit.sessoes_processamento`: Execuções do processo diário
- `audit.configuracoes_sistema`: Configurações versionadas

**Exemplo de uso:**
```python
from src.financial_etl.services import AuditLogger

with db_connection() as conn:
    audit = AuditLogger(conn)
    
    # Inicia operação
    op_id = audit.iniciar_operacao(
        tipo_operacao='UPDATE',
        descricao='Correção de Trade Marketing',
        usuario='giovanni.5683',
        origem='MANUAL'
    )
    
    # ... executa alterações ...
    
    # Finaliza operação
    audit.finalizar_operacao(op_id, status='SUCCESS', registros_afetados=15)
```

### 2. Processador de Divergências

**Arquivo:** `src/financial_etl/services/divergence_processor.py`

**Regras implementadas:**

1. **Divergências Trade Marketing:**
   - Detecta: `bonus_view.apontamento = 'Revisar Divergência!'`
   - Corrige: Sincroniza `bonus_dpto` e `trade_mkt_dpto`
   - Confiança: 95%

2. **Pendente Verificação:**
   - Detecta: `bonus_utilizado = 'PENDENTE VERIFICACAO'`
   - Confiança aumenta com tempo pendente
   - Requer aprovação manual

3. **Validação de Valores:**
   - Detecta valores negativos ou outliers
   - Confiança: 70%
   - Requer revisão manual

**Exemplo de uso:**
```python
from src.financial_etl.services import DivergenceProcessor

with db_connection() as conn:
    processor = DivergenceProcessor(conn)
    
    # Detecta divergências
    divergencias = processor.detectar_divergencias(
        data_inicio='2025-08-01',
        data_fim='2026-05-31'
    )
    
    # Aplica correções
    resultado = processor.aplicar_correcoes(
        divergencias=divergencias,
        modo='auto',  # ou 'manual'
        usuario='sistema_automatico'
    )
    
    print(f"Corrigidas: {resultado['corrigidas_automaticamente']}")
    print(f"Pendentes: {resultado['pendentes_aprovacao']}")
```

### 3. Sistema de Notificações

**Arquivo:** `src/financial_etl/services/notification_service.py`

**Funcionalidades:**
- Envio de alertas sobre divergências detectadas
- Notificação de falhas críticas
- Resumos diários de processamento
- Templates HTML profissionais

**Configuração (.env):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@empresa.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM=noreply@empresa.com
NOTIFICATION_RECIPIENTS=controller@empresa.com,manager@empresa.com
```

### 4. API REST

**Arquivo:** `src/financial_etl/api/main.py`  
**URL:** `http://localhost:8000`

**Endpoints principais:**

```
GET  /api/v1/divergencias          # Lista divergências
POST /api/v1/divergencias/processar # Processa período
POST /api/v1/divergencias/aprovar   # Aprova correções
GET  /api/v1/auditoria/operacoes    # Histórico de operações
GET  /api/v1/auditoria/sessoes      # Sessões de processamento
GET  /api/v1/metricas/resumo        # Métricas para dashboards
GET  /api/v1/relatorios/divergencias/export # Exporta CSV/Excel
```

**Documentação interativa:** `http://localhost:8000/api/docs`

### 5. Scripts de Automação

**Processamento diário:**  
`src/financial_etl/automation/daily_processor.py`

```bash
# Processar últimas 24 horas (automático)
python daily_processor.py

# Processar período específico
python daily_processor.py --data-inicio 2025-08-01 --data-fim 2026-05-31

# Apenas detectar (sem aplicar)
python daily_processor.py --modo manual
```

**Configuração de agendamento:**  
`src/financial_etl/automation/scheduler.py`

```bash
# Configura execução automática diária
python scheduler.py
```

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL 13 ou superior
- Acesso ao banco de dados com permissões de escrita
- (Opcional) Servidor SMTP para notificações

### Passo 1: Instalar Dependências

```bash
cd financial-etl-framework

# Instalar dependências principais
pip install -r requirements.txt

# Instalar dependências da API
pip install -r requirements_api.txt
```

### Passo 2: Configurar Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
# Conexão PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=seu_database
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# Configurações SMTP (opcional mas recomendado)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@empresa.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM=noreply@empresa.com

# Destinatários de notificações
NOTIFICATION_RECIPIENTS=controller@empresa.com,manager@empresa.com
```

### Passo 3: Criar Schema de Auditoria

```bash
# Conectar ao PostgreSQL e executar
psql -h localhost -U seu_usuario -d seu_database -f schemas/audit/create_audit_tables.sql
```

Ou via pgAdmin/DBeaver: executar o conteúdo do arquivo `schemas/audit/create_audit_tables.sql`

### Passo 4: Testar Conexão

```bash
python -c "from src.financial_etl.conn import get_connection; conn = get_connection(); print('Conexão OK')"
```

### Passo 5: Executar Primeiro Processamento

```bash
# Teste manual
cd src/financial_etl/automation
python daily_processor.py --modo manual

# Se tudo OK, teste automático
python daily_processor.py --modo auto
```

### Passo 6: Configurar Agendamento

```bash
python scheduler.py
# Siga as instruções na tela
```

### Passo 7: Iniciar API (Opcional)

```bash
cd src/financial_etl/api
python main.py

# API disponível em http://localhost:8000
# Documentação: http://localhost:8000/api/docs
```

---

## Guia de Uso

### Uso Diário (Automatizado)

Uma vez configurado, o sistema roda automaticamente todos os dias às 07:00:

1. Detecta divergências nas últimas 24 horas
2. Aplica correções com alta confiança (>=95%)
3. Gera relatório CSV
4. Envia email com resumo

**Ação requerida:**
- Verificar email diário
- Aprovar divergências pendentes via API ou script

### Uso Manual (Ad-hoc)

**Reprocessar período específico:**
```bash
python daily_processor.py --data-inicio 2025-12-01 --data-fim 2025-12-31 --modo auto
```

**Apenas detectar sem aplicar:**
```bash
python daily_processor.py --data-inicio 2025-12-01 --data-fim 2025-12-31 --modo manual
```

### Aprovar Divergências Pendentes

**Via API:**
```python
import requests

response = requests.post('http://localhost:8000/api/v1/divergencias/aprovar', json={
    'divergencia_ids': [1, 2, 3],
    'usuario': 'giovanni.5683',
    'aplicar_valor_sugerido': True
})

print(response.json())
```

**Via Script Python:**
```python
from src.financial_etl.conn import db_connection
from src.financial_etl.services import AuditLogger

with db_connection() as conn:
    audit = AuditLogger(conn)
    audit.atualizar_status_divergencia(
        divergencia_id=123,
        novo_status='APPROVED',
        valor_aplicado=5000.00,
        processado_por='giovanni.5683'
    )
```

### Consultar Histórico

**Via SQL:**
```sql
-- Operações recentes
SELECT * FROM audit.operacoes 
WHERE timestamp_inicio >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY timestamp_inicio DESC;

-- Divergências abertas
SELECT * FROM audit.vw_divergencias_abertas;

-- Sessões de processamento
SELECT * FROM audit.sessoes_processamento
ORDER BY inicio_processamento DESC
LIMIT 10;
```

**Via API:**
```bash
# Lista divergências
curl http://localhost:8000/api/v1/divergencias

# Histórico de operações
curl "http://localhost:8000/api/v1/auditoria/operacoes?usuario=giovanni.5683"

# Métricas resumidas
curl http://localhost:8000/api/v1/metricas/resumo
```

---

## Troubleshooting

### Problema: Processamento não roda automaticamente

**Verificações:**
1. Tarefa está criada?
   ```bash
   # Windows
   schtasks /Query /TN FinancialETL_DailyProcessor
   ```

2. Logs de execução:
   ```bash
   # Verificar logs
   ls src/financial_etl/logs/
   tail -f src/financial_etl/logs/daily_processor_YYYY-MM-DD.log
   ```

3. Executar manualmente para ver erros:
   ```bash
   python daily_processor.py
   ```

### Problema: Emails não estão sendo enviados

**Verificações:**
1. Configuração SMTP no `.env`
2. Senha de app (não senha regular do email)
3. Testar SMTP:
   ```python
   from src.financial_etl.services import NotificationService
   
   notifier = NotificationService()
   print(f"SMTP habilitado: {notifier.smtp_enabled}")
   
   # Teste de envio
   notifier.enviar_email(
       destinatarios=['seu-email@empresa.com'],
       assunto='Teste',
       corpo_html='<h1>Teste de notificação</h1>',
       corpo_texto='Teste'
   )
   ```

### Problema: Erro de conexão com banco

**Verificações:**
1. Credenciais no `.env` corretas
2. PostgreSQL está rodando
3. Firewall permite conexão
4. Testar conexão:
   ```bash
   psql -h DB_HOST -U DB_USER -d DB_NAME
   ```

### Problema: Divergências não detectadas

**Verificações:**
1. View `byd.bonus_view` existe e tem dados
2. Período especificado contém dados
3. Verificar logs de execução
4. Executar SQL manualmente:
   ```sql
   SELECT COUNT(*) FROM byd.bonus_view
   WHERE apontamento = 'Revisar Divergência!'
   AND dta_processamento >= CURRENT_DATE - INTERVAL '1 day';
   ```

---

## Manutenção

### Limpeza de Dados Antigos

```sql
-- Limpar audit logs com mais de 1 ano
DELETE FROM audit.operacoes 
WHERE timestamp_inicio < CURRENT_DATE - INTERVAL '1 year';

-- Limpar divergências processadas antigas
DELETE FROM audit.divergencias_processadas
WHERE processado_em < CURRENT_DATE - INTERVAL '6 months'
AND status_processamento IN ('APPROVED', 'REJECTED', 'AUTO_APPLIED');
```

### Backup do Schema de Auditoria

```bash
pg_dump -h localhost -U seu_usuario -d seu_database -n audit -F c -f audit_backup_$(date +%Y%m%d).dump
```

### Monitoramento de Performance

```sql
-- Queries lentas na auditoria
SELECT 
    tipo_operacao,
    AVG(duracao_segundos) as duracao_media,
    MAX(duracao_segundos) as duracao_maxima
FROM audit.operacoes
WHERE timestamp_inicio >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY tipo_operacao
HAVING AVG(duracao_segundos) > 5
ORDER BY duracao_media DESC;
```

### Atualização do Sistema

```bash
# 1. Fazer backup do banco
pg_dump seu_database > backup_pre_update.sql

# 2. Atualizar código
git pull origin main

# 3. Atualizar dependências
pip install -r requirements.txt -r requirements_api.txt --upgrade

# 4. Executar migrations (se houver)
# psql -f schemas/migrations/vXXX_update.sql

# 5. Testar
python daily_processor.py --modo manual
```

---

## Suporte e Contatos

**Documentação:**
- Técnica: Este arquivo
- API: http://localhost:8000/api/docs
- Código: Comentários inline em todos os módulos

**Logs:**
- Processamento: `src/financial_etl/logs/daily_processor_*.log`
- API: stdout durante execução
- Sistema: `src/financial_etl/logs/app.log`

**Responsável Técnico:** Financial ETL Framework Team  
**Versão:** 1.0.0  
**Última Atualização:** Janeiro 2026
