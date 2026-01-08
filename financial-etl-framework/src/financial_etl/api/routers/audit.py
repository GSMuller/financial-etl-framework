"""
Router de Auditoria

Endpoints para consulta de histórico e rastreabilidade de operações.

Autor: Financial ETL Framework
Data: 2026-01-08
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
import logging

from ...conn import db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


class OperacaoResponse(BaseModel):
    """Modelo de resposta para operação de auditoria."""
    id: int
    tipo_operacao: str
    descricao: str
    usuario: str
    origem: str
    tabela_afetada: Optional[str]
    registros_afetados: int
    timestamp_inicio: datetime
    timestamp_fim: Optional[datetime]
    duracao_segundos: Optional[float]
    status: str


@router.get(
    "/operacoes",
    response_model=List[OperacaoResponse],
    summary="Listar operações",
    description="Retorna histórico de operações executadas no sistema"
)
async def listar_operacoes(
    usuario: Optional[str] = Query(None, description="Filtrar por usuário"),
    tabela: Optional[str] = Query(None, description="Filtrar por tabela afetada"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    data_inicio: Optional[date] = Query(None, description="Data início"),
    data_fim: Optional[date] = Query(None, description="Data fim"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0)
):
    """
    Lista histórico de operações com filtros.
    
    Útil para auditoria e rastreamento de ações no sistema.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if usuario:
                conditions.append("usuario = %s")
                params.append(usuario)
            
            if tabela:
                conditions.append("tabela_afetada = %s")
                params.append(tabela)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            if data_inicio:
                conditions.append("timestamp_inicio >= %s")
                params.append(data_inicio)
            
            if data_fim:
                conditions.append("timestamp_inicio <= %s")
                params.append(data_fim)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            params.extend([limit, offset])
            
            query = f"""
            SELECT 
                id, tipo_operacao, descricao, usuario, origem,
                tabela_afetada, registros_afetados, timestamp_inicio,
                timestamp_fim, duracao_segundos, status
            FROM audit.operacoes
            WHERE {where_clause}
            ORDER BY timestamp_inicio DESC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            operacoes = [
                OperacaoResponse(
                    id=row[0],
                    tipo_operacao=row[1],
                    descricao=row[2],
                    usuario=row[3],
                    origem=row[4],
                    tabela_afetada=row[5],
                    registros_afetados=row[6],
                    timestamp_inicio=row[7],
                    timestamp_fim=row[8],
                    duracao_segundos=float(row[9]) if row[9] else None,
                    status=row[10]
                )
                for row in rows
            ]
            
            return operacoes
            
    except Exception as e:
        logger.error(f"Erro ao listar operacoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/sessoes",
    summary="Listar sessões de processamento",
    description="Retorna histórico de execuções do processamento automatizado"
)
async def listar_sessoes(
    tipo_sessao: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500)
):
    """
    Lista sessões de processamento diário e manual.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if tipo_sessao:
                conditions.append("tipo_sessao = %s")
                params.append(tipo_sessao)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            params.append(limit)
            
            query = f"""
            SELECT 
                id, tipo_sessao, inicio_processamento, fim_processamento,
                duracao_total_segundos, status, total_registros_analisados,
                divergencias_detectadas, correcoes_aplicadas,
                correcoes_pendentes, erros_encontrados, resultado_geral
            FROM audit.sessoes_processamento
            WHERE {where_clause}
            ORDER BY inicio_processamento DESC
            LIMIT %s
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            sessoes = [
                {
                    "id": row[0],
                    "tipo_sessao": row[1],
                    "inicio_processamento": row[2].isoformat() if row[2] else None,
                    "fim_processamento": row[3].isoformat() if row[3] else None,
                    "duracao_total_segundos": row[4],
                    "status": row[5],
                    "metricas": {
                        "total_registros_analisados": row[6],
                        "divergencias_detectadas": row[7],
                        "correcoes_aplicadas": row[8],
                        "correcoes_pendentes": row[9],
                        "erros_encontrados": row[10]
                    },
                    "resultado_geral": row[11]
                }
                for row in rows
            ]
            
            return sessoes
            
    except Exception as e:
        logger.error(f"Erro ao listar sessoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
