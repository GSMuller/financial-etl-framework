# API REST - Referência Completa

## Versão 1.0.0

Base URL: `http://localhost:8000`

---

## Autenticação

Atualmente a API não requer autenticação. Para ambientes de produção, implemente:
- JWT tokens
- API Keys
- OAuth 2.0

---

## Endpoints

### Health Check

#### GET /
Verificação básica da API.

**Response:**
```json
{
  "service": "Financial ETL API",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2026-01-08T10:30:00",
  "documentation": "/api/docs"
}
```

#### GET /api/health
Verificação detalhada incluindo conexão com banco de dados.

**Response:**
```json
{
  "api": "healthy",
  "database": "healthy",
  "status": "healthy",
  "timestamp": "2026-01-08T10:30:00"
}
```

---

## Divergências

### GET /api/v1/divergencias

Lista divergências com filtros e paginação.

**Query Parameters:**
- `status_processamento` (string, optional): DETECTED, APPROVED, REJECTED, AUTO_APPLIED
- `tipo_divergencia` (string, optional): Tipo específico de divergência
- `data_inicio` (date, optional): Data início (formato: YYYY-MM-DD)
- `data_fim` (date, optional): Data fim (formato: YYYY-MM-DD)
- `limit` (int, optional): Limite de resultados (default: 100, max: 1000)
- `offset` (int, optional): Offset para paginação (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "idnfsexterno": "NF123456",
    "tipo_divergencia": "TRADE_MARKETING_BONUS",
    "campo_afetado": "bonus_dpto",
    "valor_anterior": 0.0,
    "valor_sugerido": 5000.0,
    "valor_aplicado": null,
    "competencia": "2025-12",
    "status_processamento": "DETECTED",
    "confidence_score": 0.95,
    "detectado_em": "2026-01-08T07:15:00",
    "processado_em": null
  }
]
```

**Exemplo:**
```bash
curl "http://localhost:8000/api/v1/divergencias?status_processamento=DETECTED&limit=50"
```

---

### GET /api/v1/divergencias/{divergencia_id}

Obtém detalhes de uma divergência específica.

**Path Parameters:**
- `divergencia_id` (int): ID da divergência

**Response:**
```json
{
  "id": 1,
  "idnfsexterno": "NF123456",
  "tipo_divergencia": "TRADE_MARKETING_BONUS",
  "campo_afetado": "bonus_dpto",
  "valor_anterior": 0.0,
  "valor_sugerido": 5000.0,
  "valor_aplicado": 5000.0,
  "competencia": "2025-12",
  "status_processamento": "APPROVED",
  "confidence_score": 0.95,
  "detectado_em": "2026-01-08T07:15:00",
  "processado_em": "2026-01-08T09:30:00"
}
```

**Erro 404:**
```json
{
  "detail": "Divergencia 999 nao encontrada"
}
```

---

### POST /api/v1/divergencias/processar

Executa processamento de divergências em período especificado.

**Request Body:**
```json
{
  "data_inicio": "2025-08-01",
  "data_fim": "2026-05-31",
  "tipo_divergencia": null,
  "modo": "auto",
  "usuario": "giovanni.5683"
}
```

**Campos:**
- `data_inicio` (string, optional): Data início no formato YYYY-MM-DD
- `data_fim` (string, optional): Data fim no formato YYYY-MM-DD
- `tipo_divergencia` (string, optional): Filtrar tipo específico
- `modo` (string): "auto" ou "manual" (default: "manual")
- `usuario` (string): Identificador do usuário (default: "sistema")

**Response:**
```json
{
  "status": "completed",
  "periodo": {
    "data_inicio": "2025-08-01",
    "data_fim": "2026-05-31"
  },
  "modo_processamento": "auto",
  "resultado": {
    "total_divergencias": 47,
    "corrigidas_automaticamente": 35,
    "pendentes_aprovacao": 10,
    "erros": 2,
    "detalhes": [...]
  },
  "timestamp": "2026-01-08T10:45:00"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/divergencias/processar \
  -H "Content-Type: application/json" \
  -d '{"data_inicio": "2025-12-01", "data_fim": "2025-12-31", "modo": "auto", "usuario": "giovanni.5683"}'
```

---

### POST /api/v1/divergencias/aprovar

Aprova e aplica correções para divergências selecionadas.

**Request Body:**
```json
{
  "divergencia_ids": [1, 2, 3],
  "usuario": "giovanni.5683",
  "aplicar_valor_sugerido": true,
  "valor_customizado": null
}
```

**Campos:**
- `divergencia_ids` (array[int]): IDs das divergências a aprovar
- `usuario` (string): Identificador do usuário aprovando
- `aplicar_valor_sugerido` (bool): Se true, aplica valor sugerido (default: true)
- `valor_customizado` (float, optional): Valor customizado (sobrescreve sugerido)

**Response:**
```json
{
  "total_processado": 3,
  "aprovados": 3,
  "erros": 0,
  "detalhes": [
    {
      "divergencia_id": 1,
      "status": "aprovado",
      "valor_aplicado": 5000.0
    },
    {
      "divergencia_id": 2,
      "status": "aprovado",
      "valor_aplicado": 3500.0
    },
    {
      "divergencia_id": 3,
      "status": "aprovado",
      "valor_aplicado": 2000.0
    }
  ],
  "timestamp": "2026-01-08T11:00:00"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/divergencias/aprovar \
  -H "Content-Type: application/json" \
  -d '{"divergencia_ids": [1, 2, 3], "usuario": "giovanni.5683", "aplicar_valor_sugerido": true}'
```

---

### DELETE /api/v1/divergencias/{divergencia_id}/rejeitar

Rejeita uma divergência com motivo.

**Path Parameters:**
- `divergencia_id` (int): ID da divergência

**Request Body:**
```json
{
  "motivo": "Valor incorreto. Requer análise mais profunda.",
  "usuario": "giovanni.5683"
}
```

**Response:**
```json
{
  "divergencia_id": 1,
  "status": "rejeitado",
  "motivo": "Valor incorreto. Requer análise mais profunda.",
  "timestamp": "2026-01-08T11:15:00"
}
```

**Exemplo:**
```bash
curl -X DELETE http://localhost:8000/api/v1/divergencias/1/rejeitar \
  -H "Content-Type: application/json" \
  -d '{"motivo": "Valor incorreto", "usuario": "giovanni.5683"}'
```

---

## Auditoria

### GET /api/v1/auditoria/operacoes

Lista histórico de operações executadas no sistema.

**Query Parameters:**
- `usuario` (string, optional): Filtrar por usuário
- `tabela` (string, optional): Filtrar por tabela afetada
- `status` (string, optional): Filtrar por status (SUCCESS, FAILED, PENDING)
- `data_inicio` (date, optional): Data início
- `data_fim` (date, optional): Data fim
- `limit` (int, optional): Limite de resultados (default: 100, max: 1000)
- `offset` (int, optional): Offset para paginação

**Response:**
```json
[
  {
    "id": 1,
    "tipo_operacao": "UPDATE",
    "descricao": "Correcao automatica: TRADE_MARKETING_BONUS",
    "usuario": "sistema_automatico",
    "origem": "AUTOMATION",
    "tabela_afetada": "byd.controladoria",
    "registros_afetados": 1,
    "timestamp_inicio": "2026-01-08T07:20:00",
    "timestamp_fim": "2026-01-08T07:20:02",
    "duracao_segundos": 2.1,
    "status": "SUCCESS"
  }
]
```

**Exemplo:**
```bash
curl "http://localhost:8000/api/v1/auditoria/operacoes?usuario=giovanni.5683&limit=20"
```

---

### GET /api/v1/auditoria/sessoes

Lista histórico de execuções do processamento automatizado.

**Query Parameters:**
- `tipo_sessao` (string, optional): DAILY_AUTO, MANUAL_RUN, REPROCESSING
- `status` (string, optional): RUNNING, COMPLETED, FAILED, PARTIAL
- `limit` (int, optional): Limite de resultados (default: 50, max: 500)

**Response:**
```json
[
  {
    "id": 1,
    "tipo_sessao": "DAILY_AUTO",
    "inicio_processamento": "2026-01-08T07:00:00",
    "fim_processamento": "2026-01-08T07:15:30",
    "duracao_total_segundos": 930,
    "status": "COMPLETED",
    "metricas": {
      "total_registros_analisados": 47,
      "divergencias_detectadas": 47,
      "correcoes_aplicadas": 35,
      "correcoes_pendentes": 10,
      "erros_encontrados": 2
    },
    "resultado_geral": "Processamento concluido com sucesso. 35 correcoes aplicadas, 10 pendentes."
  }
]
```

---

## Métricas

### GET /api/v1/metricas/resumo

Retorna métricas resumidas do sistema.

**Query Parameters:**
- `data_inicio` (date, optional): Data início do período
- `data_fim` (date, optional): Data fim do período

**Response:**
```json
{
  "periodo": {
    "data_inicio": "2026-01-01",
    "data_fim": "2026-01-08"
  },
  "metricas_gerais": {
    "total_divergencias": 147,
    "total_resolvidas": 125,
    "taxa_resolucao_percentual": 85.03,
    "tempo_medio_resolucao_dias": 2.3
  },
  "divergencias_por_tipo": [
    {
      "tipo": "TRADE_MARKETING_BONUS",
      "total": 85,
      "resolvidas": 78,
      "taxa_resolucao": 91.76
    },
    {
      "tipo": "TRADE_MARKETING_TRADE",
      "total": 40,
      "resolvidas": 35,
      "taxa_resolucao": 87.50
    },
    {
      "tipo": "PENDENTE_VERIFICACAO",
      "total": 22,
      "resolvidas": 12,
      "taxa_resolucao": 54.55
    }
  ],
  "operacoes_por_status": [
    {
      "status": "SUCCESS",
      "total": 280
    },
    {
      "status": "FAILED",
      "total": 5
    }
  ],
  "timestamp_consulta": "2026-01-08T12:00:00"
}
```

**Uso para Looker Studio:**
```javascript
// Data Source: JSON/REST API
var url = "http://localhost:8000/api/v1/metricas/resumo";
var response = UrlFetchApp.fetch(url);
var data = JSON.parse(response.getContentText());
```

---

## Relatórios

### GET /api/v1/relatorios/divergencias/export

Exporta relatório de divergências em CSV ou Excel.

**Query Parameters:**
- `formato` (string): "csv" ou "excel" (default: "csv")
- `status_processamento` (string, optional): Filtrar por status
- `data_inicio` (date, optional): Data início
- `data_fim` (date, optional): Data fim

**Response:**
- Arquivo CSV ou Excel para download

**Headers:**
- `Content-Type`: text/csv ou application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- `Content-Disposition`: attachment; filename=divergencias_YYYY-MM-DD.csv

**Exemplo:**
```bash
# Baixar CSV
curl "http://localhost:8000/api/v1/relatorios/divergencias/export?formato=csv" -o divergencias.csv

# Baixar Excel
curl "http://localhost:8000/api/v1/relatorios/divergencias/export?formato=excel" -o divergencias.xlsx
```

---

### GET /api/v1/relatorios/metricas/performance

Retorna métricas detalhadas de performance do sistema.

**Query Parameters:**
- `data_inicio` (date, optional): Data início
- `data_fim` (date, optional): Data fim

**Response:**
```json
{
  "periodo": {
    "data_inicio": "2026-01-01",
    "data_fim": "2026-01-08"
  },
  "performance_por_tipo": [
    {
      "tipo_operacao": "UPDATE",
      "total_operacoes": 125,
      "duracao_media_seg": 1.850,
      "duracao_minima_seg": 0.120,
      "duracao_maxima_seg": 5.430,
      "mediana_seg": 1.520,
      "percentil_95_seg": 4.200
    },
    {
      "tipo_operacao": "DETECT",
      "total_operacoes": 47,
      "duracao_media_seg": 0.350,
      "duracao_minima_seg": 0.050,
      "duracao_maxima_seg": 1.200,
      "mediana_seg": 0.280,
      "percentil_95_seg": 0.920
    }
  ],
  "taxa_sucesso_por_tipo": [
    {
      "tipo_operacao": "UPDATE",
      "total": 125,
      "sucessos": 123,
      "falhas": 2,
      "taxa_sucesso_percentual": 98.40
    },
    {
      "tipo_operacao": "DETECT",
      "total": 47,
      "sucessos": 47,
      "falhas": 0,
      "taxa_sucesso_percentual": 100.00
    }
  ]
}
```

---

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos na requisição
- `404 Not Found`: Recurso não encontrado
- `500 Internal Server Error`: Erro interno do servidor

---

## Exemplos de Integração

### Python

```python
import requests

# Listar divergências pendentes
response = requests.get('http://localhost:8000/api/v1/divergencias', params={
    'status_processamento': 'DETECTED',
    'limit': 100
})
divergencias = response.json()

# Aprovar divergências
for div in divergencias:
    if div['confidence_score'] >= 0.90:
        requests.post('http://localhost:8000/api/v1/divergencias/aprovar', json={
            'divergencia_ids': [div['id']],
            'usuario': 'giovanni.5683',
            'aplicar_valor_sugerido': True
        })
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

// Obter métricas
async function obterMetricas() {
  const response = await axios.get('http://localhost:8000/api/v1/metricas/resumo');
  console.log(response.data);
}

// Processar divergências
async function processarDivergencias() {
  const response = await axios.post('http://localhost:8000/api/v1/divergencias/processar', {
    data_inicio: '2025-12-01',
    data_fim: '2025-12-31',
    modo: 'manual',
    usuario: 'sistema'
  });
  console.log(response.data);
}
```

### Power BI / Looker Studio

```
GET http://localhost:8000/api/v1/metricas/resumo
```

Configure como fonte de dados JSON/REST API e atualize automaticamente.

---

## Documentação Interativa

Acesse `http://localhost:8000/api/docs` para documentação interativa Swagger UI onde você pode:
- Ver todos os endpoints
- Testar requisições diretamente
- Ver esquemas de dados
- Baixar especificação OpenAPI

---

## Limites e Throttling

Atualmente não há limites implementados. Para produção, considere:
- Rate limiting por IP/usuário
- Timeout de requisições longas
- Paginação obrigatória para grandes volumes

---

## Versionamento

API segue versionamento semântico (v1.0.0).

Versões da API são mantidas via URL: `/api/v1/`, `/api/v2/`, etc.

---

**Última atualização:** Janeiro 2026  
**Versão da API:** 1.0.0
