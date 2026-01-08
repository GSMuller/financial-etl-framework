"""
Script de Relatorio Resumido de Divergencias
Execucao manual para visualizacao rapida do status.

Uso:
    python relatorio_divergencias.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.financial_etl.conn import get_connection


def limpar_tela():
    """Limpa a tela do terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_cabecalho():
    """Exibe cabecalho do relatorio."""
    print("\n" + "="*70)
    print("RELATORIO DE DIVERGENCIAS - BONUS VIEW")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70 + "\n")


def analisar_pendentes_verificacao(cursor):
    """Analisa pendentes de verificacao e retorna metricas."""
    query = """
    SELECT 
        COUNT(*) as total,
        MIN(dta_processamento) as mais_antigo,
        MAX(dta_processamento) as mais_recente
    FROM byd.bonus_view
    WHERE bonus_utilizado = 'PENDENTE VERIFICACAO'
        AND dta_processamento BETWEEN '2025-08-01' AND '2026-12-31'
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    total = row[0] if row[0] else 0
    mais_antigo = row[1]
    mais_recente = row[2]
    
    # Define criticidade
    if total < 10:
        criticidade = "BAIXA"
        icone = "✓"
        acao = "Situacao controlada"
    elif total <= 20:
        criticidade = "ATENCAO"
        icone = "⚠"
        acao = "Monitorar volume"
    else:
        criticidade = "CRITICA"
        icone = "✖"
        acao = "Ajustar Chassis pendentes de verificacao!"
    
    return {
        'total': total,
        'mais_antigo': mais_antigo,
        'mais_recente': mais_recente,
        'criticidade': criticidade,
        'icone': icone,
        'acao': acao
    }


def analisar_divergencias_valor(cursor):
    """Analisa divergencias de valor (Revisar Divergencia!)."""
    query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT competencia) as competencias_afetadas
    FROM byd.bonus_view
    WHERE dta_processamento BETWEEN '2025-08-01' AND '2026-05-30'
        AND apontamento = 'Revisar Divergência!'
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    total = row[0] if row[0] else 0
    competencias = row[1] if row[1] else 0
    
    return {
        'total': total,
        'competencias_afetadas': competencias
    }


def analisar_trade_marketing(cursor):
    """Analisa divergencias de Trade Marketing."""
    query = """
    SELECT COUNT(*) 
    FROM byd.bonus_view
    WHERE (
        ABS(COALESCE(CAST(bonus_dpto AS NUMERIC), 0) - COALESCE(CAST(bonus AS NUMERIC), 0)) > 0.01
        OR ABS(COALESCE(CAST(trade_mkt_dpto AS NUMERIC), 0) - COALESCE(CAST(trade AS NUMERIC), 0)) > 0.01
    )
    AND dta_processamento BETWEEN '2025-08-01' AND '2026-12-31'
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    return row[0] if row[0] else 0


def exibir_relatorio():
    """Funcao principal do relatorio."""
    limpar_tela()
    exibir_cabecalho()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Pendentes de Verificacao
        pendentes = analisar_pendentes_verificacao(cursor)
        print("1. PENDENTES DE VERIFICACAO")
        print("-" * 70)
        print(f"   Total de Chassis:      {pendentes['total']}")
        print(f"   Criticidade:           {pendentes['icone']} {pendentes['criticidade']}")
        print(f"   Acao:                  {pendentes['acao']}")
        if pendentes['mais_antigo']:
            print(f"   Mais antigo:           {pendentes['mais_antigo'].strftime('%d/%m/%Y')}")
        if pendentes['mais_recente']:
            print(f"   Mais recente:          {pendentes['mais_recente'].strftime('%d/%m/%Y')}")
        print()
        
        # 2. Divergencias de Valor
        divergencias = analisar_divergencias_valor(cursor)
        print("2. DIVERGENCIAS DE VALOR (Revisar Divergencia!)")
        print("-" * 70)
        print(f"   Total de Registros:    {divergencias['total']}")
        print(f"   Competencias Afetadas: {divergencias['competencias_afetadas']}")
        print()
        
        # 3. Trade Marketing
        trade_mkt = analisar_trade_marketing(cursor)
        print("3. DIVERGENCIAS TRADE MARKETING")
        print("-" * 70)
        print(f"   Total de Registros:    {trade_mkt}")
        print()
        
        # Resumo Final
        print("="*70)
        print("RESUMO GERAL")
        print("="*70)
        total_geral = pendentes['total'] + divergencias['total'] + trade_mkt
        print(f"Total de Divergencias: {total_geral}")
        print()
        
        if pendentes['criticidade'] == 'CRITICA' or divergencias['total'] > 50:
            print("⚠ ATENCAO: Acoes corretivas necessarias!")
        elif pendentes['criticidade'] == 'ATENCAO' or divergencias['total'] > 20:
            print("⚠ Monitoramento recomendado")
        else:
            print("✓ Situacao sob controle")
        
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✖ ERRO ao gerar relatorio: {e}\n")
        print("Verificacoes:")
        print("  1. Arquivo .env configurado?")
        print("  2. PostgreSQL rodando?")
        print("  3. Credenciais corretas?")
        print()
        sys.exit(1)


if __name__ == '__main__':
    exibir_relatorio()
