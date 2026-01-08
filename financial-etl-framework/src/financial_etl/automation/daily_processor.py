"""
Script de Processamento Diário Automatizado

Este script substitui o processo manual do notebook, executando
automaticamente a detecção e correção de divergências.

Funcionalidades:
- Detecção automática de divergências
- Aplicação de correções com alta confiança
- Registro completo de auditoria
- Envio de alertas por email
- Geração de relatórios

Uso:
    python daily_processor.py [--data-inicio YYYY-MM-DD] [--data-fim YYYY-MM-DD] [--modo auto|manual]

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

import sys
import argparse
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional

# Adiciona path do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.financial_etl.conn import db_connection
from src.financial_etl.services import (
    DivergenceProcessor,
    AuditLogger,
    NotificationService
)

# Configuração de logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'daily_processor_{date.today()}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DailyProcessor:
    """
    Processador diário automatizado de divergências.
    
    Gerencia o ciclo completo de detecção, correção e notificação.
    """
    
    def __init__(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        modo: str = 'auto'
    ):
        """
        Inicializa o processador diário.
        
        Args:
            data_inicio: Data início no formato YYYY-MM-DD (padrão: ontem)
            data_fim: Data fim no formato YYYY-MM-DD (padrão: hoje)
            modo: 'auto' para aplicação automática, 'manual' apenas detecta
        """
        # Define período padrão se não fornecido
        if data_inicio is None:
            data_inicio = (date.today() - timedelta(days=1)).isoformat()
        if data_fim is None:
            data_fim = date.today().isoformat()
        
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.modo = modo
        self.notifier = NotificationService()
        
        logger.info(
            f"Processador inicializado: periodo={data_inicio} ate {data_fim}, modo={modo}"
        )
    
    def executar(self) -> dict:
        """
        Executa o processamento completo.
        
        Returns:
            dict: Resultado do processamento com métricas
        """
        logger.info("="*70)
        logger.info("INICIANDO PROCESSAMENTO DIÁRIO DE DIVERGÊNCIAS")
        logger.info("="*70)
        
        inicio_execucao = datetime.now()
        resultado = {
            'status': 'ERROR',
            'metricas': {},
            'erros': []
        }
        
        try:
            with db_connection() as conn:
                audit = AuditLogger(conn)
                processor = DivergenceProcessor(conn)
                
                # Inicia sessão de processamento
                sessao_id = audit.iniciar_sessao_processamento(
                    tipo_sessao='DAILY_AUTO' if self.modo == 'auto' else 'MANUAL_RUN',
                    parametros_execucao={
                        'data_inicio': self.data_inicio,
                        'data_fim': self.data_fim,
                        'modo': self.modo
                    }
                )
                
                logger.info(f"Sessao de processamento iniciada: ID={sessao_id}")
                
                # ETAPA 1: Detecção de divergências
                logger.info("-" * 70)
                logger.info("ETAPA 1: Detectando divergencias")
                logger.info("-" * 70)
                
                divergencias = processor.detectar_divergencias(
                    data_inicio=self.data_inicio,
                    data_fim=self.data_fim
                )
                
                total_divergencias = len(divergencias)
                divergencias_alta_confianca = len([
                    d for d in divergencias if d.confianca >= 0.95
                ])
                
                logger.info(f"Total de divergencias detectadas: {total_divergencias}")
                logger.info(f"Alta confianca (>=0.95): {divergencias_alta_confianca}")
                
                # Resumo por tipo
                tipos_count = {}
                for div in divergencias:
                    tipos_count[div.tipo] = tipos_count.get(div.tipo, 0) + 1
                
                logger.info("Divergencias por tipo:")
                for tipo, count in sorted(tipos_count.items()):
                    logger.info(f"  - {tipo}: {count}")
                
                # ETAPA 2: Aplicação de correções
                logger.info("-" * 70)
                logger.info("ETAPA 2: Aplicando correcoes")
                logger.info("-" * 70)
                
                resultado_correcoes = processor.aplicar_correcoes(
                    divergencias=divergencias,
                    modo=self.modo,
                    usuario='sistema_automatico'
                )
                
                logger.info(f"Correcoes automaticas aplicadas: {resultado_correcoes['corrigidas_automaticamente']}")
                logger.info(f"Pendentes de aprovacao: {resultado_correcoes['pendentes_aprovacao']}")
                logger.info(f"Erros: {resultado_correcoes['erros']}")
                
                # ETAPA 3: Geração de relatório
                logger.info("-" * 70)
                logger.info("ETAPA 3: Gerando relatorio")
                logger.info("-" * 70)
                
                relatorio_path = None
                if divergencias:
                    try:
                        datasets_dir = project_root / 'Datasets'
                        datasets_dir.mkdir(exist_ok=True)
                        
                        relatorio_path = processor.gerar_relatorio_divergencias(
                            divergencias=divergencias,
                            formato='csv',
                            caminho_saida=str(
                                datasets_dir / f'divergencias_{date.today()}.csv'
                            )
                        )
                        logger.info(f"Relatorio gerado: {relatorio_path}")
                    except Exception as e:
                        logger.error(f"Erro ao gerar relatorio: {e}")
                        resultado['erros'].append(f"Erro ao gerar relatorio: {str(e)}")
                
                # ETAPA 4: Envio de notificações
                logger.info("-" * 70)
                logger.info("ETAPA 4: Enviando notificacoes")
                logger.info("-" * 70)
                
                if total_divergencias > 0:
                    try:
                        sucesso_notificacao = self.notifier.enviar_alerta_divergencias(
                            total_divergencias=total_divergencias,
                            divergencias_criticas=divergencias_alta_confianca,
                            divergencias_pendentes=resultado_correcoes['pendentes_aprovacao'],
                            data_processamento=datetime.now().strftime('%d/%m/%Y %H:%M'),
                            relatorio_anexo=relatorio_path
                        )
                        
                        if sucesso_notificacao:
                            logger.info("Alerta de divergencias enviado com sucesso")
                        else:
                            logger.warning("Alerta nao enviado (SMTP nao configurado ou sem destinatarios)")
                            
                    except Exception as e:
                        logger.error(f"Erro ao enviar notificacao: {e}")
                        resultado['erros'].append(f"Erro ao enviar notificacao: {str(e)}")
                
                # Finaliza sessão
                fim_execucao = datetime.now()
                duracao = (fim_execucao - inicio_execucao).total_seconds()
                
                metricas = {
                    'total_registros_analisados': total_divergencias,
                    'divergencias_detectadas': total_divergencias,
                    'correcoes_aplicadas': resultado_correcoes['corrigidas_automaticamente'],
                    'correcoes_pendentes': resultado_correcoes['pendentes_aprovacao'],
                    'erros_encontrados': resultado_correcoes['erros']
                }
                
                status_final = (
                    'COMPLETED' if resultado_correcoes['erros'] == 0
                    else 'PARTIAL'
                )
                
                audit.finalizar_sessao_processamento(
                    sessao_id=sessao_id,
                    status=status_final,
                    metricas=metricas,
                    resultado_geral=(
                        f"Processamento concluido com sucesso. "
                        f"{resultado_correcoes['corrigidas_automaticamente']} correcoes aplicadas, "
                        f"{resultado_correcoes['pendentes_aprovacao']} pendentes."
                    )
                )
                
                # Prepara resultado final
                resultado = {
                    'status': status_final,
                    'sessao_id': sessao_id,
                    'periodo': {
                        'data_inicio': self.data_inicio,
                        'data_fim': self.data_fim
                    },
                    'duracao_segundos': int(duracao),
                    'metricas': metricas,
                    'resultado_correcoes': resultado_correcoes,
                    'relatorio_gerado': relatorio_path,
                    'erros': resultado['erros']
                }
                
                logger.info("="*70)
                logger.info(f"PROCESSAMENTO CONCLUÍDO - Status: {status_final}")
                logger.info(f"Duracao: {int(duracao)} segundos")
                logger.info("="*70)
                
                return resultado
                
        except Exception as e:
            logger.error(f"ERRO CRÍTICO no processamento: {e}", exc_info=True)
            
            # Tenta enviar alerta de falha crítica
            try:
                self.notifier.enviar_alerta_falha_critica(
                    componente='DailyProcessor',
                    erro_mensagem=str(e),
                    stack_trace=None
                )
            except:
                pass
            
            resultado['status'] = 'FAILED'
            resultado['erros'].append(str(e))
            return resultado


def main():
    """Função principal de execução do script."""
    parser = argparse.ArgumentParser(
        description='Processamento diário automatizado de divergências',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  Processar últimas 24 horas (modo automático):
    python daily_processor.py
  
  Processar período específico:
    python daily_processor.py --data-inicio 2025-08-01 --data-fim 2026-05-31
  
  Apenas detectar sem aplicar correções:
    python daily_processor.py --modo manual
  
  Reprocessar mês completo:
    python daily_processor.py --data-inicio 2025-12-01 --data-fim 2025-12-31
        """
    )
    
    parser.add_argument(
        '--data-inicio',
        type=str,
        help='Data início no formato YYYY-MM-DD (padrão: ontem)'
    )
    
    parser.add_argument(
        '--data-fim',
        type=str,
        help='Data fim no formato YYYY-MM-DD (padrão: hoje)'
    )
    
    parser.add_argument(
        '--modo',
        type=str,
        choices=['auto', 'manual'],
        default='auto',
        help='Modo de processamento: auto (aplica correções) ou manual (apenas detecta)'
    )
    
    args = parser.parse_args()
    
    # Executa processamento
    processor = DailyProcessor(
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        modo=args.modo
    )
    
    resultado = processor.executar()
    
    # Define código de saída
    exit_code = 0 if resultado['status'] in ['COMPLETED', 'PARTIAL'] else 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
