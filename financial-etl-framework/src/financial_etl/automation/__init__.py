"""
Automation Package - Financial ETL Framework

Scripts para automação e agendamento de processamento.
"""

from .daily_processor import DailyProcessor
from .scheduler import criar_task_windows, criar_cron_linux, executar_agora

__all__ = [
    'DailyProcessor',
    'criar_task_windows',
    'criar_cron_linux',
    'executar_agora',
]
