"""
Testes para o script de rollback.
"""

import pytest
from unittest.mock import patch, MagicMock
from rollback import main


class TestRollback:
    
    @patch('rollback.get_connection')
    def test_rollback_success(self, mock_get_conn):
        """Testa execução bem-sucedida do rollback."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = main()
        
        assert result == 0
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('rollback.get_connection')
    def test_rollback_connection_error(self, mock_get_conn):
        """Testa falha na conexão."""
        mock_get_conn.side_effect = Exception("Erro de conexão")
        
        result = main()
        
        assert result == 1
