##

import psycopg2

# Configurações de conexão
config = {
    'host': '10.100.1.86',
    'database': 'bd_bonus',
    'user': 'giovanni_aud',
    'password': 'Bonus@2025',
    'port': 5432
}

def get_connection():
    """
    Cria e retorna uma nova conexão com o banco de dados PostgreSQL.
    Exemplo de uso:
        from conn import get_connection
        conn = get_connection()
        cursor = conn.cursor()
    """
    return psycopg2.connect(**config)