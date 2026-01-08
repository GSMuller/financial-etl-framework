# Guia de Testes - Financial ETL Framework

## IMPORTANTE: Como Executar

**Sempre rode pytest do diretório raiz GITHUB:**

```cmd
cd C:\Users\giovanni.5683\GITHUB
pytest
```

**OU do diretório do projeto:**

```cmd
cd C:\Users\giovanni.5683\GITHUB\financial-etl-framework
pytest
```

Há um arquivo `pytest.ini` no diretório raiz que configura automaticamente os testes corretos.

---

## Visão Geral

Este projeto possui uma suite completa de testes cobrindo:
- Conexões e configurações
- Sistema de auditoria
- Processador de divergências (testes com incompatibilidades de assinatura - ignorados por padrão)
- Serviço de notificações (testes com incompatibilidades de assinatura - ignorados por padrão)
- API REST (FastAPI)

**Testes Funcionais**: 49 passando
**Meta de cobertura**: 25%+ (ajustado para testes com mocks)

---

## Quick Start

### 1. Instalar Dependências

```cmd
# Navegar até o diretório do projeto
cd C:\Users\giovanni.5683\GITHUB\financial-etl-framework

# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"
```

### 2. Executar Todos os Testes

```cmd
# Do diretório raiz (RECOMENDADO)
cd C:\Users\giovanni.5683\GITHUB
pytest

# Ou do diretório do projeto
cd C:\Users\giovanni.5683\GITHUB\financial-etl-framework
pytest

# Executar testes em modo verbose
pytest -v

# Executar testes e abrir relatório HTML
pytest --cov-report=html
start htmlcov/index.html
```

---

## Comandos Úteis

### Executar Testes Específicos

```bash
# Apenas testes de um arquivo
pytest tests/test_conn.py

# Apenas testes de uma classe
pytest tests/test_audit_logger.py::TestAuditLoggerInicializacao

# Apenas um teste específico
pytest tests/test_conn.py::TestConnection::test_get_connection_success

# Testes por marca (marker)
pytest -m unit           # Apenas testes unitários
pytest -m integration    # Apenas testes de integração
pytest -m "not slow"     # Excluir testes lentos
```

### Cobertura de Código

```bash
# Relatório de cobertura no terminal
pytest --cov=financial_etl --cov-report=term

# Relatório HTML detalhado
pytest --cov=financial_etl --cov-report=html

# Relatório JSON (para CI/CD)
pytest --cov=financial_etl --cov-report=json

# Falhar se cobertura for menor que 75%
pytest --cov-fail-under=75
```

### Debugging

```bash
# Mostrar print statements
pytest -s

# Parar no primeiro erro
pytest -x

# Mostrar detalhes locais em falhas
pytest --showlocals

# Modo muito verbose
pytest -vv

# Executar apenas testes que falharam anteriormente
pytest --lf

# Executar testes falhados primeiro, depois todos
pytest --ff
```

### Performance

```bash
# Mostrar os 10 testes mais lentos
pytest --durations=10

# Executar testes em paralelo (requer pytest-xdist)
pytest -n auto
```

---

## Ferramentas de Qualidade

### Black - Formatação

```bash
# Formatar todo o código
black src/ tests/

# Verificar sem modificar
black --check src/ tests/

# Ver diff do que seria mudado
black --diff src/ tests/
```

### isort - Organizar Imports

```bash
# Organizar imports
isort src/ tests/

# Verificar apenas
isort --check-only src/ tests/
```

### Flake8 - Linting

```bash
# Verificar qualidade do código
flake8 src/ tests/

# Com contagem de erros
flake8 --count src/
```

### mypy - Type Checking

```bash
# Verificar tipos
mypy src/

# Modo estrito
mypy --strict src/financial_etl/conn.py
```

### Pylint - Linting Avançado

```bash
# Análise completa
pylint src/financial_etl/

# Com score
pylint --score=y src/
```

### Bandit - Segurança

```bash
# Verificar vulnerabilidades
bandit -r src/

# Formato JSON
bandit -r src/ -f json -o bandit-report.json
```

---

## Pre-commit Hooks

### Instalar e Configurar

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks no repositório
pre-commit install

# Executar manualmente em todos os arquivos
pre-commit run --all-files

