# Sistema de Processamento Automatizado de Divergências

## Resumo Executivo

Sistema profissional desenvolvido para automatizar a detecção e correção de divergências no Data Warehouse BYD, substituindo processos manuais por fluxo automatizado com auditoria completa.

---

## Arquivos Criados

### 1. Sistema de Auditoria

**schemas/audit/create_audit_tables.sql**
- Tabelas completas de auditoria (operacoes, divergencias_processadas, sessoes_processamento, configuracoes_sistema)
- Views de consulta (vw_operacoes_resumo, vw_divergencias_abertas)
- Functions helpers (registrar_operacao, finalizar_operacao)

**src/financial_etl/services/audit_logger.py**
- Classe AuditLogger com métodos para tracking completo
- Context managers para operações auditadas
- Registro de divergências e sessões
- Consulta de histórico e rollback

### 2. Processador de Divergências

**src/financial_etl/services/divergence_processor.py**
- Detecção automática de 3 tipos de divergências:
  - Trade Marketing (95% confiança)
  - Pendente Verificação (confiança variável)
  - Validação de Valores (70% confiança)
- Aplicação de correções automáticas ou manuais
- Geração de relatórios CSV/Excel
- Integração com sistema de auditoria

### 3. Sistema de Notificações

**src/financial_etl/services/notification_service.py**
- Envio de emails com templates HTML profissionais
- Alertas de divergências detectadas
- Resumos de processamento diário
- Notificações de falhas críticas
- Suporte a anexos

### 4. API REST

**src/financial_etl/api/main.py**
- FastAPI com documentação automática (Swagger)
- Endpoints de saúde e métricas
- CORS configurado para Looker Studio
- Handler global de exceções

**src/financial_etl/api/routers/divergences.py**
- GET /api/v1/divergencias (listar com filtros)
- POST /api/v1/divergencias/processar (executar detecção)
- POST /api/v1/divergencias/aprovar (aprovar correções)
- DELETE /api/v1/divergencias/{id}/rejeitar

**src/financial_etl/api/routers/audit.py**
- GET /api/v1/auditoria/operacoes (histórico)
- GET /api/v1/auditoria/sessoes (sessões de processamento)

**src/financial_etl/api/routers/reports.py**
- GET /api/v1/relatorios/divergencias/export (CSV/Excel)
- GET /api/v1/relatorios/metricas/performance

### 5. Scripts de Automação

**src/financial_etl/automation/daily_processor.py**
- Script principal de processamento diário
- Execução automatizada ou manual
- Logging completo em arquivo
- Geração de relatórios e envio de emails
- Suporte a argumentos de linha de comando

**src/financial_etl/automation/scheduler.py**
- Configuração de agendamento Windows/Linux
- Interface interativa
- Criação de tarefas no Task Scheduler
- Geração de crontab para Linux

### 6. Documentação

**docs/TECHNICAL_DOCUMENTATION.md**
- Visão geral e arquitetura completa
- Guia de uso detalhado
- Exemplos de código
- Troubleshooting
- Manutenção e boas práticas

**docs/API_REFERENCE.md**
- Referência completa de todos endpoints
- Exemplos de requisições e respostas
- Códigos de status HTTP
- Exemplos de integração (Python, JavaScript)
- Integração com Looker Studio

**docs/DEPLOYMENT_GUIDE.md**
- Passo a passo de instalação
- Configuração de ambiente
- Deployment de produção
- Configuração de agendamento
- Testes e validação
- Backup e recuperação

**requirements_api.txt**
- Dependências adicionais (FastAPI, uvicorn, openpyxl, etc)

---

## Como Usar

### Instalação Inicial

```bash
# 1. Instalar dependências
pip install -r requirements.txt
pip install -r requirements_api.txt

# 2. Configurar .env (ver docs/DEPLOYMENT_GUIDE.md)

# 3. Criar schema de auditoria
psql -f schemas/audit/create_audit_tables.sql

# 4. Testar conexão
python -c "from src.financial_etl.conn import get_connection; get_connection()"
```

### Execução Manual

```bash
# Processar últimas 24 horas (modo manual - apenas detecta)
cd src/financial_etl/automation
python daily_processor.py --modo manual

# Processar período específico (modo automático - aplica correções)
python daily_processor.py --data-inicio 2025-08-01 --data-fim 2026-05-31 --modo auto
```

### Configurar Execução Automática

```bash
# Windows ou Linux
cd src/financial_etl/automation
python scheduler.py

# Siga instruções interativas
```

### Iniciar API REST

```bash
cd src/financial_etl/api
python main.py

# API disponível em: http://localhost:8000
# Documentação: http://localhost:8000/api/docs
```

---

## Principais Benefícios

### Automação Completa
- Substitui processo manual de 2-3h/dia por 10-15 min de revisão
- Execução automática diária às 07:00
- Detecção baseada em regras com scores de confiança

### Rastreabilidade Total
- Todas operações registradas no schema audit
- Dados antes/depois para rollback
- Histórico completo de divergências

### Notificações Proativas
- Emails automáticos com resumo de divergências
- Alertas de falhas críticas
- Templates HTML profissionais

### Integração Facilitada
- API REST para ferramentas de BI
- Endpoints otimizados para Looker Studio
- Exportação CSV/Excel

### Qualidade e Consistência
- Correções aplicadas uniformemente
- Regras de negócio documentadas e versionadas
- Logs detalhados de todas execuções

---

## Próximos Passos

1. **Configurar ambiente:**
   - Seguir [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
   - Criar schema de auditoria
   - Configurar .env com credenciais

2. **Primeiro teste:**
   - Executar processamento manual
   - Verificar logs gerados
   - Confirmar email recebido

3. **Configurar agendamento:**
   - Usar script scheduler.py
   - Validar primeira execução automática

4. **Integração com Looker Studio (opcional):**
   - Iniciar API REST
   - Configurar fonte de dados JSON/REST
   - Usar endpoint /api/v1/metricas/resumo

5. **Treinamento:**
   - Revisar documentação técnica
   - Testar aprovação de divergências via API
   - Familiarizar com logs e auditoria

---

## Suporte

**Documentação:**
- Técnica: [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)
- API: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- Deploy: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

**Logs:**
- `src/financial_etl/logs/daily_processor_*.log`
- `src/financial_etl/logs/app.log`

**Auditoria:**
```sql
-- Ver sessões recentes
SELECT * FROM audit.sessoes_processamento 
ORDER BY inicio_processamento DESC LIMIT 10;

-- Ver divergências abertas
SELECT * FROM audit.vw_divergencias_abertas;
```

---

**Sistema desenvolvido com foco em:**
- Profissionalismo e qualidade de código
- Documentação completa e clara
- Facilidade de manutenção
- Rastreabilidade e auditoria
- Escalabilidade futura
