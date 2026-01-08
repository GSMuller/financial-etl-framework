"""
Router de Relatórios

Endpoints para geração de relatórios e exportação de dados.

Autor: Financial ETL Framework
Data: 2026-01-08
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date
import logging
import io
import pandas as pd

from ...conn import db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/divergencias/export",
    summary="Exportar divergências",
    description="Exporta divergências para CSV ou Excel"
)
async def exportar_divergencias(
    formato: str = Query("csv", regex="^(csv|excel)$"),
    status_processamento: Optional[str] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None)
):
    """
    Exporta relatório de divergências no formato especificado.
    """
    try:
        with db_connection() as conn:
            conditions = []
            params = []
            
            if status_processamento:
                conditions.append("status_processamento = %s")
                params.append(status_processamento)
            
            if data_inicio:
                conditions.append("detectado_em >= %s")
                params.append(data_inicio)
            
            if data_fim:
                conditions.append("detectado_em <= %s")
                params.append(data_fim)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
            SELECT 
                idnfsexterno,
                tipo_divergencia,
                campo_afetado,
                valor_anterior,
                valor_sugerido,
                valor_aplicado,
                competencia,
                status_processamento,
                confidence_score,
                detectado_em,
                processado_em,
                processado_por,
                motivo_rejeicao
            FROM audit.divergencias_processadas
            WHERE {where_clause}
            ORDER BY detectado_em DESC
            """
            
            df = pd.read_sql_query(query, conn, params=params)
            
            # Formata datas
            for col in ['detectado_em', 'processado_em']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Gera arquivo
            output = io.BytesIO()
            
            if formato == "csv":
                df.to_csv(output, index=False, encoding='utf-8-sig')
                media_type = "text/csv"
                filename = f"divergencias_{date.today().isoformat()}.csv"
            else:  # excel
                df.to_excel(output, index=False, engine='openpyxl')
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                filename = f"divergencias_{date.today().isoformat()}.xlsx"
            
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        logger.error(f"Erro ao exportar divergencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/metricas/performance",
    summary="Métricas de performance",
    description="Retorna métricas de performance do sistema"
)
async def obter_metricas_performance(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None)
):
    """
    Métricas detalhadas de performance e volumetria.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            date_condition = ""
            params = []
            if data_inicio and data_fim:
                date_condition = "WHERE timestamp_inicio BETWEEN %s AND %s"
                params = [data_inicio, data_fim]
            
            # Tempo médio por tipo de operação
            query_performance = f"""
            SELECT 
                tipo_operacao,
                COUNT(*) as total_operacoes,
                AVG(duracao_segundos) as duracao_media,
                MIN(duracao_segundos) as duracao_minima,
                MAX(duracao_segundos) as duracao_maxima,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duracao_segundos) as mediana,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duracao_segundos) as p95
            FROM audit.operacoes
            {date_condition}
            GROUP BY tipo_operacao
            """
            
            cursor.execute(query_performance, params)
            performance_rows = cursor.fetchall()
            
            performance_por_tipo = [
                {
                    "tipo_operacao": row[0],
                    "total_operacoes": row[1],
                    "duracao_media_seg": round(float(row[2]), 3) if row[2] else 0,
                    "duracao_minima_seg": round(float(row[3]), 3) if row[3] else 0,
                    "duracao_maxima_seg": round(float(row[4]), 3) if row[4] else 0,
                    "mediana_seg": round(float(row[5]), 3) if row[5] else 0,
                    "percentil_95_seg": round(float(row[6]), 3) if row[6] else 0
                }
                for row in performance_rows
            ]
            
            # Taxa de sucesso
            query_sucesso = f"""
            SELECT 
                tipo_operacao,
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as sucessos,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as falhas
            FROM audit.operacoes
            {date_condition}
            GROUP BY tipo_operacao
            """
            
            cursor.execute(query_sucesso, params)
            sucesso_rows = cursor.fetchall()
            
            taxa_sucesso_por_tipo = [
                {
                    "tipo_operacao": row[0],
                    "total": row[1],
                    "sucessos": row[2],
                    "falhas": row[3],
                    "taxa_sucesso_percentual": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in sucesso_rows
            ]
            
            return {
                "periodo": {
                    "data_inicio": data_inicio.isoformat() if data_inicio else None,
                    "data_fim": data_fim.isoformat() if data_fim else None
                },
                "performance_por_tipo": performance_por_tipo,
                "taxa_sucesso_por_tipo": taxa_sucesso_por_tipo
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter metricas performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
