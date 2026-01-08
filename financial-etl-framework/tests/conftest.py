"""
Fixtures compartilhadas para todos os testes do projeto.
"""

import pytest
import os
from unittest.mock import MagicMock, Mock
from datetime import datetime, date
from typing import Generator


@pytest.fixture
def mock_db_connection():
    """
    Fixture para simular uma conexão com banco de dados PostgreSQL.
    
    Returns:
        MagicMock: Objeto mock com cursor e métodos de commit/rollback
    """
    conn = MagicMock()
    cursor = MagicMock()
    
    # Configurar cursor
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.rowcount = 0
    cursor.description = None
    
    # Configurar connection
    conn.cursor.return_value = cursor
    conn.commit.return_value = None
    conn.rollback.return_value = None
    conn.close.return_value = None
    
    return conn


@pytest.fixture
def mock_cursor():
    """
    Fixture para simular um cursor de banco de dados.
    
    Returns:
        MagicMock: Cursor mock com métodos execute, fetchone, fetchall
    """
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.rowcount = 0
    cursor.description = None
    cursor.lastrowid = 1
    
    return cursor


@pytest.fixture
def sample_divergencia_data():
    """
    Dados de exemplo para testes de divergências.
    
    Returns:
        dict: Dicionário com dados de uma divergência típica
    """
    return {
        'id_nota': 'NF-123456',
        'tipo_divergencia': 'trade_marketing',
        'valor_esperado': 5000.00,
        'valor_encontrado': 0.00,
        'bonus_esperado': 'Trade Marketing',
        'bonus_encontrado': 'PENDENTE VERIFICACAO',
        'confianca': 0.95,
        'data_emissao': date(2026, 1, 1),
        'chassi': 'ABC123XYZ456',
        'modelo': 'BYD Dolphin'
    }


@pytest.fixture
def sample_audit_operation():
    """
    Dados de exemplo para testes de auditoria.
    
    Returns:
        dict: Dicionário com dados de uma operação de auditoria
    """
    return {
        'operacao_id': 1,
        'tipo_operacao': 'UPDATE',
        'tabela_afetada': 'byd.controladoria',
        'registro_id': 'NF-123456',
        'usuario': 'sistema',
        'timestamp_inicio': datetime(2026, 1, 8, 10, 0, 0),
        'status': 'em_andamento'
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Configura variáveis de ambiente para testes.
    
    Args:
        monkeypatch: Fixture do pytest para modificar variáveis de ambiente
    """
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_NAME', 'test_db')
    monkeypatch.setenv('DB_USER', 'test_user')
    monkeypatch.setenv('DB_PASSWORD', 'test_password')
    monkeypatch.setenv('DB_PORT', '5432')
    
    # Email configs
    monkeypatch.setenv('SMTP_HOST', 'smtp.test.com')
    monkeypatch.setenv('SMTP_PORT', '587')
    monkeypatch.setenv('SMTP_USER', 'test@test.com')
    monkeypatch.setenv('SMTP_PASSWORD', 'test_pass')
    monkeypatch.setenv('EMAIL_FROM', 'noreply@test.com')


@pytest.fixture
def mock_smtp():
    """
    Mock para servidor SMTP usado em testes de notificações.
    
    Returns:
        MagicMock: Objeto mock do smtplib.SMTP
    """
    smtp = MagicMock()
    smtp.starttls.return_value = None
    smtp.login.return_value = None
    smtp.send_message.return_value = None
    smtp.quit.return_value = None
    
    return smtp


@pytest.fixture
def sample_database_rows():
    """
    Conjunto de linhas de exemplo do banco de dados.
    
    Returns:
        list: Lista de tuplas simulando resultados de query
    """
    return [
        (1, 'NF-123456', 'trade_marketing', 'pendente', datetime(2026, 1, 8)),
        (2, 'NF-123457', 'validacao_valores', 'corrigido', datetime(2026, 1, 7)),
        (3, 'NF-123458', 'pendente_verificacao', 'pendente', datetime(2026, 1, 6))
    ]


@pytest.fixture
def mock_fastapi_client():
    """
    Cliente de teste para FastAPI.
    
    Returns:
        TestClient: Cliente configurado para testes de API
    """
    from fastapi.testclient import TestClient
    from financial_etl.api.main import app
    
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_env():
    """
    Fixture que roda automaticamente antes de cada teste para limpar ambiente.
    """
    # Salvar estado original
    original_env = os.environ.copy()
    
    yield
    
    # Restaurar estado original após o teste
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_csv_file(tmp_path):
    """
    Cria um arquivo CSV temporário para testes.
    
    Args:
        tmp_path: Fixture do pytest que fornece diretório temporário
    
    Returns:
        Path: Caminho para o arquivo CSV temporário
    """
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(
        "id_nota,chassi,valor,bonus\n"
        "NF-001,CHASSI001,50000,Trade Marketing\n"
        "NF-002,CHASSI002,60000,IPVA, Wallbox\n"
    )
    return csv_file


@pytest.fixture
def sample_divergencias_list(sample_divergencia_data):
    """
    Lista de divergências para testes em lote.
    
    Returns:
        list: Lista com múltiplas divergências
    """
    return [
        {**sample_divergencia_data, 'id_nota': f'NF-{i}', 'chassi': f'CHASSI{i}'}
        for i in range(1, 6)
    ]
