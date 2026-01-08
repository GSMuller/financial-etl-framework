"""
Financial ETL Framework - PostgreSQL Data Warehouse
Pacote para ETL de dados financeiros e controladoria.
"""

__version__ = "1.0.0"
__author__ = "Giovanni Muller"

from .conn import get_connection, db_connection
from .config import logger

__all__ = ['get_connection', 'db_connection', 'logger']
