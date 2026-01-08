"""
Routers Package - API REST

Este pacote contém os routers da API organizados por domínio.
"""

from . import divergences, audit, reports

__all__ = ['divergences', 'audit', 'reports']
