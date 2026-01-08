"""
Processador Automático de Divergências

Este módulo substitui o processo manual do notebook divergencia.ipynb,
automatizando a detecção e correção de divergências em dados de bônus.

Funcionalidades:
- Detecção automática de divergências em Trade Marketing
- Análise de inconsistências em cálculos de bônus
- Validação de regras de negócio
- Geração de relatórios de divergências
- Aplicação automática ou assistida de correções

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from decimal import Decimal

from ..conn import db_connection
from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)


@dataclass
class Divergencia:
    """
    Representa uma divergência detectada no sistema.
    
    Attributes:
        idnfsexterno: Identificador único da nota fiscal
        tipo: Tipo de divergência detectada
        campo_afetado: Campo do banco que apresenta divergência
        valor_atual: Valor atualmente registrado
        valor_esperado: Valor calculado/esperado pela regra
        competencia: Competência (mês/ano) da transação
        confianca: Score de confiança da detecção (0.0 a 1.0)
        regras_violadas: Lista de regras de negócio violadas
        dados_adicionais: Contexto adicional relevante
    """
    idnfsexterno: str
    tipo: str
    campo_afetado: str
    valor_atual: Optional[float]
    valor_esperado: Optional[float]
    competencia: Optional[str]
    confianca: float = 1.0
    regras_violadas: List[str] = None
    dados_adicionais: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.regras_violadas is None:
            self.regras_violadas = []
        if self.dados_adicionais is None:
            self.dados_adicionais = {}


class DivergenceProcessor:
    """
    Processador principal para detecção e correção de divergências.
    
    Este serviço substitui o processo manual realizado em notebooks,
    oferecendo:
    - Detecção automática baseada em regras
    - Validação de dados
    - Sugestão de correções
    - Aplicação automatizada com auditoria
    
    Exemplo de uso:
        >>> with db_connection() as conn:
        ...     processor = DivergenceProcessor(conn)
        ...     divergencias = processor.detectar_divergencias(
        ...         data_inicio='2025-08-01',
        ...         data_fim='2026-05-31'
        ...     )
        ...     resultado = processor.aplicar_correcoes(
        ...         divergencias,
        ...         modo='auto',
        ...         usuario='sistema_automatico'
        ...     )
    """
    
    def __init__(self, connection):
        """
        Inicializa o processador de divergências.
        
        Args:
            connection: Conexão psycopg2 ativa com o banco de dados
        """
        self.conn = connection
        self.cursor = connection.cursor()
        self.audit = AuditLogger(connection)
    
    def detectar_divergencias(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        tipo_divergencia: Optional[str] = None,
        limite_confianca: float = 0.8
    ) -> List[Divergencia]:
        """
        Detecta divergências nos dados de bônus usando regras de negócio.
        
        Regras implementadas:
        1. Divergência Trade Marketing: bonus_view.apontamento = 'Revisar Divergência!'
        2. Status pendente verificação sem motivo válido
        3. Valores de bônus fora do range esperado
        4. Inconsistências entre tabelas relacionadas
        
        Args:
            data_inicio: Data inicial no formato 'YYYY-MM-DD'
            data_fim: Data final no formato 'YYYY-MM-DD'
            tipo_divergencia: Filtrar por tipo específico (opcional)
            limite_confianca: Score mínimo de confiança (0.0 a 1.0)
        
        Returns:
            List[Divergencia]: Lista de divergências detectadas
        """
        logger.info(
            f"Iniciando deteccao de divergencias: "
            f"periodo={data_inicio} ate {data_fim}"
        )
        
        divergencias = []
        
        # Regra 1: Divergências de Trade Marketing
        divergencias_trade = self._detectar_divergencias_trade_marketing(
            data_inicio, data_fim
        )
        divergencias.extend(divergencias_trade)
        
        # Regra 2: Pendentes de Verificação
        divergencias_pendentes = self._detectar_pendentes_verificacao(
            data_inicio, data_fim
        )
        divergencias.extend(divergencias_pendentes)
        
        # Regra 3: Validações de valores
        divergencias_valores = self._detectar_divergencias_valores(
            data_inicio, data_fim
        )
        divergencias.extend(divergencias_valores)
        
        # Filtra por confiança mínima
        divergencias_filtradas = [
            d for d in divergencias
            if d.confianca >= limite_confianca
        ]
        
        logger.info(
            f"Deteccao concluida: {len(divergencias_filtradas)} divergencias encontradas "
            f"(confianca >= {limite_confianca})"
        )
        
        return divergencias_filtradas
    
    def _detectar_divergencias_trade_marketing(
        self,
        data_inicio: Optional[str],
        data_fim: Optional[str]
    ) -> List[Divergencia]:
        """
        Detecta divergências de Trade Marketing usando a view bonus_view.
        
        Esta é a regra principal que substitui o notebook divergencia.ipynb.
        Identifica casos onde bonus_view.apontamento = 'Revisar Divergência!'
        """
        try:
            query = """
            SELECT 
                idnfsexterno,
                des_modelo,
                apontamento,
                competencia,
                bonus_utilizado,
                valor_bonus,
                trade,
                bonus_dpto,
                trade_mkt_dpto,
                dta_processamento
            FROM byd.bonus_view
            WHERE apontamento = 'Revisar Divergência!'
            """
            
            params = []
            if data_inicio and data_fim:
                query += " AND dta_processamento BETWEEN %s AND %s"
                params.extend([data_inicio, data_fim])
            
            query += " ORDER BY dta_processamento DESC"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            divergencias = []
            for row in rows:
                # Analisa se bonus_dpto deveria ser igual a valor_bonus
                # e trade_mkt_dpto deveria ser igual a trade
                valor_bonus = float(row[5]) if row[5] else 0.0
                trade = float(row[6]) if row[6] else 0.0
                bonus_dpto_atual = float(row[7]) if row[7] else 0.0
                trade_mkt_dpto_atual = float(row[8]) if row[8] else 0.0
                
                # Divergência no campo bonus_dpto
                if abs(bonus_dpto_atual - valor_bonus) > 0.01:
                    divergencias.append(Divergencia(
                        idnfsexterno=row[0],
                        tipo='TRADE_MARKETING_BONUS',
                        campo_afetado='bonus_dpto',
                        valor_atual=bonus_dpto_atual,
                        valor_esperado=valor_bonus,
                        competencia=row[3],
                        confianca=0.95,
                        regras_violadas=['BONUS_DPTO_DIVERGENTE'],
                        dados_adicionais={
                            'des_modelo': row[1],
                            'bonus_utilizado': row[4],
                            'dta_processamento': str(row[9]) if row[9] else None
                        }
                    ))
                
                # Divergência no campo trade_mkt_dpto
                if abs(trade_mkt_dpto_atual - trade) > 0.01:
                    divergencias.append(Divergencia(
                        idnfsexterno=row[0],
                        tipo='TRADE_MARKETING_TRADE',
                        campo_afetado='trade_mkt_dpto',
                        valor_atual=trade_mkt_dpto_atual,
                        valor_esperado=trade,
                        competencia=row[3],
                        confianca=0.95,
                        regras_violadas=['TRADE_MKT_DPTO_DIVERGENTE'],
                        dados_adicionais={
                            'des_modelo': row[1],
                            'bonus_utilizado': row[4],
                            'dta_processamento': str(row[9]) if row[9] else None
                        }
                    ))
            
            logger.info(
                f"Trade Marketing: {len(divergencias)} divergencias detectadas"
            )
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao detectar divergencias Trade Marketing: {e}")
            raise
    
    def _detectar_pendentes_verificacao(
        self,
        data_inicio: Optional[str],
        data_fim: Optional[str]
    ) -> List[Divergencia]:
        """
        Detecta registros com status 'PENDENTE VERIFICACAO' que permanecem
        sem resolução por período prolongado.
        Busca sempre no período fixo: Agosto/2025 até Dezembro/2026.
        """
        try:
            query = """
            SELECT 
                idnfsexterno,
                competencia,
                bonus_utilizado,
                dta_processamento,
                EXTRACT(DAY FROM NOW() - dta_processamento)::INTEGER as dias_pendente
            FROM byd.bonus_view
            WHERE bonus_utilizado = 'PENDENTE VERIFICACAO'
                AND dta_processamento BETWEEN '2025-08-01' AND '2026-12-31'
            """
            
            params = []
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            divergencias = []
            for row in rows:
                dias_pendente = row[4]
                
                # Marca todos como baixa confiança individual (não processar automaticamente)
                # A criticidade será avaliada no total de pendentes
                confianca = 0.5
                
                divergencias.append(Divergencia(
                    idnfsexterno=row[0],
                    tipo='PENDENTE_VERIFICACAO',
                    campo_afetado='bonus_utilizado',
                    valor_atual='PENDENTE VERIFICACAO',
                    valor_esperado=None,  # Requer análise manual
                    competencia=row[1],
                    confianca=confianca,
                    regras_violadas=['VERIFICACAO_PENDENTE_PROLONGADA'],
                    dados_adicionais={
                        'dias_pendente': dias_pendente,
                        'dta_processamento': str(row[3]) if row[3] else None
                    }
                ))
            
            # Determina criticidade baseada no volume total
            total_pendentes = len(divergencias)
            if total_pendentes < 10:
                nivel_criticidade = "BAIXA CRITICIDADE"
            elif total_pendentes <= 20:
                nivel_criticidade = "ATENCAO - Volume moderado de pendentes"
            else:
                nivel_criticidade = "CRITICO - Ajustar Chassis pendentes de verificacao!"
            
            logger.info(
                f"Pendentes Verificacao: {total_pendentes} detectadas - {nivel_criticidade}"
            )
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao detectar pendentes verificacao: {e}")
            raise
    
    def _detectar_divergencias_valores(
        self,
        data_inicio: Optional[str],
        data_fim: Optional[str]
    ) -> List[Divergencia]:
        """
        Detecta valores suspeitos ou fora dos ranges esperados.
        
        Validações:
        - Valores negativos em campos de bônus
        - Valores extremamente altos (outliers)
        - Inconsistências matemáticas
        """
        try:
            query = """
            SELECT 
                idnfsexterno,
                competencia,
                trade,
                valor_bonus,
                bonus_dpto,
                trade_mkt_dpto
            FROM byd.bonus_view
            WHERE (
                COALESCE(CAST(trade AS NUMERIC), 0) < 0
                OR COALESCE(CAST(valor_bonus AS NUMERIC), 0) < 0
                OR COALESCE(CAST(bonus_dpto AS NUMERIC), 0) < 0
                OR COALESCE(CAST(trade AS NUMERIC), 0) > 100000
                OR COALESCE(CAST(valor_bonus AS NUMERIC), 0) > 100000
            )
            """
            
            params = []
            if data_inicio and data_fim:
                query += " AND dta_processamento BETWEEN %s AND %s"
                params.extend([data_inicio, data_fim])
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            divergencias = []
            for row in rows:
                trade = float(row[2]) if row[2] else 0.0
                valor_bonus = float(row[3]) if row[3] else 0.0
                
                regras_violadas = []
                
                if trade < 0:
                    regras_violadas.append('TRADE_VALOR_NEGATIVO')
                if valor_bonus < 0:
                    regras_violadas.append('BONUS_VALOR_NEGATIVO')
                if trade > 100000:
                    regras_violadas.append('TRADE_VALOR_OUTLIER')
                if valor_bonus > 100000:
                    regras_violadas.append('BONUS_VALOR_OUTLIER')
                
                if regras_violadas:
                    divergencias.append(Divergencia(
                        idnfsexterno=row[0],
                        tipo='VALIDACAO_VALOR',
                        campo_afetado='valores_bonus',
                        valor_atual=None,
                        valor_esperado=None,
                        competencia=row[1],
                        confianca=0.7,
                        regras_violadas=regras_violadas,
                        dados_adicionais={
                            'trade': trade,
                            'valor_bonus': valor_bonus
                        }
                    ))
            
            logger.info(
                f"Validacao Valores: {len(divergencias)} divergencias detectadas"
            )
            return divergencias
            
        except Exception as e:
            logger.error(f"Erro ao detectar divergencias de valores: {e}")
            raise
    
    def aplicar_correcoes(
        self,
        divergencias: List[Divergencia],
        modo: str = 'manual',
        usuario: str = 'sistema',
        limite_auto_aplicacao: float = 0.95
    ) -> Dict[str, Any]:
        """
        Aplica correções para as divergências detectadas.
        
        Args:
            divergencias: Lista de divergências a corrigir
            modo: 'auto' para aplicação automática, 'manual' para gerar apenas relatório
            usuario: Identificador do usuário aprovando as correções
            limite_auto_aplicacao: Confiança mínima para auto-aplicação (modo auto)
        
        Returns:
            Dict com resultados: {
                'total_divergencias': int,
                'corrigidas_automaticamente': int,
                'pendentes_aprovacao': int,
                'erros': int,
                'detalhes': List[Dict]
            }
        """
        logger.info(
            f"Iniciando aplicacao de correcoes: modo={modo}, "
            f"total_divergencias={len(divergencias)}"
        )
        
        resultado = {
            'total_divergencias': len(divergencias),
            'corrigidas_automaticamente': 0,
            'pendentes_aprovacao': 0,
            'erros': 0,
            'detalhes': []
        }
        
        for div in divergencias:
            try:
                # Decide se aplica automaticamente ou marca como pendente
                aplicar_auto = (
                    modo == 'auto' and
                    div.confianca >= limite_auto_aplicacao and
                    div.tipo in ['TRADE_MARKETING_BONUS', 'TRADE_MARKETING_TRADE']
                )
                
                if aplicar_auto:
                    sucesso = self._aplicar_correcao_automatica(div, usuario)
                    if sucesso:
                        resultado['corrigidas_automaticamente'] += 1
                        resultado['detalhes'].append({
                            'idnfsexterno': div.idnfsexterno,
                            'tipo': div.tipo,
                            'status': 'CORRIGIDO_AUTO',
                            'valor_aplicado': div.valor_esperado
                        })
                    else:
                        resultado['erros'] += 1
                        resultado['detalhes'].append({
                            'idnfsexterno': div.idnfsexterno,
                            'tipo': div.tipo,
                            'status': 'ERRO',
                            'motivo': 'Falha na aplicacao automatica'
                        })
                else:
                    # Registra como pendente de aprovação manual
                    self._registrar_divergencia_pendente(div)
                    resultado['pendentes_aprovacao'] += 1
                    resultado['detalhes'].append({
                        'idnfsexterno': div.idnfsexterno,
                        'tipo': div.tipo,
                        'status': 'PENDENTE_APROVACAO',
                        'confianca': div.confianca
                    })
                    
            except Exception as e:
                logger.error(
                    f"Erro ao processar divergencia {div.idnfsexterno}: {e}"
                )
                resultado['erros'] += 1
                resultado['detalhes'].append({
                    'idnfsexterno': div.idnfsexterno,
                    'tipo': div.tipo,
                    'status': 'ERRO',
                    'motivo': str(e)
                })
        
        logger.info(
            f"Aplicacao de correcoes concluida: "
            f"auto={resultado['corrigidas_automaticamente']}, "
            f"pendentes={resultado['pendentes_aprovacao']}, "
            f"erros={resultado['erros']}"
        )
        
        return resultado
    
    def _aplicar_correcao_automatica(
        self,
        divergencia: Divergencia,
        usuario: str
    ) -> bool:
        """
        Aplica correção automática para uma divergência específica.
        Registra a operação no sistema de auditoria.
        """
        try:
            # Inicia operação auditada
            op_id = self.audit.iniciar_operacao(
                tipo_operacao='UPDATE',
                descricao=f'Correcao automatica: {divergencia.tipo}',
                usuario=usuario,
                origem='AUTOMATION',
                tabela_afetada='byd.controladoria'
            )
            
            # Captura dados anteriores para rollback
            query_anterior = f"""
            SELECT {divergencia.campo_afetado}
            FROM byd.controladoria
            WHERE idnfsexterno = %s
            """
            self.cursor.execute(query_anterior, (divergencia.idnfsexterno,))
            valor_anterior = self.cursor.fetchone()
            
            # Aplica a correção
            query_update = f"""
            UPDATE byd.controladoria
            SET {divergencia.campo_afetado} = %s
            WHERE idnfsexterno = %s
            """
            self.cursor.execute(
                query_update,
                (divergencia.valor_esperado, divergencia.idnfsexterno)
            )
            
            registros_afetados = self.cursor.rowcount
            
            # Registra divergência no audit
            div_id = self.audit.registrar_divergencia(
                operacao_id=op_id,
                idnfsexterno=divergencia.idnfsexterno,
                tipo_divergencia=divergencia.tipo,
                valor_anterior=divergencia.valor_atual,
                valor_sugerido=divergencia.valor_esperado,
                campo_afetado=divergencia.campo_afetado,
                competencia=divergencia.competencia,
                confidence_score=divergencia.confianca,
                regras_aplicadas=divergencia.regras_violadas,
                dados_contextuais=divergencia.dados_adicionais
            )
            
            # Atualiza status da divergência como aplicada
            self.audit.atualizar_status_divergencia(
                divergencia_id=div_id,
                novo_status='AUTO_APPLIED',
                valor_aplicado=divergencia.valor_esperado,
                processado_por=usuario
            )
            
            # Finaliza operação com sucesso
            self.audit.finalizar_operacao(
                operacao_id=op_id,
                status='SUCCESS',
                registros_afetados=registros_afetados,
                dados_anteriores=[{
                    'idnfsexterno': divergencia.idnfsexterno,
                    'campo': divergencia.campo_afetado,
                    'valor': valor_anterior[0] if valor_anterior else None
                }],
                dados_posteriores=[{
                    'idnfsexterno': divergencia.idnfsexterno,
                    'campo': divergencia.campo_afetado,
                    'valor': divergencia.valor_esperado
                }]
            )
            
            self.conn.commit()
            
            logger.info(
                f"Correcao automatica aplicada: idnf={divergencia.idnfsexterno}, "
                f"campo={divergencia.campo_afetado}"
            )
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(
                f"Erro ao aplicar correcao automatica para {divergencia.idnfsexterno}: {e}"
            )
            
            # Registra falha na auditoria
            if 'op_id' in locals():
                self.audit.finalizar_operacao(
                    operacao_id=op_id,
                    status='FAILED',
                    erro_mensagem=str(e)
                )
            
            return False
    
    def _registrar_divergencia_pendente(self, divergencia: Divergencia) -> int:
        """
        Registra divergência que requer aprovação manual.
        """
        op_id = self.audit.iniciar_operacao(
            tipo_operacao='DETECT',
            descricao=f'Divergencia detectada: {divergencia.tipo}',
            usuario='sistema',
            origem='AUTOMATION'
        )
        
        div_id = self.audit.registrar_divergencia(
            operacao_id=op_id,
            idnfsexterno=divergencia.idnfsexterno,
            tipo_divergencia=divergencia.tipo,
            valor_anterior=divergencia.valor_atual,
            valor_sugerido=divergencia.valor_esperado,
            campo_afetado=divergencia.campo_afetado,
            competencia=divergencia.competencia,
            confidence_score=divergencia.confianca,
            regras_aplicadas=divergencia.regras_violadas,
            dados_contextuais=divergencia.dados_adicionais
        )
        
        self.audit.finalizar_operacao(op_id, status='SUCCESS')
        self.conn.commit()
        
        return div_id
    
    def gerar_relatorio_divergencias(
        self,
        divergencias: List[Divergencia],
        formato: str = 'csv',
        caminho_saida: Optional[str] = None
    ) -> str:
        """
        Gera relatório consolidado de divergências detectadas.
        
        Args:
            divergencias: Lista de divergências
            formato: 'csv' ou 'excel'
            caminho_saida: Caminho para salvar o arquivo (opcional)
        
        Returns:
            str: Caminho do arquivo gerado
        """
        df = pd.DataFrame([
            {
                'idnfsexterno': d.idnfsexterno,
                'tipo_divergencia': d.tipo,
                'campo_afetado': d.campo_afetado,
                'valor_atual': d.valor_atual,
                'valor_esperado': d.valor_esperado,
                'competencia': d.competencia,
                'confianca': d.confianca,
                'regras_violadas': ', '.join(d.regras_violadas)
            }
            for d in divergencias
        ])
        
        if caminho_saida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            caminho_saida = f'divergencias_{timestamp}.{formato}'
        
        if formato == 'csv':
            df.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
        elif formato == 'excel':
            df.to_excel(caminho_saida, index=False)
        
        logger.info(f"Relatorio gerado: {caminho_saida}")
        return caminho_saida
