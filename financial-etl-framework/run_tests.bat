@echo off
REM Script Windows para executar testes facilmente
REM Uso: run_tests.bat [all|quick|coverage|quality]

setlocal

if "%1"=="" goto menu
if /i "%1"=="all" goto all_tests
if /i "%1"=="quick" goto quick_tests
if /i "%1"=="coverage" goto coverage_tests
if /i "%1"=="quality" goto quality_checks
goto menu

:menu
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Financial ETL - Test Runner (Windows)             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo  Use: run_tests.bat [comando]
echo.
echo  Comandos disponíveis:
echo    all       - Executar todos os testes
echo    quick     - Testes rápidos (sem lentos)
echo    coverage  - Testes com cobertura HTML
echo    quality   - Verificar qualidade de código
echo.
echo  Ou execute diretamente: python run_tests.py
echo.
goto end

:all_tests
echo.
echo ═══════════════════════════════════════════════════════════
echo   Executando TODOS os testes
echo ═══════════════════════════════════════════════════════════
echo.
pytest -v
goto end

:quick_tests
echo.
echo ═══════════════════════════════════════════════════════════
echo   Executando testes rápidos
echo ═══════════════════════════════════════════════════════════
echo.
pytest -m "not slow" -v
goto end

:coverage_tests
echo.
echo ═══════════════════════════════════════════════════════════
echo   Executando testes com cobertura
echo ═══════════════════════════════════════════════════════════
echo.
pytest --cov=financial_etl --cov-report=html --cov-report=term
echo.
echo Relatório HTML gerado em: htmlcov\index.html
set /p OPEN="Abrir relatório no navegador? (s/n): "
if /i "%OPEN%"=="s" start htmlcov\index.html
goto end

:quality_checks
echo.
echo ═══════════════════════════════════════════════════════════
echo   Verificando qualidade de código
echo ═══════════════════════════════════════════════════════════
echo.
echo Verificando formatação (Black)...
black --check src\ tests\
if %errorlevel% neq 0 (
    echo ❌ Black falhou
    set FAILED=1
) else (
    echo ✅ Black passou
)

echo.
echo Verificando imports (isort)...
isort --check-only src\ tests\
if %errorlevel% neq 0 (
    echo ❌ isort falhou
    set FAILED=1
) else (
    echo ✅ isort passou
)

echo.
echo Verificando linting (Flake8)...
flake8 src\ tests\
if %errorlevel% neq 0 (
    echo ❌ Flake8 falhou
    set FAILED=1
) else (
    echo ✅ Flake8 passou
)

echo.
echo Verificando tipos (mypy)...
mypy src\
if %errorlevel% neq 0 (
    echo ❌ mypy falhou
    set FAILED=1
) else (
    echo ✅ mypy passou
)

echo.
if defined FAILED (
    echo ⚠️  Alguns checks falharam. Para corrigir:
    echo     black src\ tests\
    echo     isort src\ tests\
) else (
    echo ✨ Todos os checks passaram!
)
goto end

:end
endlocal
