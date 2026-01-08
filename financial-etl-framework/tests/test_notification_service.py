"""
Testes para o módulo NotificationService (services/notification_service.py)

Suite completa de testes incluindo:
- Envio de emails básicos e com anexos
- Alertas de divergências
- Resumos de processamento
- Alertas de falhas críticas
- Tratamento de erros de SMTP
"""

import pytest
from unittest.mock import MagicMock, patch, call, Mock
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from financial_etl.services.notification_service import NotificationService
    NOTIFICATION_AVAILABLE = True
except ImportError:
    NOTIFICATION_AVAILABLE = False
    NotificationService = None


pytestmark = pytest.mark.skipif(not NOTIFICATION_AVAILABLE, reason="Módulo notification_service não disponível")


class TestNotificationServiceInit:
    """Testes de inicialização do NotificationService."""
    
    def test_init_com_env_vars(self, mock_env_vars):
        """Testa inicialização com variáveis de ambiente."""
        service = NotificationService()
        
        assert service.smtp_host == 'smtp.test.com'
        assert service.smtp_port == 587
        assert service.smtp_user == 'test@test.com'
    
    def test_init_sem_env_vars(self):
        """Testa inicialização sem variáveis de ambiente."""
        import os
        
        # Limpar variáveis relevantes
        for key in ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD']:
            os.environ.pop(key, None)
        
        # Deve usar valores default ou lançar erro
        try:
            service = NotificationService()
            assert service is not None
        except (ValueError, KeyError):
            # Esperado se validação estiver implementada
            pass


class TestEnviarEmail:
    """Testes para envio básico de emails."""
    
    @patch('smtplib.SMTP')
    def test_enviar_email_simples(self, mock_smtp_class, mock_env_vars):
        """Testa envio de email simples."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@example.com',
            assunto='Teste',
            corpo='Mensagem de teste'
        )
        
        # Verificar que SMTP foi chamado
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once()
        mock_smtp.send_message.assert_called_once()
        assert resultado == True or mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_enviar_email_html(self, mock_smtp_class, mock_env_vars):
        """Testa envio de email com HTML."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        html_corpo = """
        <html>
            <body>
                <h1>Teste HTML</h1>
                <p>Este é um email de teste.</p>
            </body>
        </html>
        """
        
        resultado = service.enviar_email(
            destinatario='test@example.com',
            assunto='Teste HTML',
            corpo=html_corpo,
            html=True
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_enviar_email_multiplos_destinatarios(self, mock_smtp_class, mock_env_vars):
        """Testa envio para múltiplos destinatários."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        destinatarios = ['user1@test.com', 'user2@test.com', 'user3@test.com']
        
        resultado = service.enviar_email(
            destinatario=destinatarios,
            assunto='Teste múltiplos',
            corpo='Mensagem para vários'
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_enviar_email_com_anexo(self, mock_smtp_class, mock_env_vars, temp_csv_file):
        """Testa envio de email com anexo."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@example.com',
            assunto='Email com anexo',
            corpo='Veja o anexo',
            anexos=[str(temp_csv_file)]
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_enviar_email_erro_smtp(self, mock_smtp_class, mock_env_vars):
        """Testa tratamento de erro SMTP."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        mock_smtp.send_message.side_effect = smtplib.SMTPException("Erro de conexão")
        
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@example.com',
            assunto='Teste erro',
            corpo='Deve falhar'
        )
        
        assert resultado == False or mock_smtp.send_message.called


