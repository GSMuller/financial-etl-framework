"""
Testes para o módulo de conexão com o banco de dados.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from conn import get_connection, db_connection


class TestConnection:
    
    def test_get_connection_missing_credentials(self, monkeypatch):
        """Verifica se erro é levantado quando credenciais estão faltando."""
        monkeypatch.delenv('DB_HOST', raising=False)
        monkeypatch.delenv('DB_NAME', raising=False)
        
        with pytest.raises(ValueError, match="Variáveis de ambiente obrigatórias"):
            get_connection()
    
    @patch('conn.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Testa conexão bem-sucedida."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = get_connection()
        
        assert conn is not None
        mock_connect.assert_called_once()
    
    @patch('conn.psycopg2.connect')
    def test_db_connection_commit_on_success(self, mock_connect):
        """Verifica que commit é executado em caso de sucesso."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with db_connection() as conn:
            pass
        
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('conn.psycopg2.connect')
    def test_db_connection_rollback_on_error(self, mock_connect):
        """Verifica que rollback é executado em caso de erro."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with pytest.raises(Exception):
            with db_connection() as conn:
                raise Exception("Erro simulado")
        
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
