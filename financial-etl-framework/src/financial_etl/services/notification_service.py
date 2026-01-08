"""
Serviço de Notificações

Sistema de alertas e notificações para eventos críticos do Data Warehouse.
Suporta múltiplos canais: email, logs e extensível para Slack/Teams.

Funcionalidades:
- Envio de alertas sobre divergências detectadas
- Notificações de falhas em processos automatizados
- Resumos diários de processamento
- Alertas de thresholds excedidos

Autor: Financial ETL Framework
Data: 2026-01-08
Versão: 1.0.0
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Serviço centralizado de notificações e alertas.
    
    Gerencia envio de alertas através de diferentes canais,
    com templates formatados e suporte a anexos.
    
    Configuração via variáveis de ambiente:
        SMTP_HOST: Servidor SMTP
        SMTP_PORT: Porta SMTP (default: 587)
        SMTP_USER: Usuário para autenticação
        SMTP_PASSWORD: Senha do usuário
        SMTP_FROM: Email remetente
        NOTIFICATION_RECIPIENTS: Lista de destinatários (separados por vírgula)
    
    Exemplo de uso:
        >>> notifier = NotificationService()
        >>> notifier.enviar_alerta_divergencias(
        ...     total=15,
        ...     criticas=3,
        ...     destinatarios=['controller@empresa.com']
        ... )
    """
    
    def __init__(self):
        """Inicializa o serviço de notificações com configurações do ambiente."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        
        # Destinatários padrão (pode ser sobrescrito por notificação)
        recipients_env = os.getenv('NOTIFICATION_RECIPIENTS', '')
        self.default_recipients = [
            r.strip() for r in recipients_env.split(',') if r.strip()
        ]
        
        self.smtp_enabled = bool(self.smtp_user and self.smtp_password)
        
        if not self.smtp_enabled:
            logger.warning(
                "SMTP nao configurado. Notificacoes via email desabilitadas. "
                "Configure SMTP_USER e SMTP_PASSWORD no arquivo .env"
            )
    
    def enviar_email(
        self,
        destinatarios: List[str],
        assunto: str,
        corpo_html: str,
        corpo_texto: Optional[str] = None,
        anexos: Optional[List[str]] = None
    ) -> bool:
        """
        Envia email formatado com suporte a HTML e anexos.
        
        Args:
            destinatarios: Lista de endereços de email
            assunto: Assunto do email
            corpo_html: Corpo do email em HTML
            corpo_texto: Corpo alternativo em texto puro (opcional)
            anexos: Lista de caminhos de arquivos para anexar (opcional)
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        if not self.smtp_enabled:
            logger.warning("Email nao enviado: SMTP nao configurado")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Adiciona corpo texto plano (fallback)
            if corpo_texto:
                part_texto = MIMEText(corpo_texto, 'plain', 'utf-8')
                msg.attach(part_texto)
            
            # Adiciona corpo HTML
            part_html = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(part_html)
            
            # Adiciona anexos se fornecidos
            if anexos:
                for caminho_arquivo in anexos:
                    if Path(caminho_arquivo).exists():
                        with open(caminho_arquivo, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={Path(caminho_arquivo).name}'
                            )
                            msg.attach(part)
            
            # Envia email via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(
                f"Email enviado com sucesso: assunto='{assunto}', "
                f"destinatarios={len(destinatarios)}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def enviar_alerta_divergencias(
        self,
        total_divergencias: int,
        divergencias_criticas: int,
        divergencias_pendentes: int,
        data_processamento: Optional[str] = None,
        relatorio_anexo: Optional[str] = None,
        destinatarios: Optional[List[str]] = None
    ) -> bool:
        """
        Envia alerta sobre divergências detectadas no processamento.
        
        Args:
            total_divergencias: Total de divergências encontradas
            divergencias_criticas: Quantidade com alta confiança
            divergencias_pendentes: Quantidade aguardando aprovação
            data_processamento: Data/hora do processamento
            relatorio_anexo: Caminho para arquivo CSV/Excel de detalhamento
            destinatarios: Lista de emails (usa padrão se None)
        
        Returns:
            bool: True se alerta enviado com sucesso
        """
        if destinatarios is None:
            destinatarios = self.default_recipients
        
        if not destinatarios:
            logger.warning("Sem destinatarios configurados para alerta")
            return False
        
        data_proc = data_processamento or datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Define nível de severidade
        if divergencias_criticas > 10:
            severidade = 'CRÍTICO'
            cor_severidade = '#dc3545'  # vermelho
        elif divergencias_criticas > 5:
            severidade = 'ATENÇÃO'
            cor_severidade = '#fd7e14'  # laranja
        else:
            severidade = 'INFORMATIVO'
            cor_severidade = '#0d6efd'  # azul
        
        assunto = f'[{severidade}] Divergências Detectadas - {total_divergencias} registros'
        
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background-color: {cor_severidade}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 5px 5px 0 0; 
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border: 1px solid #dee2e6; 
                }}
                .metric {{ 
                    background-color: white; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-left: 4px solid {cor_severidade}; 
                }}
                .metric-title {{ font-weight: bold; color: #6c757d; }}
                .metric-value {{ font-size: 24px; color: {cor_severidade}; font-weight: bold; }}
                .footer {{ 
                    margin-top: 20px; 
                    padding: 15px; 
                    background-color: #e9ecef; 
                    font-size: 12px; 
                    color: #6c757d; 
                }}
                .action-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 15px 0;
                    background-color: {cor_severidade};
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Alerta de Divergências - Data Warehouse BYD</h2>
                </div>
                <div class="content">
                    <p><strong>Data do Processamento:</strong> {data_proc}</p>
                    <p><strong>Nível de Severidade:</strong> {severidade}</p>
                    
                    <div class="metric">
                        <div class="metric-title">Total de Divergências Detectadas</div>
                        <div class="metric-value">{total_divergencias}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-title">Divergências Críticas (alta confiança)</div>
                        <div class="metric-value">{divergencias_criticas}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-title">Pendentes de Aprovação</div>
                        <div class="metric-value">{divergencias_pendentes}</div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <strong>Ação Necessária:</strong><br>
                        Revisar as divergências detectadas e aprovar as correções sugeridas 
                        através da interface de gestão ou via API.
                    </p>
                    
                    {'<p>Relatório detalhado anexado a este email.</p>' if relatorio_anexo else ''}
                </div>
                <div class="footer">
                    <p>
                        Este é um alerta automático gerado pelo Financial ETL Framework.<br>
                        Sistema de Auditoria e Processamento de Divergências v1.0.0
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        corpo_texto = f"""
        ALERTA DE DIVERGÊNCIAS - DATA WAREHOUSE BYD
        
        Data do Processamento: {data_proc}
        Nível de Severidade: {severidade}
        
        MÉTRICAS:
        - Total de Divergências: {total_divergencias}
        - Divergências Críticas: {divergencias_criticas}
        - Pendentes de Aprovação: {divergencias_pendentes}
        
        AÇÃO NECESSÁRIA:
        Revisar divergências detectadas e aprovar correções sugeridas.
        
        ---
        Financial ETL Framework - Sistema de Auditoria v1.0.0
        """
        
        anexos = [relatorio_anexo] if relatorio_anexo else None
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto,
            anexos=anexos
        )
    
    def enviar_resumo_processamento(
        self,
        sessao_id: int,
        status: str,
        metricas: Dict[str, Any],
        duracao_segundos: int,
        erros: Optional[List[str]] = None,
        destinatarios: Optional[List[str]] = None
    ) -> bool:
        """
        Envia resumo de execução do processamento diário.
        
        Args:
            sessao_id: ID da sessão de processamento
            status: Status final (COMPLETED, FAILED, PARTIAL)
            metricas: Dicionário com métricas do processamento
            duracao_segundos: Tempo total de execução
            erros: Lista de erros encontrados (se houver)
            destinatarios: Lista de emails (usa padrão se None)
        
        Returns:
            bool: True se enviado com sucesso
        """
        if destinatarios is None:
            destinatarios = self.default_recipients
        
        if not destinatarios:
            return False
        
        # Define cor baseada no status
        cor_status = {
            'COMPLETED': '#28a745',  # verde
            'FAILED': '#dc3545',     # vermelho
            'PARTIAL': '#ffc107'     # amarelo
        }.get(status, '#6c757d')
        
        # Formata duração
        minutos = duracao_segundos // 60
        segundos = duracao_segundos % 60
        duracao_fmt = f"{minutos}min {segundos}s"
        
        assunto = f'[{status}] Resumo Processamento Diário - Sessão #{sessao_id}'
        
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background-color: {cor_status}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 5px 5px 0 0; 
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border: 1px solid #dee2e6; 
                }}
                .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
                .metric {{ 
                    background-color: white; 
                    padding: 15px; 
                    text-align: center; 
                    border-radius: 5px; 
                }}
                .metric-value {{ font-size: 28px; font-weight: bold; color: {cor_status}; }}
                .metric-label {{ font-size: 12px; color: #6c757d; margin-top: 5px; }}
                .error-section {{ 
                    background-color: #fff3cd; 
                    border: 1px solid #ffc107; 
                    padding: 15px; 
                    margin: 15px 0; 
                    border-radius: 5px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Resumo de Processamento Diário</h2>
                    <p>Sessão #{sessao_id} - Status: {status}</p>
                </div>
                <div class="content">
                    <p><strong>Duração Total:</strong> {duracao_fmt}</p>
                    <p><strong>Data/Hora Conclusão:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    
                    <h3>Métricas do Processamento</h3>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-value">{metricas.get('total_registros_analisados', 0)}</div>
                            <div class="metric-label">Registros Analisados</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{metricas.get('divergencias_detectadas', 0)}</div>
                            <div class="metric-label">Divergências Detectadas</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{metricas.get('correcoes_aplicadas', 0)}</div>
                            <div class="metric-label">Correções Aplicadas</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{metricas.get('correcoes_pendentes', 0)}</div>
                            <div class="metric-label">Pendentes Aprovação</div>
                        </div>
                    </div>
                    
                    {f'''
                    <div class="error-section">
                        <h4>Erros Encontrados ({len(erros)})</h4>
                        <ul>
                            {"".join(f"<li>{erro}</li>" for erro in erros[:10])}
                        </ul>
                        {f"<p><em>... e mais {len(erros)-10} erros</em></p>" if len(erros) > 10 else ""}
                    </div>
                    ''' if erros else ''}
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=f"Processamento Sessao #{sessao_id}: {status}"
        )
    
    def enviar_alerta_falha_critica(
        self,
        componente: str,
        erro_mensagem: str,
        stack_trace: Optional[str] = None,
        destinatarios: Optional[List[str]] = None
    ) -> bool:
        """
        Envia alerta de falha crítica que requer atenção imediata.
        
        Args:
            componente: Nome do componente que falhou
            erro_mensagem: Mensagem de erro
            stack_trace: Stack trace completo (opcional)
            destinatarios: Lista de emails (usa padrão se None)
        
        Returns:
            bool: True se enviado com sucesso
        """
        if destinatarios is None:
            destinatarios = self.default_recipients
        
        if not destinatarios:
            return False
        
        assunto = f'[CRÍTICO] Falha no Sistema - {componente}'
        
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #dc3545; color: white; padding: 15px;">
                <h2>ALERTA CRÍTICO - Falha no Sistema</h2>
            </div>
            <div style="padding: 20px; background-color: #f8f9fa;">
                <p><strong>Componente:</strong> {componente}</p>
                <p><strong>Horário:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>Erro:</strong></p>
                <pre style="background-color: white; padding: 15px; border: 1px solid #dee2e6;">
{erro_mensagem}
                </pre>
                
                {f'''
                <p><strong>Stack Trace:</strong></p>
                <pre style="background-color: white; padding: 15px; border: 1px solid #dee2e6; overflow-x: auto;">
{stack_trace}
                </pre>
                ''' if stack_trace else ''}
                
                <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffc107;">
                    <strong>Ação Requerida:</strong> Verificar logs do sistema e corrigir o problema imediatamente.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=f"FALHA CRITICA em {componente}: {erro_mensagem}"
        )