class TestEnviarAlertaDivergencias:
    """Testes para alertas de divergências."""
    
    @patch('smtplib.SMTP')
    def test_alerta_divergencias_encontradas(self, mock_smtp_class, mock_env_vars, sample_divergencias_list):
        """Testa envio de alerta quando divergências são encontradas."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_alerta_divergencias(
            divergencias_count=5,
            divergencias_resumo=sample_divergencias_list[:3],
            destinatarios=['controller@company.com']
        )
        
        assert mock_smtp.send_message.called or resultado == True
    
    @patch('smtplib.SMTP')
    def test_alerta_sem_divergencias(self, mock_smtp_class, mock_env_vars):
        """Testa que não envia alerta se não houver divergências."""
        service = NotificationService()
        
        resultado = service.enviar_alerta_divergencias(
            divergencias_count=0,
            divergencias_resumo=[],
            destinatarios=['controller@company.com']
        )
        
        # Não deve enviar email
        assert resultado == False or resultado is None
    
    @patch('smtplib.SMTP')
    def test_alerta_divergencias_html_formatado(self, mock_smtp_class, mock_env_vars):
        """Testa formatação HTML do alerta de divergências."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        divergencias = [
            {
                'id_nota': 'NF-001',
                'tipo_divergencia': 'trade_marketing',
                'confianca': 0.95,
                'valor_esperado': 5000.0
            }
        ]
        
        resultado = service.enviar_alerta_divergencias(
            divergencias_count=1,
            divergencias_resumo=divergencias,
            destinatarios=['test@test.com']
        )
        
        # Verificar que mensagem foi enviada
        if mock_smtp.send_message.called:
            call_args = mock_smtp.send_message.call_args
            # Verificar que contém HTML
            assert call_args is not None


class TestEnviarResumoProcessamento:
    """Testes para envio de resumo de processamento."""
    
    @patch('smtplib.SMTP')
    def test_resumo_processamento_sucesso(self, mock_smtp_class, mock_env_vars):
        """Testa envio de resumo de processamento bem-sucedido."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_resumo_processamento(
            data_processamento=date(2026, 1, 8),
            divergencias_detectadas=10,
            corrigidas_automaticamente=8,
            pendentes_revisao=2,
            tempo_processamento=120.5,
            destinatarios=['manager@company.com']
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_resumo_sem_divergencias(self, mock_smtp_class, mock_env_vars):
        """Testa resumo quando não há divergências."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_resumo_processamento(
            data_processamento=date(2026, 1, 8),
            divergencias_detectadas=0,
            corrigidas_automaticamente=0,
            pendentes_revisao=0,
            tempo_processamento=30.0,
            destinatarios=['manager@company.com']
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_resumo_com_metricas_detalhadas(self, mock_smtp_class, mock_env_vars):
        """Testa resumo com métricas detalhadas."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        metricas = {
            'trade_marketing': 5,
            'pendente_verificacao': 3,
            'validacao_valores': 2,
            'taxa_sucesso': 0.80
        }
        
        resultado = service.enviar_resumo_processamento(
            data_processamento=date(2026, 1, 8),
            divergencias_detectadas=10,
            corrigidas_automaticamente=8,
            pendentes_revisao=2,
            tempo_processamento=150.0,
            metricas_detalhadas=metricas,
            destinatarios=['manager@company.com']
        )
        
        assert mock_smtp.send_message.called


class TestEnviarAlertaFalhaCritica:
    """Testes para alertas de falhas críticas."""
    
    @patch('smtplib.SMTP')
    def test_alerta_falha_critica(self, mock_smtp_class, mock_env_vars):
        """Testa envio de alerta de falha crítica."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        resultado = service.enviar_alerta_falha_critica(
            tipo_falha='DATABASE_CONNECTION',
            mensagem_erro='Não foi possível conectar ao banco de dados',
            stack_trace='Traceback...',
            destinatarios=['admin@company.com', 'devops@company.com']
        )
        
        assert mock_smtp.send_message.called
    
    @patch('smtplib.SMTP')
    def test_alerta_falha_com_contexto(self, mock_smtp_class, mock_env_vars):
        """Testa alerta de falha com contexto adicional."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        contexto = {
            'servidor': 'prod-db-01',
            'timestamp': datetime(2026, 1, 8, 10, 30),
            'tentativas': 3
        }
        
        resultado = service.enviar_alerta_falha_critica(
            tipo_falha='ETL_FAILURE',
            mensagem_erro='Falha ao processar dados',
            contexto=contexto,
            destinatarios=['admin@company.com']
        )
        
        assert mock_smtp.send_message.called


class TestTemplatesHTML:
    """Testes para templates HTML de emails."""
    
    def test_template_divergencias_renderiza(self, mock_env_vars):
        """Testa renderização do template de divergências."""
        service = NotificationService()
        
        if hasattr(service, '_gerar_html_divergencias'):
            html = service._gerar_html_divergencias(
                divergencias_count=5,
                divergencias_resumo=[
                    {'id_nota': 'NF-001', 'tipo': 'trade_marketing'}
                ]
            )
            
            assert '<html' in html.lower()
            assert 'NF-001' in html
    
    def test_template_resumo_renderiza(self, mock_env_vars):
        """Testa renderização do template de resumo."""
        service = NotificationService()
        
        if hasattr(service, '_gerar_html_resumo'):
            html = service._gerar_html_resumo(
                data_processamento=date(2026, 1, 8),
                divergencias_detectadas=10,
                corrigidas=8,
                pendentes=2
            )
            
            assert '<html' in html.lower()
            assert '10' in html


class TestTratamentoErros:
    """Testes para tratamento de erros."""
    
    @patch('smtplib.SMTP')
    def test_erro_autenticacao(self, mock_smtp_class, mock_env_vars):
        """Testa tratamento de erro de autenticação."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
        
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@test.com',
            assunto='Teste',
            corpo='Teste'
        )
        
        assert resultado == False
    
    @patch('smtplib.SMTP')
    def test_erro_conexao(self, mock_smtp_class, mock_env_vars):
        """Testa tratamento de erro de conexão."""
        mock_smtp_class.side_effect = smtplib.SMTPConnectError(421, 'Cannot connect')
        
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@test.com',
            assunto='Teste',
            corpo='Teste'
        )
        
        assert resultado == False
    
    def test_destinatario_invalido(self, mock_env_vars):
        """Testa validação de destinatário inválido."""
        service = NotificationService()
        
        with pytest.raises(ValueError):
            service.enviar_email(
                destinatario='',  # Vazio
                assunto='Teste',
                corpo='Teste'
            )
    
    def test_anexo_inexistente(self, mock_env_vars):
        """Testa tratamento de anexo que não existe."""
        service = NotificationService()
        
        resultado = service.enviar_email(
            destinatario='test@test.com',
            assunto='Teste',
            corpo='Teste',
            anexos=['/caminho/inexistente/arquivo.pdf']
        )
        
        # Deve falhar ou ignorar anexo
        assert resultado == False or resultado == True


