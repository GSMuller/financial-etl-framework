"""
Services Package - Financial ETL Framework

Este pacote contém os serviços principais do sistema de processamento
automatizado de divergências e auditoria.

Módulos:
    audit_logger: Sistema de auditoria e rastreabilidade
    divergence_processor: Detecção e correção automática de divergências
    notification_service: Alertas e notificações via email
"""

from .audit_logger import AuditLogger
from .divergence_processor import DivergenceProcessor, Divergencia
from .notification_service import NotificationService

__all__ = [
    'AuditLogger',
    'DivergenceProcessor',
    'Divergencia',
    'NotificationService',
]
