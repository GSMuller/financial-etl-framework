"""
Script para consultar registros pendentes de verificação.
Exporta resultados para CSV ou retorna DataFrame.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from conn import db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def consultar_pendentes_verificacao(ano=None, exportar_csv=False):
    """
    Consulta registros com status PENDENTE VERIFICACAO.
    
    Args:
        ano (int, optional): Ano para filtrar. Default: ano atual.
        exportar_csv (bool): Se True, exporta para CSV.
    
    Returns:
        pd.DataFrame: DataFrame com os resultados.
    """
    if ano is None:
        ano = datetime.now().year
    
    query = """
    SELECT * 
    FROM byd.bonus_view
    WHERE dta_processamento BETWEEN %s AND %s
        AND bonus_utilizado = 'PENDENTE VERIFICACAO'
    ORDER BY dta_processamento DESC
    """
    
    try:
        with db_connection() as conn:
            data_inicio = f'{ano}-01-01'
            data_fim = f'{ano}-12-31'
            
            logger.info(f"Consultando pendentes de verificação: {ano}")
            df = pd.read_sql_query(query, conn, params=(data_inicio, data_fim))
            
            logger.info(f"Total de registros encontrados: {len(df)}")
            
            if exportar_csv and not df.empty:
                output_path = Path(__file__).parent.parent / 'Datasets' / f'pendentes_verificacao_{ano}.csv'
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                logger.info(f"Arquivo exportado: {output_path}")
            
            return df
            
    except Exception as e:
        logger.error(f"Erro ao consultar pendentes: {e}")
        raise


def main():
    """Execução principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Consulta pendentes de verificação')
    parser.add_argument('--ano', type=int, help='Ano para filtrar (default: ano atual)')
    parser.add_argument('--csv', action='store_true', help='Exportar para CSV')
    
    args = parser.parse_args()
    
    df = consultar_pendentes_verificacao(ano=args.ano, exportar_csv=args.csv)
    
    if not df.empty:
        print(f"\n{'='*60}")
        print(f"REGISTROS PENDENTES DE VERIFICAÇÃO")
        print(f"{'='*60}\n")
        print(df.head(10))
        print(f"\nTotal: {len(df)} registros")
    else:
        print("Nenhum registro pendente encontrado.")


if __name__ == '__main__':
    main()