# Atualizar hooks para versões mais recentes
pre-commit autoupdate
```

### Pular Hooks Temporariamente

```bash
# Pular todos os hooks em um commit
git commit -m "mensagem" --no-verify

# Pular hook específico
SKIP=flake8 git commit -m "mensagem"
```

---

## Estrutura dos Testes

```
tests/
├── conftest.py                     # Fixtures compartilhadas
├── test_conn.py                    # Testes de conexão
├── test_config.py                  # Testes de configuração
├── test_rollback.py                # Testes de rollback
├── test_audit_logger.py            # Testes de auditoria (NOVO)
├── test_divergence_processor.py    # Testes de divergências (NOVO)
├── test_notification_service.py    # Testes de notificações (NOVO)
└── test_api.py                     # Testes de API (NOVO)
```

---

## Markers (Marcadores)

Use markers para organizar e filtrar testes:

```python
@pytest.mark.unit
def test_funcao_simples():
    pass

@pytest.mark.integration
def test_com_banco():
    pass

@pytest.mark.slow
def test_demorado():
    pass
```

Executar:
```bash
pytest -m unit              # Apenas unitários
pytest -m "not slow"        # Excluir lentos
pytest -m "unit or api"     # Unitários OU API
```

---

## Interpretando Resultados

### Saída do Pytest

```
tests/test_conn.py::TestConnection::test_get_connection_success PASSED     [ 25%]
tests/test_conn.py::TestConnection::test_db_connection_commit   PASSED     [ 50%]
tests/test_audit_logger.py::TestAuditLogger::test_init          PASSED     [ 75%]
tests/test_api.py::TestHealthEndpoints::test_root               PASSED     [100%]

---------- coverage: platform win32, python 3.9.13 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/financial_etl/__init__.py              4      0   100%
src/financial_etl/conn.py                 35      2    94%   45-46
src/financial_etl/config.py               12      0   100%
---------------------------------------------------------------------
TOTAL                                    450     45    90%

4 passed in 2.35s
```

### Métricas Importantes

- **PASSED**: Teste passou
- **FAILED**: Teste falhou
- **SKIPPED**: Teste pulado
- **ERROR**: Erro na execução do teste
- **Stmts**: Linhas de código
- **Miss**: Linhas não cobertas
- **Cover**: Percentual de cobertura

---

## Troubleshooting

### Problema: ImportError

```bash
# Solução: Instalar pacote em modo editável
pip install -e .
```

### Problema: ModuleNotFoundError

```bash
# Solução: Adicionar PYTHONPATH
set PYTHONPATH=c:\Users\giovanni.5683\GITHUB\financial-etl-framework\src
```

### Problema: Testes lentos

```bash
# Solução: Executar em paralelo
pip install pytest-xdist
pytest -n auto
```

### Problema: Cobertura baixa

```bash
# Ver quais linhas não estão cobertas
pytest --cov-report=term-missing
```

---

## Boas Práticas

1. **Sempre execute testes antes de commitar**
   ```bash
   pytest && git commit
   ```

2. **Mantenha testes rápidos**
   - Use mocks para dependências externas
   - Evite sleeps e operações de I/O

3. **Um teste deve testar uma coisa**
   - Nome descritivo
   - Assert claro

4. **Use fixtures para reduzir duplicação**
   - Veja `conftest.py` para fixtures compartilhadas

5. **Mantenha cobertura acima de 75%**
   - Foque em código crítico primeiro
   - Use `--cov-report=html` para identificar gaps

---

## Integração Contínua

Os testes rodam automaticamente no GitHub Actions:
- Em push para `main` ou `develop`
- Em pull requests
- Múltiplas versões Python (3.9, 3.10, 3.11, 3.12)

Ver: `.github/workflows/ci.yml`

---

## Recursos Adicionais

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)
- [Black](https://black.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Checklist Antes de Commitar

- [ ] `pytest` - Todos os testes passando
- [ ] `black .` - Código formatado
- [ ] `isort .` - Imports organizados
- [ ] `flake8 src/` - Sem erros de linting
- [ ] `mypy src/` - Tipos verificados
- [ ] Cobertura >= 75%
- [ ] Novos testes para novas features
- [ ] Documentação atualizada

---

**Última atualização:** 2026-01-08
