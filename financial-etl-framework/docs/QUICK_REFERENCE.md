# Quick Reference - Comandos Essenciais

## Testes

```bash
# Executar todos os testes
pytest

# Com verbose
pytest -v

# Com cobertura
pytest --cov

# Relatório HTML
pytest --cov-report=html

# Teste específico
pytest tests/test_conn.py

# Por marker
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Parar no primeiro erro
pytest -x

# Mostrar prints
pytest -s

# Últimos falhados
pytest --lf
```

## Formatação

```bash
# Black
black src/ tests/
black --check src/

# isort
isort src/ tests/
isort --check-only src/

# Ambos
black src/ tests/ && isort src/ tests/
```

## Linting

```bash
# Flake8
flake8 src/
flake8 src/ tests/

# Pylint
pylint src/financial_etl/

# Bandit (segurança)
bandit -r src/
```

## Type Checking

```bash
# mypy
mypy src/
mypy --strict src/financial_etl/conn.py
```

## Pre-commit

```bash
# Instalar
pre-commit install

# Executar manualmente
pre-commit run --all-files

# Executar em arquivos staged
pre-commit run

# Atualizar hooks
pre-commit autoupdate

# Pular em commit
git commit --no-verify
```

## Instalação

```bash
# Básico
pip install -e .

# Com desenvolvimento
pip install -e ".[dev]"

# Com notebooks
pip install -e ".[dev,notebooks]"

# Completo
pip install -e ".[dev,notebooks,excel]"

# Atualizar dependências
pip install --upgrade -e ".[dev]"
```

## Scripts Helper

```bash
# Menu interativo
python run_tests.py

# Windows batch
run_tests.bat all
run_tests.bat quick
run_tests.bat coverage
run_tests.bat quality
```

## Cobertura

```bash
# Gerar relatório
pytest --cov-report=html

# Abrir no navegador (Windows)
start htmlcov/index.html

# Ver no terminal
pytest --cov-report=term

# Com linhas faltantes
pytest --cov-report=term-missing
```

## Git Workflow

```bash
# 1. Criar branch
git checkout -b feature/nome-feature

# 2. Fazer mudanças
# ... código ...

# 3. Testar
pytest

# 4. Formatar
black src/ tests/
isort src/ tests/

# 5. Verificar qualidade
flake8 src/
mypy src/

# 6. Commit (pre-commit roda automaticamente)
git add .
git commit -m "feat: descrição da feature"

# 7. Push
git push origin feature/nome-feature
```

## Debug

```bash
# Executar com debugger
pytest --pdb

# Parar no primeiro erro e debugar
pytest -x --pdb

# Ver traceback completo
pytest --tb=long

# Ver variáveis locais
pytest --showlocals
```

## Performance

```bash
# Testes mais lentos
pytest --durations=10

# Paralelo (requer pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Manutenção

```bash
# Limpar cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache htmlcov .coverage

# Windows PowerShell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
Remove-Item .pytest_cache, htmlcov, .coverage -Recurse -Force -ErrorAction SilentlyContinue
```

## Documentação

```bash
# Ver ajuda pytest
pytest --help

# Ver markers disponíveis
pytest --markers

# Ver fixtures disponíveis
pytest --fixtures
```

## CI/CD Local

```bash
# Simular pipeline local
black --check src/ && \
isort --check-only src/ && \
flake8 src/ && \
mypy src/ && \
pytest --cov-fail-under=75
```

## Variáveis de Ambiente

```bash
# Linux/Mac
export DB_HOST=localhost
export DB_NAME=financial_dw

# Windows CMD
set DB_HOST=localhost
set DB_NAME=financial_dw

# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_NAME="financial_dw"

# Ou usar arquivo .env
cp .env.example .env
# Editar .env com suas credenciais
```

## Links Úteis

- Pytest: https://docs.pytest.org/
- Black: https://black.readthedocs.io/
- isort: https://pycqa.github.io/isort/
- Flake8: https://flake8.pycqa.org/
- mypy: http://mypy-lang.org/
- Pre-commit: https://pre-commit.com/

---

**Tip:** Adicione este arquivo aos seus favoritos para referência rápida!
