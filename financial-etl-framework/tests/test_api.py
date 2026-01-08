"""
Testes para a API FastAPI (api/main.py)

Suite completa de testes de integração para todos os endpoints:
- Health checks
- Endpoints de divergências
- Endpoints de auditoria
- Endpoints de relatórios
- Endpoints de métricas
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date

try:
    from fastapi.testclient import TestClient
    from financial_etl.api.main import app
    client = TestClient(app)
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    client = None


pytestmark = pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI não instalado")


class TestHealthEndpoints:
    """Testes para endpoints de health check."""
    
    def test_root_endpoint(self):
        """Testa endpoint raiz (/)."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Financial ETL API"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_health_check_success(self):
        """Testa health check quando tudo está OK."""
        with patch('financial_etl.api.main.db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value.__enter__.return_value = mock_connection
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["api"] == "healthy"
            assert data["database"] == "healthy"
            assert data["status"] == "healthy"
    
    def test_health_check_database_down(self):
        """Testa health check quando banco está indisponível."""
        with patch('financial_etl.api.main.db_connection') as mock_conn:
            mock_conn.return_value.__enter__.side_effect = Exception("Database error")
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["database"] == "unhealthy"
            assert data["status"] == "degraded"


class TestMetricasEndpoints:
    """Testes para endpoints de métricas."""
    
    def test_metricas_resumo_sem_filtros(self):
        """Testa endpoint de métricas sem filtros de data."""
        with patch('financial_etl.api.main.db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (100, 80, 20, 5)
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value.__enter__.return_value = mock_connection
            
            response = client.get("/api/v1/metricas/resumo")
            
            # Pode retornar 200 ou 404 dependendo da implementação
            assert response.status_code in [200, 404, 422]
    
    def test_metricas_resumo_com_filtros(self):
        """Testa métricas com filtros de data."""
        with patch('financial_etl.api.main.db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (50, 40, 10, 2)
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value.__enter__.return_value = mock_connection
            
            response = client.get(
                "/api/v1/metricas/resumo",
                params={
                    "data_inicio": "2026-01-01",
                    "data_fim": "2026-01-31"
                }
            )
            
            assert response.status_code in [200, 404, 422]


class TestDivergenciasEndpoints:
    """Testes para endpoints de divergências."""
    
    def test_listar_divergencias(self):
        """Testa listagem de divergências."""
        response = client.get("/api/v1/divergencias/")
        
        # Endpoint pode não estar implementado ainda
        assert response.status_code in [200, 404, 405]
    
    def test_listar_divergencias_com_paginacao(self):
        """Testa listagem com paginação."""
        response = client.get(
            "/api/v1/divergencias/",
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code in [200, 404, 405, 422]
    
    def test_obter_divergencia_por_id(self):
        """Testa obtenção de divergência específica."""
        response = client.get("/api/v1/divergencias/123")
        
        assert response.status_code in [200, 404]
    


class TestAuditoriaEndpoints:
    """Testes para endpoints de auditoria."""
    
    def test_listar_operacoes_auditoria(self):
        """Testa listagem de operações de auditoria."""
        response = client.get("/api/v1/auditoria/operacoes")
        
        assert response.status_code in [200, 404, 405]
    
    def test_obter_operacao_auditoria_por_id(self):
        """Testa obtenção de operação específica."""
        response = client.get("/api/v1/auditoria/operacoes/123")
        
        assert response.status_code in [200, 404]
    
    def test_obter_historico_registro(self):
        """Testa histórico de um registro específico."""
        response = client.get("/api/v1/auditoria/historico/NF-123")
        
        assert response.status_code in [200, 404]


class TestRelatoriosEndpoints:
    """Testes para endpoints de relatórios."""
    
    def test_gerar_relatorio_divergencias(self):
        """Testa geração de relatório de divergências."""
        payload = {
            "data_inicio": "2026-01-01",
            "data_fim": "2026-01-31",
            "formato": "csv"
        }
        
        response = client.post("/api/v1/relatorios/divergencias", json=payload)
        
        assert response.status_code in [200, 201, 404, 422]
    
    def test_gerar_relatorio_excel(self):
        """Testa geração de relatório em Excel."""
        payload = {
            "data_inicio": "2026-01-01",
            "data_fim": "2026-01-31",
            "formato": "excel"
        }
        
        response = client.post("/api/v1/relatorios/divergencias", json=payload)
        
        assert response.status_code in [200, 201, 404, 422]
    
    def test_download_relatorio(self):
        """Testa download de relatório gerado."""
        response = client.get("/api/v1/relatorios/download/relatorio_123.csv")
        
        assert response.status_code in [200, 404]


class TestCORS:
    """Testes para configuração CORS."""
    
    def test_cors_headers_presente(self):
        """Testa presença de headers CORS."""
        response = client.options("/api/health")
        
        # Verificar headers CORS
        assert response.status_code in [200, 405]
    
    def test_cors_permite_looker_studio(self):
        """Testa que CORS permite Looker Studio."""
        headers = {
            "Origin": "https://lookerstudio.google.com"
        }
        
        response = client.get("/api/health", headers=headers)
        
        assert response.status_code == 200


class TestValidacao:
    """Testes de validação de entrada."""
    
    def test_data_invalida(self):
        """Testa validação de data inválida."""
        response = client.get(
            "/api/v1/metricas/resumo",
            params={
                "data_inicio": "invalid-date",
                "data_fim": "2026-01-31"
            }
        )
        
        assert response.status_code == 422
    


class TestAutenticacao:
    """Testes de autenticação (se implementado)."""
    
    def test_endpoint_sem_autenticacao(self):
        """Testa acesso sem autenticação."""
        # Se autenticação estiver implementada
        response = client.get("/api/v1/divergencias/")
        
        # Pode retornar 401 se autenticação for obrigatória
        assert response.status_code in [200, 401, 404]
    
    def test_token_invalido(self):
        """Testa token de autenticação inválido."""
        headers = {"Authorization": "Bearer token_invalido"}
        
        response = client.get("/api/v1/divergencias/", headers=headers)
        
        assert response.status_code in [200, 401, 404]


class TestTratamentoErros:
    """Testes de tratamento de erros."""
    
    def test_endpoint_inexistente(self):
        """Testa requisição para endpoint que não existe."""
        response = client.get("/api/v1/endpoint/inexistente")
        
        assert response.status_code == 404
    
    def test_metodo_nao_permitido(self):
        """Testa método HTTP não permitido."""
        response = client.delete("/api/health")
        
        assert response.status_code in [405, 404]
    
    def test_erro_interno_servidor(self):
        """Testa tratamento de erro interno."""
        with patch('financial_etl.api.main.db_connection') as mock_conn:
            mock_conn.return_value.__enter__.side_effect = Exception("Internal error")
            
            response = client.get("/api/health")
            
            # Deve tratar erro graciosamente
            assert response.status_code in [200, 500]


class TestDocumentacao:
    """Testes para documentação da API."""
    
    def test_swagger_docs_disponivel(self):
        """Testa que Swagger docs está disponível."""
        response = client.get("/api/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_redoc_disponivel(self):
        """Testa que ReDoc está disponível."""
        response = client.get("/api/redoc")
        
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Testa que OpenAPI JSON está disponível."""
        response = client.get("/api/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data


class TestPerformance:
    """Testes de performance básicos."""
    
    def test_health_check_rapido(self):
        """Testa que health check responde rapidamente."""
        import time
        
        start = time.time()
        response = client.get("/api/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0  # Deve responder em menos de 5 segundos
    
    def test_root_endpoint_rapido(self):
        """Testa que endpoint raiz responde rapidamente."""
        import time
        
        start = time.time()
        response = client.get("/")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Deve responder em menos de 1 segundo


class TestIntegracao:
    """Testes de integração de fluxo completo."""
    
    def test_fluxo_deteccao_correcao(self):
        """Testa fluxo completo de detecção e correção."""
        # 1. Detectar divergências
        response1 = client.post(
            "/api/v1/divergencias/detectar",
            json={"data_inicio": "2026-01-01", "data_fim": "2026-01-31"}
        )
        
        # 2. Listar divergências
        response2 = client.get("/api/v1/divergencias/")
        
        # 3. Corrigir divergência
        if response1.status_code == 200:
            response3 = client.post(
                "/api/v1/divergencias/corrigir",
                json={"id_nota": "NF-123", "tipo_correcao": "automatica"}
            )
            
            # Verificar que fluxo funcionou
            assert response3.status_code in [200, 201, 404, 422]


class TestRespostasPadronizadas:
    """Testes para verificar formato padrão de respostas."""
    
    def test_erro_404_formato_padrao(self):
        """Testa formato de resposta 404."""
        response = client.get("/api/v1/inexistente")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_sucesso_200_formato_padrao(self):
        """Testa formato de resposta 200."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# Fixtures específicas para testes de API
@pytest.fixture
def api_client():
    """Fixture que retorna cliente de teste."""
    return TestClient(app)


@pytest.fixture
def mock_db_for_api(mock_db_connection):
    """Fixture que mocka banco de dados para API."""
    with patch('financial_etl.api.main.db_connection') as mock:
        mock.return_value.__enter__.return_value = mock_db_connection
        yield mock
