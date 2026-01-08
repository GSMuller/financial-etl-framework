"""
Scheduler para Execução Automatizada

Configura e gerencia agendamento de tarefas usando Windows Task Scheduler
ou cron (Linux/Mac).

Este módulo fornece funções para configurar a execução automática diária
do processamento de divergências.

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

import os
import sys
import platform
from pathlib import Path
from datetime import time as dtime

# Path do script de processamento diário
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DAILY_PROCESSOR_SCRIPT = PROJECT_ROOT / 'src' / 'financial_etl' / 'automation' / 'daily_processor.py'


def criar_task_windows(
    nome_task: str = 'FinancialETL_DailyProcessor',
    horario: dtime = dtime(7, 0),  # 07:00
    usuario: str = None
) -> bool:
    """
    Cria tarefa agendada no Windows Task Scheduler.
    
    Args:
        nome_task: Nome da tarefa no Task Scheduler
        horario: Horário de execução (padrão: 07:00)
        usuario: Usuário Windows (padrão: usuário atual)
    
    Returns:
        bool: True se criado com sucesso
    
    Exemplo:
        >>> criar_task_windows(horario=dtime(8, 30))
    """
    if platform.system() != 'Windows':
        print("Este método é apenas para Windows")
        return False
    
    python_exe = sys.executable
    script_path = str(DAILY_PROCESSOR_SCRIPT)
    
    # Obtém usuário atual se não fornecido
    if usuario is None:
        usuario = os.environ.get('USERNAME', 'SYSTEM')
    
    # Comando para criar tarefa usando schtasks
    comando = f'''schtasks /Create /SC DAILY /TN "{nome_task}" /TR "{python_exe} {script_path}" /ST {horario.strftime("%H:%M")} /RU {usuario} /F'''
    
    print(f"Criando tarefa agendada: {nome_task}")
    print(f"Horário: {horario.strftime('%H:%M')}")
    print(f"Python: {python_exe}")
    print(f"Script: {script_path}")
    print()
    
    try:
        resultado = os.system(comando)
        
        if resultado == 0:
            print(f"✓ Tarefa '{nome_task}' criada com sucesso")
            print(f"  Executará diariamente às {horario.strftime('%H:%M')}")
            print()
            print("Gerenciar tarefa:")
            print(f"  Ver: schtasks /Query /TN {nome_task}")
            print(f"  Executar agora: schtasks /Run /TN {nome_task}")
            print(f"  Deletar: schtasks /Delete /TN {nome_task} /F")
            return True
        else:
            print(f"✗ Erro ao criar tarefa (código: {resultado})")
            print("  Nota: Pode requerer permissões de administrador")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao criar tarefa: {e}")
        return False


def criar_cron_linux(
    horario: dtime = dtime(7, 0),
    usuario: str = None
) -> str:
    """
    Gera linha de crontab para Linux/Mac.
    
    Args:
        horario: Horário de execução
        usuario: Usuário Linux (padrão: usuário atual)
    
    Returns:
        str: Linha de crontab para adicionar
    
    Uso:
        1. Execute: crontab -e
        2. Adicione a linha retornada por esta função
        3. Salve e saia
    """
    python_exe = sys.executable
    script_path = str(DAILY_PROCESSOR_SCRIPT)
    log_path = PROJECT_ROOT / 'src' / 'financial_etl' / 'logs' / 'cron.log'
    
    # Formato: minuto hora dia mês dia_semana comando
    cron_line = (
        f"{horario.minute} {horario.hour} * * * "
        f"{python_exe} {script_path} >> {log_path} 2>&1"
    )
    
    print("="*70)
    print("CONFIGURAÇÃO CRON")
    print("="*70)
    print()
    print("Para agendar a execução automática:")
    print()
    print("1. Abra o editor de crontab:")
    print("   crontab -e")
    print()
    print("2. Adicione a seguinte linha:")
    print()
    print(f"   {cron_line}")
    print()
    print("3. Salve e saia (Ctrl+X, Y, Enter no nano)")
    print()
    print("4. Verifique se foi adicionado:")
    print("   crontab -l")
    print()
    print("="*70)
    
    return cron_line


def remover_task_windows(nome_task: str = 'FinancialETL_DailyProcessor') -> bool:
    """
    Remove tarefa agendada do Windows Task Scheduler.
    
    Args:
        nome_task: Nome da tarefa a remover
    
    Returns:
        bool: True se removido com sucesso
    """
    if platform.system() != 'Windows':
        print("Este método é apenas para Windows")
        return False
    
    comando = f'schtasks /Delete /TN "{nome_task}" /F'
    
    print(f"Removendo tarefa: {nome_task}")
    
    try:
        resultado = os.system(comando)
        
        if resultado == 0:
            print(f"✓ Tarefa '{nome_task}' removida com sucesso")
            return True
        else:
            print(f"✗ Erro ao remover tarefa ou tarefa não encontrada")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao remover tarefa: {e}")
        return False


def executar_agora() -> int:
    """
    Executa o processamento imediatamente (para testes).
    
    Returns:
        int: Código de saída do processo
    """
    python_exe = sys.executable
    script_path = str(DAILY_PROCESSOR_SCRIPT)
    
    print("Executando processamento imediatamente...")
    print(f"Script: {script_path}")
    print()
    
    comando = f'"{python_exe}" "{script_path}"'
    return os.system(comando)


def main():
    """
    Interface interativa para configuração do agendamento.
    """
    print("="*70)
    print("CONFIGURAÇÃO DE AGENDAMENTO - FINANCIAL ETL FRAMEWORK")
    print("="*70)
    print()
    
    sistema = platform.system()
    print(f"Sistema operacional detectado: {sistema}")
    print()
    
    if sistema == 'Windows':
        print("Opções disponíveis:")
        print("  1. Criar tarefa agendada (execução diária)")
        print("  2. Remover tarefa agendada")
        print("  3. Executar processamento agora (teste)")
        print("  4. Sair")
        print()
        
        try:
            opcao = input("Escolha uma opção (1-4): ").strip()
            
            if opcao == '1':
                print()
                horario_str = input("Horário de execução (HH:MM) [07:00]: ").strip() or "07:00"
                try:
                    hora, minuto = map(int, horario_str.split(':'))
                    horario = dtime(hora, minuto)
                    criar_task_windows(horario=horario)
                except ValueError:
                    print("✗ Formato de horário inválido")
                    
            elif opcao == '2':
                print()
                remover_task_windows()
                
            elif opcao == '3':
                print()
                executar_agora()
                
            elif opcao == '4':
                print("Encerrando...")
                
            else:
                print("✗ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário")
            
    else:
        # Linux/Mac
        print("Para sistemas Unix/Linux, use cron:")
        print()
        horario_str = input("Horário de execução (HH:MM) [07:00]: ").strip() or "07:00"
        try:
            hora, minuto = map(int, horario_str.split(':'))
            horario = dtime(hora, minuto)
            criar_cron_linux(horario=horario)
        except ValueError:
            print("✗ Formato de horário inválido")


if __name__ == '__main__':
    main()
