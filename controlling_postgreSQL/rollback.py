"""
Script para executar rollback de transações no banco de dados PostgreSQL.
Útil quando uma operação precisa ser desfeita.
"""

import sys
from conn import get_connection

def main():
    """
    Executa rollback na conexão ativa do banco de dados.
    """
    conn = None
    
    try:
        print("🔄 Conectando ao banco de dados...")
        conn = get_connection()
        
        print("↩️  Executando rollback...")
        conn.rollback()
        
        print("✅ Rollback realizado com sucesso!")
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao executar rollback: {e}")
        return 1
        
    finally:
        if conn:
            try:
                conn.close()
                print("🔒 Conexão fechada.")
            except Exception as e:
                print(f"⚠️  Erro ao fechar conexão: {e}")

if __name__ == "__main__":
    sys.exit(main())