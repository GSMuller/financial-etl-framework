"""
API REST - Financial ETL Framework

FastAPI application para interface web com o sistema de processamento
de divergências e auditoria.

Fornece endpoints para:
- Consulta de divergências e histórico
- Aprovação de correções
- Métricas e dashboards
- Integração com Looker Studio
- Gestão de auditoria

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, date
import logging

from ..conn import db_connection
from ..services import AuditLogger, DivergenceProcessor, NotificationService
from .routers import divergences, audit, reports

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="Financial ETL API",
    description=(
        "API REST para gestão de divergências e auditoria do Data Warehouse BYD. "
        "Fornece endpoints para detecção automática, correção assistida e "
        "rastreabilidade completa de operações."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuração CORS para permitir acesso do Looker Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lookerstudio.google.com",
        "http://localhost:3000",  # Para desenvolvimento local
        "*"  # Remover em produção, especificar domínios permitidos
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Inclui routers das diferentes seções
app.include_router(
    divergences.router,
    prefix="/api/v1/divergencias",
    tags=["Divergências"]
)
app.include_router(
    audit.router,
    prefix="/api/v1/auditoria",
    tags=["Auditoria"]
)
app.include_router(
    reports.router,
    prefix="/api/v1/relatorios",
    tags=["Relatórios"]
)


@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raiz - verificação de saúde da API.
    
    Returns:
        Informações básicas sobre a API e status operacional
    """
    return {
        "service": "Financial ETL API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/api/docs"
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Verificação de saúde da API e conexão com banco de dados.
    
    Returns:
        Status de cada componente do sistema
    """
    status_checks = {
        "api": "healthy",
        "database": "unknown",
        "timestamp": datetime.now().isoformat()
    }
    
    # Testa conexão com banco de dados
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            status_checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status_checks["database"] = "unhealthy"
        status_checks["database_error"] = str(e)
    
    # Determina status geral
    overall_status = (
        "healthy" if status_checks["database"] == "healthy"
        else "degraded"
    )
    status_checks["status"] = overall_status
    
    return status_checks


@app.get("/api/v1/metricas/resumo", tags=["Métricas"])
async def obter_metricas_resumo(
    data_inicio: Optional[date] = Query(None, description="Data início filtro"),
    data_fim: Optional[date] = Query(None, description="Data fim filtro")
):
    """
    Retorna métricas resumidas do sistema para dashboards.
    
    Endpoint otimizado para integração com Looker Studio e outras
    ferramentas de BI.
    
    Query Parameters:
        data_inicio: Filtrar métricas a partir desta data
        data_fim: Filtrar métricas até esta data
    
    Returns:
        Dicionário com métricas agregadas:
        - total_divergencias
        - divergencias_por_tipo
        - taxa_resolucao
        - tempo_medio_resolucao
        - operacoes_por_status
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            
            # Condição de filtro por data
            date_condition = ""
            params = []
            if data_inicio and data_fim:
                date_condition = "WHERE detectado_em BETWEEN %s AND %s"
                params = [data_inicio, data_fim]
            
            # Divergências por tipo
            query_tipos = f"""
            SELECT 
                tipo_divergencia,
                COUNT(*) as total,
                COUNT(CASE WHEN status_processamento = 'AUTO_APPLIED' THEN 1 END) as resolvidas
            FROM audit.divergencias_processadas
            {date_condition}
            GROUP BY tipo_divergencia
            """
            cursor.execute(query_tipos, params)
            divergencias_por_tipo = [
                {
                    "tipo": row[0],
                    "total": row[1],
                    "resolvidas": row[2],
                    "taxa_resolucao": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in cursor.fetchall()
            ]
            
            # Métricas gerais
            query_geral = f"""
            SELECT 
                COUNT(*) as total,
                AVG(EXTRACT(DAY FROM processado_em - detectado_em)) as tempo_medio_dias,
                COUNT(CASE WHEN status_processamento IN ('AUTO_APPLIED', 'APPROVED') THEN 1 END) as resolvidas
            FROM audit.divergencias_processadas
            {date_condition}
            """
            cursor.execute(query_geral, params)
            row = cursor.fetchone()
            
            total_divergencias = row[0]
            tempo_medio_dias = float(row[1]) if row[1] else 0.0
            total_resolvidas = row[2]
            
            taxa_resolucao = (
                round((total_resolvidas / total_divergencias * 100), 2)
                if total_divergencias > 0 else 0.0
            )
            
            # Operações por status
            query_operacoes = f"""
            SELECT 
                status,
                COUNT(*) as total
            FROM audit.operacoes
            {date_condition.replace('detectado_em', 'timestamp_inicio')}
            GROUP BY status
            """
            cursor.execute(query_operacoes, params)
            operacoes_por_status = [
                {"status": row[0], "total": row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                "periodo": {
                    "data_inicio": data_inicio.isoformat() if data_inicio else None,
                    "data_fim": data_fim.isoformat() if data_fim else None
                },
                "metricas_gerais": {
                    "total_divergencias": total_divergencias,
                    "total_resolvidas": total_resolvidas,
                    "taxa_resolucao_percentual": taxa_resolucao,
                    "tempo_medio_resolucao_dias": round(tempo_medio_dias, 1)
                },
                "divergencias_por_tipo": divergencias_por_tipo,
                "operacoes_por_status": operacoes_por_status,
                "timestamp_consulta": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter metricas resumo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar metricas: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas.
    """
    logger.error(f"Erro nao tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
