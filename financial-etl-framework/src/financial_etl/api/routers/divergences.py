"""
Router de Divergências

Endpoints para gestão de divergências detectadas pelo sistema.

Autor: Financial ETL Framework
Data: 2026-01-08
"""

from fastapi import APIRouter, HTTPException, Query, status, Body
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging

from ...conn import db_connection
from ...services import DivergenceProcessor, Divergencia

logger = logging.getLogger(__name__)

router = APIRouter()


class DivergenciaResponse(BaseModel):
    """Modelo de resposta para divergência."""
    id: int
    idnfsexterno: str
    tipo_divergencia: str
    campo_afetado: str
    valor_anterior: Optional[float]
    valor_sugerido: Optional[float]
    valor_aplicado: Optional[float] = None
    competencia: Optional[str]
    status_processamento: str
    confidence_score: Optional[float]
    detectado_em: datetime
    processado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AprovarCorrecaoRequest(BaseModel):
    """Modelo de requisição para aprovação de correção."""
    divergencia_ids: List[int] = Field(..., description="IDs das divergências a aprovar")
    usuario: str = Field(..., description="Identificador do usuário aprovando")
    aplicar_valor_sugerido: bool = Field(True, description="Se True, aplica valor sugerido")
    valor_customizado: Optional[float] = Field(None, description="Valor customizado (sobrescreve sugerido)")


class ProcessarDivergenciasRequest(BaseModel):
    """Modelo de requisição para processamento de divergências."""
    data_inicio: Optional[str] = Field(None, description="Data início no formato YYYY-MM-DD")
    data_fim: Optional[str] = Field(None, description="Data fim no formato YYYY-MM-DD")
    tipo_divergencia: Optional[str] = Field(None, description="Filtrar por tipo específico")
    modo: str = Field("manual", description="Modo de processamento: 'auto' ou 'manual'")
    usuario: str = Field("sistema", description="Usuário executando o processamento")


