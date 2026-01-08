# Guia de Implantação e Deployment

## Sistema de Processamento Automatizado de Divergências

---

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Passo a Passo](#instalação-passo-a-passo)
3. [Configuração de Ambiente](#configuração-de-ambiente)
4. [Deployment da API](#deployment-da-api)
5. [Configuração de Agendamento](#configuração-de-agendamento)
6. [Testes e Validação](#testes-e-validação)
7. [Monitoramento](#monitoramento)
8. [Backup e Recuperação](#backup-e-recuperação)

---

## Pré-requisitos

### Software Necessário

- **Python:** 3.9 ou superior
- **PostgreSQL:** 13 ou superior
- **Git:** Para versionamento
- **Acesso:** Permissões de leitura/escrita no banco de dados

### Conhecimentos Recomendados

- SQL básico
- Linha de comando (CMD/PowerShell/Bash)
- Conceitos de API REST (para integração)

### Recursos de Sistema

- **Memória RAM:** Mínimo 4GB, recomendado 8GB
- **Disco:** 10GB livres para logs e relatórios
- **Rede:** Acesso ao banco PostgreSQL e servidor SMTP

---

## Instalação Passo a Passo

### 1. Clonar ou Atualizar Repositório

```bash
# Se ainda não possui o repositório
git clone <url-do-repositorio>
cd financial-etl-framework

# Se já possui, atualize
git pull origin main
```

### 2. Criar Ambiente Virtual Python

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Instalar todas as dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_api.txt

# Verificar instalação
pip list
```

### 4. Configurar Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
# ===== POSTGRESQL =====
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nome_do_database
DB_USER=usuario_postgres
DB_PASSWORD=senha_postgres

# ===== SMTP (NOTIFICAÇÕES) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@empresa.com
SMTP_PASSWORD=senha-de-app-gmail
SMTP_FROM=noreply@empresa.com

# ===== DESTINATÁRIOS =====
# Separados por vírgula
NOTIFICATION_RECIPIENTS=controller@empresa.com,manager@empresa.com,analista@empresa.com

# ===== AMBIENTE =====
# PRODUCTION, STAGING ou DEVELOPMENT
ENVIRONMENT=PRODUCTION
```

**Nota sobre senha do Gmail:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Crie senha de app
3. Use essa senha no `SMTP_PASSWORD`

### 5. Configurar Banco de Dados

#### 5.1. Criar Schema de Auditoria

```bash
# Método 1: Via psql
psql -h localhost -U seu_usuario -d seu_database -f schemas/audit/create_audit_tables.sql

# Método 2: Via pgAdmin
# 1. Abra pgAdmin
# 2. Conecte ao banco
# 3. Abra Query Tool
# 4. Carregue schemas/audit/create_audit_tables.sql
# 5. Execute (F5)
```

#### 5.2. Verificar Criação

```sql
-- Deve retornar as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'audit';

-- Resultado esperado:
-- operacoes
-- divergencias_processadas
-- sessoes_processamento
-- configuracoes_sistema
```

### 6. Testar Conexão

```bash
# Teste de conexão básico
python -c "from src.financial_etl.conn import get_connection; conn = get_connection(); print('Conexão OK'); conn.close()"

# Se aparecer "Conexão OK", prossiga
```

---

## Configuração de Ambiente

### Estrutura de Diretórios

```
financial-etl-framework/
├── src/
│   └── financial_etl/
│       ├── api/                 # API REST
│       ├── services/            # Serviços principais
│       ├── automation/          # Scripts de automação
│       ├── logs/                # Logs de execução (criado automaticamente)
│       ├── conn.py              # Conexão DB
│       └── config.py            # Configurações
├── schemas/
│   ├── audit/                   # Schema de auditoria
│   └── byd/                     # Schemas BYD existentes
├── Datasets/                    # Relatórios CSV gerados
├── docs/                        # Documentação
├── .env                         # Variáveis de ambiente (NÃO versionar)
├── requirements.txt             # Dependências Python
└── requirements_api.txt         # Dependências da API
```

### Permissões de Banco de Dados

Usuário PostgreSQL precisa ter:

```sql
-- Permissões necessárias
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA byd TO seu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO seu_usuario;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO seu_usuario;
```

---

## Deployment da API

### Desenvolvimento Local

```bash
# Navegar para diretório da API
cd src/financial_etl/api

# Iniciar servidor de desenvolvimento
python main.py

# API disponível em: http://localhost:8000
# Documentação: http://localhost:8000/api/docs
```

### Produção com Uvicorn

```bash
# Instalar uvicorn
pip install uvicorn[standard]

# Executar com múltiplos workers
cd src/financial_etl/api
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info

# Para rodar em background (Windows)
start /B uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Para rodar em background (Linux)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > api.log 2>&1 &
```

### Produção com Gunicorn (Linux)

```bash
pip install gunicorn

cd src/financial_etl/api
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Como Serviço Windows

Criar arquivo `start_api.bat`:

```batch
@echo off
cd /d "C:\caminho\para\financial-etl-framework\src\financial_etl\api"
call ..\..\..\..\venv\Scripts\activate.bat
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
pause
```

Criar tarefa no Task Scheduler para executar na inicialização.

### Como Serviço Linux (systemd)

Criar `/etc/systemd/system/financial-etl-api.service`:

```ini
[Unit]
Description=Financial ETL API
After=network.target postgresql.service

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/financial-etl-framework
Environment="PATH=/caminho/para/venv/bin"
ExecStart=/caminho/para/venv/bin/uvicorn src.financial_etl.api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable financial-etl-api
sudo systemctl start financial-etl-api
sudo systemctl status financial-etl-api
```

---

## Configuração de Agendamento

### Windows Task Scheduler

#### Método 1: Script Interativo

```bash
cd src/financial_etl/automation
python scheduler.py

# Siga instruções na tela:
# 1. Criar tarefa agendada
# 2. Horário: 07:00 (ou desejado)
```

#### Método 2: Manual

1. Abrir Task Scheduler (Agendador de Tarefas)
2. Criar Tarefa Básica
3. Nome: `FinancialETL_DailyProcessor`
4. Gatilho: Diariamente às 07:00
5. Ação: Iniciar programa
   - Programa: `C:\caminho\para\venv\Scripts\python.exe`
   - Argumentos: `C:\caminho\para\financial-etl-framework\src\financial_etl\automation\daily_processor.py`
   - Iniciar em: `C:\caminho\para\financial-etl-framework`

#### Método 3: Via Command Line

```batch
schtasks /Create /SC DAILY /TN "FinancialETL_DailyProcessor" /TR "C:\caminho\para\venv\Scripts\python.exe C:\caminho\para\financial-etl-framework\src\financial_etl\automation\daily_processor.py" /ST 07:00 /RU SYSTEM /F
```

### Linux Cron

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa às 07:00 diariamente)
0 7 * * * /caminho/para/venv/bin/python /caminho/para/financial-etl-framework/src/financial_etl/automation/daily_processor.py >> /caminho/para/logs/cron.log 2>&1

# Salvar e sair
# Verificar
crontab -l
```

---

## Testes e Validação

### Teste 1: Conexão com Banco

```bash
python -c "from src.financial_etl.conn import get_connection; conn = get_connection(); print('OK'); conn.close()"
```

### Teste 2: Execução Manual do Processamento

```bash
cd src/financial_etl/automation

# Modo manual (apenas detecta, não aplica)
python daily_processor.py --modo manual

# Verificar logs
type ..\logs\daily_processor_2026-01-08.log  # Windows
cat ../logs/daily_processor_2026-01-08.log   # Linux
```

### Teste 3: Envio de Email

```python
from src.financial_etl.services import NotificationService

notifier = NotificationService()
print(f"SMTP configurado: {notifier.smtp_enabled}")

sucesso = notifier.enviar_email(
    destinatarios=['seu-email@empresa.com'],
    assunto='Teste de Notificação',
    corpo_html='<h1>Sistema funcionando</h1>',
    corpo_texto='Sistema funcionando'
)

print(f"Email enviado: {sucesso}")
```

### Teste 4: API Funcionando

```bash
# Iniciar API em terminal separado
cd src/financial_etl/api
python main.py

# Em outro terminal, testar:
curl http://localhost:8000/
curl http://localhost:8000/api/health
```

### Teste 5: Processamento Completo

```bash
# Executar processamento automático em período de teste
python daily_processor.py --data-inicio 2025-12-01 --data-fim 2025-12-05 --modo auto

# Verificar:
# 1. Logs gerados
# 2. Email recebido
# 3. Dados na tabela audit.sessoes_processamento
```

---

## Monitoramento

### Logs

**Localização:**
- Processamento: `src/financial_etl/logs/daily_processor_YYYY-MM-DD.log`
- Aplicação: `src/financial_etl/logs/app.log`
- API: stdout durante execução

**Visualizar logs recentes:**

```bash
# Windows
type src\financial_etl\logs\daily_processor_2026-01-08.log

# Linux
tail -f src/financial_etl/logs/daily_processor_$(date +%Y-%m-%d).log
```

### Verificar Execução Agendada

```bash
# Windows
schtasks /Query /TN FinancialETL_DailyProcessor /V

# Linux
crontab -l
grep "python.*daily_processor" /var/log/syslog
```

### Monitorar Banco de Dados

```sql
-- Sessões de processamento recentes
SELECT * FROM audit.sessoes_processamento
ORDER BY inicio_processamento DESC
LIMIT 10;

-- Operações com erro
SELECT * FROM audit.operacoes
WHERE status = 'FAILED'
ORDER BY timestamp_inicio DESC
LIMIT 20;

-- Divergências ainda abertas
SELECT COUNT(*) FROM audit.vw_divergencias_abertas;
```

### Dashboard de Monitoramento

Criar view SQL para dashboard:

```sql
CREATE OR REPLACE VIEW audit.vw_dashboard_monitoramento AS
SELECT 
    CURRENT_DATE as data_consulta,
    (SELECT COUNT(*) FROM audit.vw_divergencias_abertas) as divergencias_abertas,
    (SELECT COUNT(*) FROM audit.sessoes_processamento WHERE inicio_processamento::date = CURRENT_DATE) as execucoes_hoje,
    (SELECT status FROM audit.sessoes_processamento WHERE tipo_sessao = 'DAILY_AUTO' ORDER BY inicio_processamento DESC LIMIT 1) as status_ultima_execucao,
    (SELECT COUNT(*) FROM audit.operacoes WHERE timestamp_inicio::date = CURRENT_DATE AND status = 'FAILED') as erros_hoje;
```

---

## Backup e Recuperação

### Backup do Schema de Auditoria

```bash
# Backup diário automático (adicionar ao cron/task scheduler)
pg_dump -h localhost -U seu_usuario -d seu_database -n audit -F c -f "backup_audit_$(date +%Y%m%d).dump"

# Backup com SQL puro
pg_dump -h localhost -U seu_usuario -d seu_database -n audit -f "backup_audit_$(date +%Y%m%d).sql"
```

### Restauração

```bash
# De arquivo .dump
pg_restore -h localhost -U seu_usuario -d seu_database backup_audit_20260108.dump

# De arquivo .sql
psql -h localhost -U seu_usuario -d seu_database -f backup_audit_20260108.sql
```

### Backup de Logs

```bash
# Windows - criar task scheduler
xcopy src\financial_etl\logs\*.log D:\backups\logs\ /D /Y

# Linux - adicionar ao crontab
0 2 * * * tar -czf /backup/logs/logs_$(date +\%Y\%m\%d).tar.gz /caminho/para/logs/*.log
```

---

## Checklist de Implantação

Antes de considerar o sistema em produção:

- [ ] Banco de dados configurado e testado
- [ ] Schema de auditoria criado
- [ ] Arquivo .env configurado corretamente
- [ ] Teste de conexão bem-sucedido
- [ ] Teste de processamento manual bem-sucedido
- [ ] Emails sendo enviados corretamente
- [ ] Agendamento configurado (Task Scheduler/Cron)
- [ ] Primeira execução automática bem-sucedida
- [ ] API funcionando (se utilizada)
- [ ] Logs sendo gerados corretamente
- [ ] Backup configurado
- [ ] Documentação revisada
- [ ] Usuários treinados

---

## Troubleshooting de Deployment

### Erro: ModuleNotFoundError

```bash
# Verificar se está no venv
which python  # Linux
where python  # Windows

# Reinstalar dependências
pip install -r requirements.txt -r requirements_api.txt
```

### Erro: Connection refused (PostgreSQL)

```bash
# Verificar se PostgreSQL está rodando
# Windows
sc query postgresql-x64-13

# Linux
sudo systemctl status postgresql

# Testar conexão manual
psql -h localhost -U seu_usuario -d seu_database
```

### Erro: SMTP Authentication failed

- Verificar senha de app (não senha regular)
- Habilitar "Aplicativos menos seguros" no Gmail
- Verificar firewall bloqueando porta 587

### Task Scheduler não executa

- Verificar se caminho do Python está correto
- Usar caminhos absolutos
- Configurar "Iniciar em" com diretório do projeto
- Executar como usuário com permissões adequadas

---

**Última atualização:** Janeiro 2026  
**Versão:** 1.0.0
