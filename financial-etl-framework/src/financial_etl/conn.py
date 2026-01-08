"""
Módulo de conexão com banco de dados PostgreSQL.
Utiliza variáveis de ambiente para segurança das credenciais.
"""

import os
import psycopg2
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from psycopg2.extensions import connection as Connection

# Carrega variáveis de ambiente do arquivo .env
# Define o caminho do .env na raiz do projeto (2 níveis acima)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configurações de conexão usando variáveis de ambiente
config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_connection() -> Connection:
    """
    Cria e retorna uma nova conexão com o banco de dados PostgreSQL.
    
    As credenciais são carregadas do arquivo .env na raiz do projeto.
    
    Returns:
        Connection: Objeto de conexão com o banco de dados.
    
    Raises:
        psycopg2.Error: Se houver erro na conexão.
        ValueError: Se credenciais obrigatórias não estiverem definidas.
    
    Exemplo de uso:
        from conn import get_connection
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # ... suas operações
        except Exception as e:
            print(f"Erro na conexão: {e}")
        finally:
            if conn:
                conn.close()
    """
    # Validação de credenciais obrigatórias
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"❌ Variáveis de ambiente obrigatórias não definidas: {', '.join(missing_vars)}\n"
            f"Certifique-se de ter um arquivo .env na raiz do projeto com todas as credenciais."
        )
    
    try:
        return psycopg2.connect(**config)
    except psycopg2.Error as e:
        raise psycopg2.Error(
            f"❌ Erro ao conectar ao banco de dados: {e}\n"
            f"Verifique suas credenciais no arquivo .env"
        )


@contextmanager
def db_connection() -> Generator[Connection, None, None]:
    """
    Context manager para gerenciar conexões de forma segura.
    Garante commit em caso de sucesso e rollback em caso de erro.
    
    Yields:
        Connection: Conexão ativa com o banco de dados
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()