@router.get(
    "",
    response_model=List[DivergenciaResponse],
    summary="Listar divergências",
    description="Retorna lista de divergências detectadas com filtros opcionais"
)
async def listar_divergencias(
    status_processamento: Optional[str] = Query(
        None,
        description="Filtrar por status (DETECTED, APPROVED, REJECTED, AUTO_APPLIED)"
    ),
    tipo_divergencia: Optional[str] = Query(
        None,
        description="Filtrar por tipo de divergência"
    ),
    data_inicio: Optional[date] = Query(
        None,
        description="Data início (detectado_em >= data)"
    ),
    data_fim: Optional[date] = Query(
        None,
        description="Data fim (detectado_em <= data)"
    ),
    limit: int = Query(100, le=1000, description="Limite de resultados"),
    offset: int = Query(0, description="Offset para paginação")
):
    """
    Lista divergências com filtros e paginação.
    
    Útil para dashboards e interfaces de aprovação.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if status_processamento:
                conditions.append("status_processamento = %s")
                params.append(status_processamento)
            
            if tipo_divergencia:
                conditions.append("tipo_divergencia = %s")
                params.append(tipo_divergencia)
            
            if data_inicio:
                conditions.append("detectado_em >= %s")
                params.append(data_inicio)
            
            if data_fim:
                conditions.append("detectado_em <= %s")
                params.append(data_fim)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            params.extend([limit, offset])
            
            query = f"""
            SELECT 
                id, idnfsexterno, tipo_divergencia, campo_afetado,
                valor_anterior, valor_sugerido, valor_aplicado,
                competencia, status_processamento, confidence_score,
                detectado_em, processado_em
            FROM audit.divergencias_processadas
            WHERE {where_clause}
            ORDER BY detectado_em DESC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            divergencias = [
                DivergenciaResponse(
                    id=row[0],
                    idnfsexterno=row[1],
                    tipo_divergencia=row[2],
                    campo_afetado=row[3],
                    valor_anterior=float(row[4]) if row[4] else None,
                    valor_sugerido=float(row[5]) if row[5] else None,
                    valor_aplicado=float(row[6]) if row[6] else None,
                    competencia=row[7],
                    status_processamento=row[8],
                    confidence_score=float(row[9]) if row[9] else None,
                    detectado_em=row[10],
                    processado_em=row[11]
                )
                for row in rows
            ]
            
            return divergencias
            
    except Exception as e:
        logger.error(f"Erro ao listar divergencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{divergencia_id}",
    response_model=DivergenciaResponse,
    summary="Obter divergência específica",
    description="Retorna detalhes completos de uma divergência pelo ID"
)
async def obter_divergencia(divergencia_id: int):
    """Obtém detalhes de uma divergência específica."""
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                id, idnfsexterno, tipo_divergencia, campo_afetado,
                valor_anterior, valor_sugerido, valor_aplicado,
                competencia, status_processamento, confidence_score,
                detectado_em, processado_em
            FROM audit.divergencias_processadas
            WHERE id = %s
            """
            
            cursor.execute(query, (divergencia_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Divergencia {divergencia_id} nao encontrada"
                )
            
            return DivergenciaResponse(
                id=row[0],
                idnfsexterno=row[1],
                tipo_divergencia=row[2],
                campo_afetado=row[3],
                valor_anterior=float(row[4]) if row[4] else None,
                valor_sugerido=float(row[5]) if row[5] else None,
                valor_aplicado=float(row[6]) if row[6] else None,
                competencia=row[7],
                status_processamento=row[8],
                confidence_score=float(row[9]) if row[9] else None,
                detectado_em=row[10],
                processado_em=row[11]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter divergencia {divergencia_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/processar",
    summary="Processar divergências",
    description="Detecta e processa divergências no período especificado"
)
async def processar_divergencias(request: ProcessarDivergenciasRequest):
    """
    Executa detecção e processamento de divergências.
    
    Pode ser usado para:
    - Processamento manual ad-hoc
    - Reprocessamento de períodos específicos
    - Detecção sem aplicação automática
    """
    try:
        with db_connection() as conn:
            processor = DivergenceProcessor(conn)
            
            # Detecta divergências
            divergencias = processor.detectar_divergencias(
                data_inicio=request.data_inicio,
                data_fim=request.data_fim,
                tipo_divergencia=request.tipo_divergencia
            )
            
            # Aplica correções se solicitado
            resultado = processor.aplicar_correcoes(
                divergencias=divergencias,
                modo=request.modo,
                usuario=request.usuario
            )
            
            return {
                "status": "completed",
                "periodo": {
                    "data_inicio": request.data_inicio,
                    "data_fim": request.data_fim
                },
                "modo_processamento": request.modo,
                "resultado": resultado,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao processar divergencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/aprovar",
    summary="Aprovar correções",
    description="Aprova e aplica correções para divergências selecionadas"
)
async def aprovar_correcoes(request: AprovarCorrecaoRequest):
    """
    Aprova e aplica correções para divergências pendentes.
    
    Permite aprovação em lote e customização de valores.
    """
    try:
        with db_connection() as conn:
            from ...services import AuditLogger
            audit = AuditLogger(conn)
            cursor = conn.cursor()
            
            resultados = []
            
            for div_id in request.divergencia_ids:
                try:
                    # Obtém dados da divergência
                    cursor.execute(
                        """
                        SELECT idnfsexterno, tipo_divergencia, campo_afetado,
                               valor_sugerido
                        FROM audit.divergencias_processadas
                        WHERE id = %s AND status_processamento = 'DETECTED'
                        """,
                        (div_id,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        resultados.append({
                            "divergencia_id": div_id,
                            "status": "erro",
                            "mensagem": "Divergencia nao encontrada ou ja processada"
                        })
                        continue
                    
                    idnfsexterno, tipo_div, campo, valor_sugerido = row
                    
                    # Define valor a aplicar
                    valor_aplicar = (
                        request.valor_customizado
                        if request.valor_customizado is not None
                        else valor_sugerido
                    )
                    
                    # Inicia operação auditada
                    op_id = audit.iniciar_operacao(
                        tipo_operacao='UPDATE',
                        descricao=f'Aprovacao manual: {tipo_div}',
                        usuario=request.usuario,
                        origem='API',
                        tabela_afetada='byd.controladoria'
                    )
                    
                    # Aplica correção
                    cursor.execute(
                        f"""
                        UPDATE byd.controladoria
                        SET {campo} = %s
                        WHERE idnfsexterno = %s
                        """,
                        (valor_aplicar, idnfsexterno)
                    )
                    
                    # Atualiza status da divergência
                    audit.atualizar_status_divergencia(
                        divergencia_id=div_id,
                        novo_status='APPROVED',
                        valor_aplicado=valor_aplicar,
                        processado_por=request.usuario
                    )
                    
                    audit.finalizar_operacao(op_id, status='SUCCESS')
                    
                    resultados.append({
                        "divergencia_id": div_id,
                        "status": "aprovado",
                        "valor_aplicado": valor_aplicar
                    })
                    
                except Exception as e:
                    logger.error(f"Erro ao aprovar divergencia {div_id}: {e}")
                    resultados.append({
                        "divergencia_id": div_id,
                        "status": "erro",
                        "mensagem": str(e)
                    })
            
            conn.commit()
            
            return {
                "total_processado": len(request.divergencia_ids),
                "aprovados": len([r for r in resultados if r["status"] == "aprovado"]),
                "erros": len([r for r in resultados if r["status"] == "erro"]),
                "detalhes": resultados,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao aprovar correcoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{divergencia_id}/rejeitar",
    summary="Rejeitar divergência",
    description="Marca uma divergência como rejeitada com motivo"
)
async def rejeitar_divergencia(
    divergencia_id: int,
    motivo: str = Body(..., embed=True),
    usuario: str = Body(..., embed=True)
):
    """
    Rejeita uma divergência, registrando o motivo.
    """
    try:
        with db_connection() as conn:
            from ...services import AuditLogger
            audit = AuditLogger(conn)
            
            audit.atualizar_status_divergencia(
                divergencia_id=divergencia_id,
                novo_status='REJECTED',
                processado_por=usuario,
                motivo_rejeicao=motivo
            )
            
            return {
                "divergencia_id": divergencia_id,
                "status": "rejeitado",
                "motivo": motivo,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao rejeitar divergencia {divergencia_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
