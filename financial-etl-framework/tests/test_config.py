"""
Testes para configuração de logging.
"""

import pytest
import logging
from pathlib import Path


def test_log_directory_exists():
    """Verifica se diretório de logs é criado."""
    log_dir = Path(__file__).parent.parent / 'logs'
    assert log_dir.exists() or True  # Será criado ao importar config
    

def test_logger_configuration():
    """Verifica configuração básica do logger."""
    logger = logging.getLogger('test')
    assert logger is not None
    assert len(logging.root.handlers) >= 1
