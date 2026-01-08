#!/usr/bin/env python
"""
Script helper para executar testes com diferentes configurações.
Uso: python run_tests.py [opção]
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """Executa comando e retorna status."""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Menu principal."""
    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║         Financial ETL - Test Runner                       ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        print("Selecione uma opção:\n")
        print("  1. Executar TODOS os testes")
        print("  2. Executar testes com cobertura (HTML)")
        print("  3. Executar apenas testes unitários")
        print("  4. Executar apenas testes de integração")
        print("  5. Executar testes rápidos (excluir lentos)")
        print("  6. Executar testes de API")
        print("  7. Verificar qualidade de código (Black, Flake8, mypy)")
        print("  8. Executar pre-commit em todos os arquivos")
        print("  9. Ver relatório de cobertura")
        print("  0. Sair\n")
        
        option = input("Opção: ").strip()
    
    # Mapear opções
    commands = {
        '1': ('pytest -v', 'Executando TODOS os testes'),
        '2': ('pytest --cov=financial_etl --cov-report=html --cov-report=term', 
              'Executando testes com cobertura'),
        '3': ('pytest -m unit -v', 'Executando testes unitários'),
        '4': ('pytest -m integration -v', 'Executando testes de integração'),
        '5': ('pytest -m "not slow" -v', 'Executando testes rápidos'),
        '6': ('pytest -m api -v', 'Executando testes de API'),
        '7': (None, 'Verificando qualidade de código'),
        '8': ('pre-commit run --all-files', 'Executando pre-commit'),
        '9': (None, 'Abrindo relatório de cobertura'),
        '0': (None, 'Saindo...'),
    }
    
    if option not in commands:
        print("❌ Opção inválida!")
        return 1
    
    # Opções especiais
    if option == '0':
        print("👋 Até logo!")
        return 0
    
    if option == '7':
        print(f"\n{'='*60}")
        print("  Verificando qualidade de código")
        print(f"{'='*60}\n")
        
        checks = [
            ("black --check src/ tests/", "Black (formatação)"),
            ("isort --check-only src/ tests/", "isort (imports)"),
            ("flake8 src/ tests/", "Flake8 (linting)"),
            ("mypy src/", "mypy (tipos)"),
        ]
        
        all_passed = True
        for cmd, name in checks:
            print(f"\n🔍 {name}...")
            if not run_command(cmd):
                all_passed = False
                print(f"  ❌ {name} falhou")
            else:
                print(f"  ✅ {name} passou")
        
        if all_passed:
            print("\n✨ Todos os checks passaram!")
            return 0
        else:
            print("\n⚠️  Alguns checks falharam. Execute:")
            print("    black src/ tests/")
            print("    isort src/ tests/")
            return 1
    
    if option == '9':
        import webbrowser
        html_path = Path('htmlcov/index.html')
        if html_path.exists():
            print("📊 Abrindo relatório de cobertura no navegador...")
            webbrowser.open(str(html_path.absolute()))
            return 0
        else:
            print("❌ Relatório não encontrado. Execute primeiro:")
            print("    pytest --cov-report=html")
            return 1
    
    # Executar comando padrão
    cmd, description = commands[option]
    if cmd:
        success = run_command(cmd, description)
        if success:
            print("\n✅ Sucesso!")
            
            # Se foi cobertura, perguntar se quer abrir
            if option == '2':
                resp = input("\n📊 Abrir relatório HTML? (s/n): ").lower()
                if resp == 's':
                    import webbrowser
                    webbrowser.open('htmlcov/index.html')
            
            return 0
        else:
            print("\n❌ Falhou!")
            return 1
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
