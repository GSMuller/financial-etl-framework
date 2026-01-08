"""
Módulo de Auditoria e Logging de Operações

Este módulo implementa o sistema de auditoria completo, registrando
todas as operações realizadas no Data Warehouse para fins de:
- Rastreabilidade e compliance
- Rollback de operações
- Análise de performance
- Monitoramento de processos automatizados

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Sistema de auditoria para registro de operações no Data Warehouse.
    
    Responsável por:
    - Registrar operações de INSERT, UPDATE, DELETE
    - Capturar dados anteriores e posteriores para rollback
    - Calcular métricas de performance
    - Facilitar rastreamento de alterações
    
    Exemplos de uso:
        >>> audit = AuditLogger(connection)
        >>> op_id = audit.iniciar_operacao(
        ...     tipo='UPDATE',
        ...     descricao='Correção de divergências Trade Marketing',
        ...     usuario='giovanni.5683',
        ...     origem='AUTOMATION'
        ... )
        >>> # ... executa operações ...
        >>> audit.finalizar_operacao(op_id, status='SUCCESS')
    """
    
    def __init__(self, connection):
        """
        Inicializa o sistema de auditoria.
        
        Args:
            connection: Conexão psycopg2 ativa com o banco de dados
        """
        self.conn = connection
        self.cursor = connection.cursor()
    
    def iniciar_operacao(
        self,
        tipo_operacao: str,
        descricao: str,
        usuario: str,
        origem: str,
        tabela_afetada: Optional[str] = None,
        filtros_aplicados: Optional[Dict[str, Any]] = None,
        query_executada: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Inicia registro de uma nova operação no sistema de auditoria.
        
        Args:
            tipo_operacao: Tipo da operação (INSERT, UPDATE, DELETE, BULK_UPDATE, etc)
            descricao: Descrição detalhada da operação sendo realizada
            usuario: Identificador do usuário ou sistema executando
            origem: Origem da operação (MANUAL, API, AUTOMATION, NOTEBOOK)
            tabela_afetada: Nome da tabela sendo modificada (schema.table)
            filtros_aplicados: Dicionário com filtros WHERE aplicados
            query_executada: Query SQL completa executada
            metadata: Metadados adicionais relevantes ao contexto
        
        Returns:
            int: ID da operação criada na tabela audit.operacoes
        
        Raises:
            psycopg2.Error: Se houver erro ao registrar a operação
        """
        try:
            query = """
            INSERT INTO audit.operacoes (
                tipo_operacao, descricao, usuario, origem,
                tabela_afetada, filtros_aplicados, query_executada,
                timestamp_inicio, status, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, NOW(), 'PENDING', %s
            ) RETURNING id
            """
            
            self.cursor.execute(query, (
                tipo_operacao,
                descricao,
                usuario,
                origem,
                tabela_afetada,
                Json(filtros_aplicados) if filtros_aplicados else None,
                query_executada,
                Json(metadata) if metadata else None
            ))
            
            operacao_id = self.cursor.fetchone()[0]
            self.conn.commit()
            
            logger.info(f"Operacao iniciada: ID={operacao_id}, tipo={tipo_operacao}")
            return operacao_id
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao iniciar operacao de auditoria: {e}")
            self.conn.rollback()
            raise
    
    def finalizar_operacao(
        self,
        operacao_id: int,
        status: str,
        registros_afetados: int = 0,
        dados_anteriores: Optional[List[Dict]] = None,
        dados_posteriores: Optional[List[Dict]] = None,
        erro_mensagem: Optional[str] = None
    ) -> None:
        """
        Finaliza registro de operação, calculando duração e armazenando resultados.
        
        Args:
            operacao_id: ID da operação retornado por iniciar_operacao()
            status: Status final (SUCCESS, FAILED, ROLLED_BACK)
            registros_afetados: Quantidade de registros modificados
            dados_anteriores: Lista com estado anterior dos dados (para rollback)
            dados_posteriores: Lista com estado posterior dos dados
            erro_mensagem: Mensagem de erro se status = FAILED
        
        Raises:
            psycopg2.Error: Se houver erro ao finalizar a operação
        """
        try:
            query = """
            UPDATE audit.operacoes
            SET 
                timestamp_fim = NOW(),
                duracao_segundos = EXTRACT(EPOCH FROM (NOW() - timestamp_inicio)),
                status = %s,
                registros_afetados = %s,
                dados_anteriores = %s,
                dados_posteriores = %s,
                erro_mensagem = %s
            WHERE id = %s
            """
            
            self.cursor.execute(query, (
                status,
                registros_afetados,
                Json(dados_anteriores) if dados_anteriores else None,
                Json(dados_posteriores) if dados_posteriores else None,
                erro_mensagem,
                operacao_id
            ))
            
            self.conn.commit()
            
            logger.info(
                f"Operacao finalizada: ID={operacao_id}, status={status}, "
                f"registros={registros_afetados}"
            )
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao finalizar operacao {operacao_id}: {e}")
            self.conn.rollback()
            raise
    
    @contextmanager
    def operacao_auditada(
        self,
        tipo_operacao: str,
        descricao: str,
        usuario: str,
        origem: str,
        **kwargs
    ):
        """
        Context manager para operações auditadas automaticamente.
        
        Garante que a operação seja iniciada, executada e finalizada
        corretamente, mesmo em caso de exceções.
        
        Args:
            tipo_operacao: Tipo da operação (INSERT, UPDATE, DELETE, etc)
            descricao: Descrição da operação
            usuario: Usuário executando
            origem: Origem da operação
            **kwargs: Argumentos adicionais para iniciar_operacao()
        
        Yields:
            int: ID da operação criada
        
        Exemplo:
            >>> with audit.operacao_auditada('UPDATE', 'Corrigir bonus', 'user', 'API') as op_id:
            ...     cursor.execute("UPDATE byd.controladoria SET ...")
            ...     registros = cursor.rowcount
            ...     yield registros  # Retorna qtd de registros afetados
        """
        operacao_id = self.iniciar_operacao(
            tipo_operacao, descricao, usuario, origem, **kwargs
        )
        
        try:
            yield operacao_id
            self.finalizar_operacao(operacao_id, status='SUCCESS')
            
        except Exception as e:
            erro_msg = f"{type(e).__name__}: {str(e)}"
            self.finalizar_operacao(
                operacao_id,
                status='FAILED',
                erro_mensagem=erro_msg
            )
            logger.error(f"Operacao {operacao_id} falhou: {erro_msg}")
            raise
    
    def registrar_divergencia(
        self,
        operacao_id: int,
        idnfsexterno: str,
        tipo_divergencia: str,
        valor_anterior: Optional[float],
        valor_sugerido: Optional[float],
        campo_afetado: str,
        competencia: Optional[str] = None,
        confidence_score: Optional[float] = None,
        regras_aplicadas: Optional[List[str]] = None,
        dados_contextuais: Optional[Dict] = None
    ) -> int:
        """
        Registra uma divergência detectada no sistema.
        
        Args:
            operacao_id: ID da operação que detectou a divergência
            idnfsexterno: Identificador da nota fiscal
            tipo_divergencia: Tipo (TRADE_MARKETING, BONUS_CALCULATION, etc)
            valor_anterior: Valor atual no banco
            valor_sugerido: Valor sugerido pela correção
            campo_afetado: Nome do campo com divergência
            competencia: Competência no formato YYYY-MM
            confidence_score: Score de confiança (0.0 a 1.0)
            regras_aplicadas: Lista de regras que detectaram a divergência
            dados_contextuais: Dados adicionais relevantes
        
        Returns:
            int: ID da divergência registrada
        """
        try:
            query = """
            INSERT INTO audit.divergencias_processadas (
                operacao_id, idnfsexterno, tipo_divergencia,
                valor_anterior, valor_sugerido, campo_afetado,
                competencia, status_processamento, detectado_em,
                confidence_score, regras_aplicadas, dados_contextuais
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, 'DETECTED', NOW(), %s, %s, %s
            ) RETURNING id
            """
            
            self.cursor.execute(query, (
                operacao_id,
                idnfsexterno,
                tipo_divergencia,
                valor_anterior,
                valor_sugerido,
                campo_afetado,
                competencia,
                confidence_score,
                regras_aplicadas,
                Json(dados_contextuais) if dados_contextuais else None
            ))
            
            divergencia_id = self.cursor.fetchone()[0]
            self.conn.commit()
            
            logger.info(
                f"Divergencia registrada: ID={divergencia_id}, "
                f"tipo={tipo_divergencia}, idnf={idnfsexterno}"
            )
            
            return divergencia_id
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao registrar divergencia: {e}")
            self.conn.rollback()
            raise
    
    def atualizar_status_divergencia(
        self,
        divergencia_id: int,
        novo_status: str,
        valor_aplicado: Optional[float] = None,
        processado_por: Optional[str] = None,
        motivo_rejeicao: Optional[str] = None
    ) -> None:
        """
        Atualiza o status de processamento de uma divergência.
        
        Args:
            divergencia_id: ID da divergência a ser atualizada
            novo_status: Novo status (APPROVED, REJECTED, AUTO_APPLIED)
            valor_aplicado: Valor efetivamente aplicado (pode diferir do sugerido)
            processado_por: Identificador de quem processou
            motivo_rejeicao: Motivo da rejeição (se aplicável)
        """
        try:
            query = """
            UPDATE audit.divergencias_processadas
            SET 
                status_processamento = %s,
                valor_aplicado = %s,
                processado_em = NOW(),
                processado_por = %s,
                motivo_rejeicao = %s
            WHERE id = %s
            """
            
            self.cursor.execute(query, (
                novo_status,
                valor_aplicado,
                processado_por,
                motivo_rejeicao,
                divergencia_id
            ))
            
            self.conn.commit()
            
            logger.info(
                f"Status divergencia atualizado: ID={divergencia_id}, "
                f"status={novo_status}"
            )
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao atualizar divergencia {divergencia_id}: {e}")
            self.conn.rollback()
            raise
    
    def iniciar_sessao_processamento(
        self,
        tipo_sessao: str,
        parametros_execucao: Optional[Dict] = None,
        ambiente: str = 'PRODUCTION'
    ) -> int:
        """
        Inicia uma nova sessão de processamento automatizado.
        
        Args:
            tipo_sessao: Tipo (DAILY_AUTO, MANUAL_RUN, REPROCESSING)
            parametros_execucao: Parâmetros utilizados na execução
            ambiente: Ambiente de execução (PRODUCTION, STAGING, DEVELOPMENT)
        
        Returns:
            int: ID da sessão criada
        """
        try:
            query = """
            INSERT INTO audit.sessoes_processamento (
                tipo_sessao, inicio_processamento, status,
                parametros_execucao, ambiente
            ) VALUES (
                %s, NOW(), 'RUNNING', %s, %s
            ) RETURNING id
            """
            
            self.cursor.execute(query, (
                tipo_sessao,
                Json(parametros_execucao) if parametros_execucao else None,
                ambiente
            ))
            
            sessao_id = self.cursor.fetchone()[0]
            self.conn.commit()
            
            logger.info(f"Sessao de processamento iniciada: ID={sessao_id}")
            return sessao_id
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao iniciar sessao: {e}")
            self.conn.rollback()
            raise
    
    def finalizar_sessao_processamento(
        self,
        sessao_id: int,
        status: str,
        metricas: Dict[str, int],
        resultado_geral: Optional[str] = None,
        log_completo: Optional[str] = None
    ) -> None:
        """
        Finaliza uma sessão de processamento com métricas e resultados.
        
        Args:
            sessao_id: ID da sessão
            status: Status final (COMPLETED, FAILED, PARTIAL)
            metricas: Dicionário com métricas da sessão
            resultado_geral: Resumo textual do resultado
            log_completo: Log completo da execução
        """
        try:
            query = """
            UPDATE audit.sessoes_processamento
            SET 
                fim_processamento = NOW(),
                duracao_total_segundos = EXTRACT(EPOCH FROM (NOW() - inicio_processamento))::INTEGER,
                status = %s,
                total_registros_analisados = %s,
                divergencias_detectadas = %s,
                correcoes_aplicadas = %s,
                correcoes_pendentes = %s,
                erros_encontrados = %s,
                resultado_geral = %s,
                log_completo = %s
            WHERE id = %s
            """
            
            self.cursor.execute(query, (
                status,
                metricas.get('total_registros_analisados', 0),
                metricas.get('divergencias_detectadas', 0),
                metricas.get('correcoes_aplicadas', 0),
                metricas.get('correcoes_pendentes', 0),
                metricas.get('erros_encontrados', 0),
                resultado_geral,
                log_completo,
                sessao_id
            ))
            
            self.conn.commit()
            
            logger.info(f"Sessao finalizada: ID={sessao_id}, status={status}")
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao finalizar sessao {sessao_id}: {e}")
            self.conn.rollback()
            raise
    
    def obter_operacoes_para_rollback(
        self,
        operacao_id: int
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados necessários para realizar rollback de uma operação.
        
        Args:
            operacao_id: ID da operação a ser revertida
        
        Returns:
            List[Dict]: Lista com dados anteriores para rollback
        """
        try:
            query = """
            SELECT 
                id, tipo_operacao, tabela_afetada,
                dados_anteriores, registros_afetados
            FROM audit.operacoes
            WHERE id = %s
            """
            
            self.cursor.execute(query, (operacao_id,))
            row = self.cursor.fetchone()
            
            if not row:
                raise ValueError(f"Operacao {operacao_id} nao encontrada")
            
            return {
                'id': row[0],
                'tipo_operacao': row[1],
                'tabela_afetada': row[2],
                'dados_anteriores': row[3],
                'registros_afetados': row[4]
            }
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter dados para rollback: {e}")
            raise
    
    def obter_historico_operacoes(
        self,
        usuario: Optional[str] = None,
        tabela: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Consulta histórico de operações com filtros opcionais.
        
        Args:
            usuario: Filtrar por usuário específico
            tabela: Filtrar por tabela afetada
            data_inicio: Data inicial do período
            data_fim: Data final do período
            limit: Limite de registros retornados
        
        Returns:
            List[Dict]: Lista com operações encontradas
        """
        try:
            conditions = []
            params = []
            
            if usuario:
                conditions.append("usuario = %s")
                params.append(usuario)
            
            if tabela:
                conditions.append("tabela_afetada = %s")
                params.append(tabela)
            
            if data_inicio:
                conditions.append("timestamp_inicio >= %s")
                params.append(data_inicio)
            
            if data_fim:
                conditions.append("timestamp_inicio <= %s")
                params.append(data_fim)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            params.append(limit)
            
            query = f"""
            SELECT 
                id, tipo_operacao, descricao, usuario, origem,
                tabela_afetada, registros_afetados, timestamp_inicio,
                timestamp_fim, status
            FROM audit.operacoes
            WHERE {where_clause}
            ORDER BY timestamp_inicio DESC
            LIMIT %s
            """
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            return [
                {
                    'id': row[0],
                    'tipo_operacao': row[1],
                    'descricao': row[2],
                    'usuario': row[3],
                    'origem': row[4],
                    'tabela_afetada': row[5],
                    'registros_afetados': row[6],
                    'timestamp_inicio': row[7],
                    'timestamp_fim': row[8],
                    'status': row[9]
                }
                for row in rows
            ]
            
        except psycopg2.Error as e:
            logger.error(f"Erro ao obter historico: {e}")
            raise