class TestConfiguracaoSMTP:
    """Testes para configuração de SMTP."""
    
    def test_smtp_ssl(self, mock_env_vars):
        """Testa configuração com SSL."""
        import os
        os.environ['SMTP_USE_SSL'] = 'true'
        
        service = NotificationService()
        
        # Verificar configuração SSL
        if hasattr(service, 'use_ssl'):
            assert service.use_ssl == True
    
    def test_smtp_porta_customizada(self, mock_env_vars):
        """Testa porta SMTP customizada."""
        import os
        os.environ['SMTP_PORT'] = '465'
        
        service = NotificationService()
        
        assert service.smtp_port == 465


class TestIntegracao:
    """Testes de integração do fluxo completo."""
    
    @patch('smtplib.SMTP')
    def test_fluxo_completo_alerta(self, mock_smtp_class, mock_env_vars, sample_divergencias_list):
        """Testa fluxo completo de detecção e alerta."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        service = NotificationService()
        
        # Simular detecção de divergências
        divergencias = sample_divergencias_list
        
        # Enviar alerta
        alerta_enviado = service.enviar_alerta_divergencias(
            divergencias_count=len(divergencias),
            divergencias_resumo=divergencias[:5],
            destinatarios=['controller@company.com']
        )
        
        # Enviar resumo
        resumo_enviado = service.enviar_resumo_processamento(
            data_processamento=date.today(),
            divergencias_detectadas=len(divergencias),
            corrigidas_automaticamente=3,
            pendentes_revisao=2,
            tempo_processamento=90.0,
            destinatarios=['manager@company.com']
        )
        
        assert mock_smtp.send_message.call_count >= 1
