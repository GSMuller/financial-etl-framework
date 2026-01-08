"""
Script para criar schema de auditoria no PostgreSQL

Este script executa o arquivo create_audit_tables.sql no banco de dados
configurado no .env, facilitando a instalação sem necessidade de psql.

Uso:
    python setup_audit_schema.py

Autor: Financial ETL Framework
Data: 2026-01-08
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.financial_etl.conn import get_connection

def executar_sql_file(cursor, sql_file_path):
    """
    Executa um arquivo SQL no banco de dados.
    
    Args:
        cursor: Cursor do psycopg2
        sql_file_path: Caminho para o arquivo SQL
    """
    print(f"Lendo arquivo: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Executando SQL...")
    cursor.execute(sql_content)
    print("SQL executado com sucesso")


def main():
    """Função principal."""
    print("="*70)
    print("CONFIGURAÇÃO DO SCHEMA DE AUDITORIA")
    print("="*70)
    print()
    
    # Localiza o arquivo SQL
    sql_file = project_root / 'schemas' / 'audit' / 'create_audit_tables.sql'
    
    if not sql_file.exists():
        print(f"ERRO: Arquivo SQL não encontrado: {sql_file}")
        sys.exit(1)
    
    print(f"Arquivo SQL encontrado: {sql_file}")
    print()
    
    # Confirmação do usuário
    print("Este script irá:")
    print("  1. Criar schema 'audit'")
    print("  2. Criar tabelas de auditoria")
    print("  3. Criar views de consulta")
    print("  4. Criar functions helpers")
    print()
    
    resposta = input("Deseja continuar? (S/N): ").strip().upper()
    
    if resposta != 'S':
        print("Operação cancelada pelo usuário")
        sys.exit(0)
    
    print()
    print("Conectando ao banco de dados...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Conexão estabelecida com sucesso")
        print()
        
        # Executa o SQL
        executar_sql_file(cursor, sql_file)
        
        # Commit das alterações
        conn.commit()
        print()
        print("Transação confirmada (commit)")
        
        # Verifica se as tabelas foram criadas
        print()
        print("Verificando tabelas criadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'audit'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        
        if tabelas:
            print(f"Schema 'audit' criado com sucesso!")
            print()
            print("Tabelas criadas:")
            for (tabela,) in tabelas:
                print(f"  - audit.{tabela}")
        else:
            print("AVISO: Nenhuma tabela encontrada no schema 'audit'")
        
        # Fecha conexão
        cursor.close()
        conn.close()
        
        print()
        print("="*70)
        print("CONFIGURAÇÃO CONCLUÍDA COM SUCESSO")
        print("="*70)
        print()
        print("Próximos passos:")
        print("  1. Testar processamento: python src/financial_etl/automation/daily_processor.py --modo manual")
        print("  2. Configurar agendamento: python src/financial_etl/automation/scheduler.py")
        print()
        
    except Exception as e:
        print()
        print("="*70)
        print("ERRO AO CONFIGURAR SCHEMA")
        print("="*70)
        print()
        print(f"Erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print()
        print("Verificações:")
        print("  1. Arquivo .env está configurado corretamente?")
        print("  2. PostgreSQL está rodando?")
        print("  3. Credenciais estão corretas?")
        print("  4. Usuário tem permissões para criar schemas/tabelas?")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
