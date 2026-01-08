/**
 * AUDIT SCHEMA - Sistema de Auditoria e Rastreabilidade
 * 
 * Este schema implementa um sistema completo de auditoria para rastreamento
 * de todas as operações realizadas no Data Warehouse, incluindo:
 * - Operações manuais e automatizadas
 * - Histórico de correções de divergências
 * - Aprovações e rejeições de processos
 * - Rollback e reversões de transações
 * 
 * Autor: Financial ETL Framework
 * Data: 2026-01-08
 * Versão: 1.0.0
 */

-- Criação do schema de auditoria
CREATE SCHEMA IF NOT EXISTS audit;

-- Comentário descritivo do schema
COMMENT ON SCHEMA audit IS 'Sistema de auditoria e rastreabilidade de operações do Data Warehouse';


/**
 * TABELA: audit.operacoes
 * 
 * Registra todas as operações executadas no banco de dados, seja por
 * processos automatizados ou intervenções manuais.
 * 
 * Uso:
 *   - Rastreamento completo de todas as transações
 *   - Base para rollback de operações
 *   - Análise de performance e volumetria
 *   - Compliance e auditoria externa
 */
CREATE TABLE IF NOT EXISTS audit.operacoes (
    id SERIAL PRIMARY KEY,
    tipo_operacao VARCHAR(50) NOT NULL,           -- INSERT, UPDATE, DELETE, ROLLBACK, BULK_UPDATE
    descricao TEXT NOT NULL,                      -- Descrição detalhada da operação
    usuario VARCHAR(100) NOT NULL,                -- Usuário ou sistema que executou
    origem VARCHAR(50) NOT NULL,                  -- MANUAL, API, AUTOMATION, NOTEBOOK
    
    -- Contexto da operação
    tabela_afetada VARCHAR(200),                  -- Schema.table afetada
    registros_afetados INTEGER DEFAULT 0,         -- Quantidade de registros alterados
    filtros_aplicados JSONB,                      -- Filtros WHERE utilizados (formato JSON)
    
    -- SQL e dados
    query_executada TEXT,                         -- Query SQL executada (se aplicável)
    dados_anteriores JSONB,                       -- Estado anterior dos dados (para rollback)
    dados_posteriores JSONB,                      -- Estado posterior dos dados
    
    -- Controle temporal
    timestamp_inicio TIMESTAMP NOT NULL DEFAULT NOW(),
    timestamp_fim TIMESTAMP,
    duracao_segundos NUMERIC(10,3),               -- Duração calculada
    
    -- Status e controle
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, SUCCESS, FAILED, ROLLED_BACK
    erro_mensagem TEXT,                           -- Mensagem de erro se status = FAILED
    rollback_de INTEGER REFERENCES audit.operacoes(id), -- ID da operação que foi revertida
    
    -- Metadados adicionais
    ip_origem VARCHAR(45),                        -- Endereço IP de origem
    user_agent TEXT,                              -- User agent (para operações via API)
    metadata JSONB                                -- Dados adicionais contextuais
);

-- Índices para otimização de consultas frequentes
CREATE INDEX idx_operacoes_tipo ON audit.operacoes(tipo_operacao);
CREATE INDEX idx_operacoes_usuario ON audit.operacoes(usuario);
CREATE INDEX idx_operacoes_tabela ON audit.operacoes(tabela_afetada);
CREATE INDEX idx_operacoes_timestamp ON audit.operacoes(timestamp_inicio DESC);
CREATE INDEX idx_operacoes_status ON audit.operacoes(status);
CREATE INDEX idx_operacoes_origem ON audit.operacoes(origem);

-- Comentários documentando os campos
COMMENT ON TABLE audit.operacoes IS 'Registro completo de todas as operações executadas no Data Warehouse';
COMMENT ON COLUMN audit.operacoes.tipo_operacao IS 'Tipo de operação SQL ou processo (INSERT, UPDATE, DELETE, etc)';
COMMENT ON COLUMN audit.operacoes.origem IS 'Sistema ou interface que originou a operação';
COMMENT ON COLUMN audit.operacoes.dados_anteriores IS 'Snapshot dos dados antes da operação em formato JSON';
COMMENT ON COLUMN audit.operacoes.rollback_de IS 'Referência à operação que foi revertida por esta';


/**
 * TABELA: audit.divergencias_processadas
 * 
 * Registra especificamente o processamento de divergências detectadas
 * no sistema de bônus, incluindo decisões de aprovação/rejeição.
 * 
 * Uso:
 *   - Histórico de divergências encontradas
 *   - Rastreamento de decisões de correção
 *   - Análise de padrões de divergências
 *   - Base para machine learning futuro
 */
CREATE TABLE IF NOT EXISTS audit.divergencias_processadas (
    id SERIAL PRIMARY KEY,
    operacao_id INTEGER REFERENCES audit.operacoes(id),
    
    -- Identificação da divergência
    idnfsexterno VARCHAR(100) NOT NULL,           -- Identificador da nota fiscal
    tipo_divergencia VARCHAR(100) NOT NULL,       -- TRADE_MARKETING, BONUS_CALCULATION, STATUS, etc
    competencia VARCHAR(7),                       -- YYYY-MM
    
    -- Detalhes da divergência
    valor_anterior NUMERIC(15,2),
    valor_sugerido NUMERIC(15,2),
    valor_aplicado NUMERIC(15,2),
    campo_afetado VARCHAR(100),
    
    -- Decisão e processamento
    status_processamento VARCHAR(50) NOT NULL,    -- DETECTED, APPROVED, REJECTED, AUTO_APPLIED
    decisao_automatica BOOLEAN DEFAULT FALSE,     -- Se foi aplicada automaticamente
    motivo_rejeicao TEXT,                        -- Motivo se rejeitada
    
    -- Rastreamento
    detectado_em TIMESTAMP NOT NULL DEFAULT NOW(),
    processado_em TIMESTAMP,
    processado_por VARCHAR(100),
    
    -- Metadados
    confidence_score NUMERIC(3,2),               -- Score de confiança (0-1) se ML aplicado
    regras_aplicadas TEXT[],                     -- Lista de regras que detectaram
    dados_contextuais JSONB                      -- Contexto adicional da divergência
);

CREATE INDEX idx_divergencias_idnf ON audit.divergencias_processadas(idnfsexterno);
CREATE INDEX idx_divergencias_tipo ON audit.divergencias_processadas(tipo_divergencia);
CREATE INDEX idx_divergencias_status ON audit.divergencias_processadas(status_processamento);
CREATE INDEX idx_divergencias_competencia ON audit.divergencias_processadas(competencia);
CREATE INDEX idx_divergencias_detectado ON audit.divergencias_processadas(detectado_em DESC);

COMMENT ON TABLE audit.divergencias_processadas IS 'Histórico de divergências detectadas e suas resoluções';
COMMENT ON COLUMN audit.divergencias_processadas.confidence_score IS 'Score de confiança da detecção automática (0.0 a 1.0)';


/**
 * TABELA: audit.sessoes_processamento
 * 
 * Registra cada execução do processamento automatizado diário,
 * consolidando métricas e resultados de cada sessão.
 * 
 * Uso:
 *   - Monitoramento de execuções diárias
 *   - Análise de performance do sistema
 *   - Alertas de falhas
 *   - Métricas operacionais
 */
CREATE TABLE IF NOT EXISTS audit.sessoes_processamento (
    id SERIAL PRIMARY KEY,
    tipo_sessao VARCHAR(50) NOT NULL,            -- DAILY_AUTO, MANUAL_RUN, REPROCESSING
    
    -- Controle temporal
    inicio_processamento TIMESTAMP NOT NULL DEFAULT NOW(),
    fim_processamento TIMESTAMP,
    duracao_total_segundos INTEGER,
    
    -- Métricas da sessão
    total_registros_analisados INTEGER DEFAULT 0,
    divergencias_detectadas INTEGER DEFAULT 0,
    correcoes_aplicadas INTEGER DEFAULT 0,
    correcoes_pendentes INTEGER DEFAULT 0,
    erros_encontrados INTEGER DEFAULT 0,
    
    -- Status e resultado
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING', -- RUNNING, COMPLETED, FAILED, PARTIAL
    resultado_geral TEXT,                         -- Resumo textual do resultado
    
    -- Detalhes técnicos
    versao_sistema VARCHAR(20),
    ambiente VARCHAR(20),                         -- PRODUCTION, STAGING, DEVELOPMENT
    parametros_execucao JSONB,                   -- Parâmetros utilizados na execução
    log_completo TEXT,                           -- Log completo da execução
    
    -- Notificações
    alertas_enviados BOOLEAN DEFAULT FALSE,
    destinatarios_notificados TEXT[]
);

CREATE INDEX idx_sessoes_inicio ON audit.sessoes_processamento(inicio_processamento DESC);
CREATE INDEX idx_sessoes_status ON audit.sessoes_processamento(status);
CREATE INDEX idx_sessoes_tipo ON audit.sessoes_processamento(tipo_sessao);

COMMENT ON TABLE audit.sessoes_processamento IS 'Registro de cada execução do processo automatizado de ETL';


/**
 * TABELA: audit.configuracoes_sistema
 * 
 * Armazena configurações do sistema e seu histórico de alterações,
 * permitindo rastreamento de quando e por quem foram modificadas.
 * 
 * Uso:
 *   - Controle de parâmetros operacionais
 *   - Histórico de mudanças de configuração
 *   - Rollback de configurações
 */
CREATE TABLE IF NOT EXISTS audit.configuracoes_sistema (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) NOT NULL,
    valor TEXT NOT NULL,
    tipo_valor VARCHAR(20),                      -- STRING, INTEGER, BOOLEAN, JSON
    descricao TEXT,
    
    -- Controle de versão
    versao INTEGER NOT NULL DEFAULT 1,
    ativo BOOLEAN DEFAULT TRUE,
    
    -- Rastreamento
    criado_em TIMESTAMP NOT NULL DEFAULT NOW(),
    criado_por VARCHAR(100) NOT NULL,
    modificado_em TIMESTAMP,
    modificado_por VARCHAR(100),
    
    -- Validação
    valor_padrao TEXT,
    validacao_regex VARCHAR(500),
    obrigatorio BOOLEAN DEFAULT FALSE,
    
    UNIQUE(chave, versao)
);

CREATE INDEX idx_config_chave_ativo ON audit.configuracoes_sistema(chave, ativo);
CREATE INDEX idx_config_modificado ON audit.configuracoes_sistema(modificado_em DESC);

COMMENT ON TABLE audit.configuracoes_sistema IS 'Configurações do sistema com versionamento e histórico';


/**
 * VIEW: audit.vw_operacoes_resumo
 * 
 * View consolidada para análise rápida de operações por período.
 */
CREATE OR REPLACE VIEW audit.vw_operacoes_resumo AS
SELECT 
    DATE(timestamp_inicio) as data,
    tipo_operacao,
    origem,
    status,
    COUNT(*) as total_operacoes,
    SUM(registros_afetados) as total_registros,
    AVG(duracao_segundos) as duracao_media_seg,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as total_erros
FROM audit.operacoes
GROUP BY DATE(timestamp_inicio), tipo_operacao, origem, status;

COMMENT ON VIEW audit.vw_operacoes_resumo IS 'Resumo diário de operações por tipo e status';


/**
 * VIEW: audit.vw_divergencias_abertas
 * 
 * View de divergências ainda não processadas ou pendentes.
 */
CREATE OR REPLACE VIEW audit.vw_divergencias_abertas AS
SELECT 
    d.*,
    EXTRACT(DAY FROM NOW() - d.detectado_em) as dias_pendente
FROM audit.divergencias_processadas d
WHERE status_processamento IN ('DETECTED', 'APPROVED')
  AND processado_em IS NULL
ORDER BY detectado_em ASC;

COMMENT ON VIEW audit.vw_divergencias_abertas IS 'Divergências detectadas aguardando processamento';


/**
 * FUNCTION: audit.registrar_operacao
 * 
 * Função helper para facilitar registro de operações de auditoria.
 * Retorna o ID da operação criada.
 */
CREATE OR REPLACE FUNCTION audit.registrar_operacao(
    p_tipo_operacao VARCHAR(50),
    p_descricao TEXT,
    p_usuario VARCHAR(100),
    p_origem VARCHAR(50),
    p_tabela_afetada VARCHAR(200) DEFAULT NULL,
    p_registros_afetados INTEGER DEFAULT 0,
    p_query_executada TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_operacao_id INTEGER;
BEGIN
    INSERT INTO audit.operacoes (
        tipo_operacao, descricao, usuario, origem,
        tabela_afetada, registros_afetados, query_executada,
        timestamp_inicio, status
    ) VALUES (
        p_tipo_operacao, p_descricao, p_usuario, p_origem,
        p_tabela_afetada, p_registros_afetados, p_query_executada,
        NOW(), 'SUCCESS'
    ) RETURNING id INTO v_operacao_id;
    
    RETURN v_operacao_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION audit.registrar_operacao IS 'Helper para registro simplificado de operações de auditoria';


/**
 * FUNCTION: audit.finalizar_operacao
 * 
 * Atualiza uma operação com status final e calcula duração.
 */
CREATE OR REPLACE FUNCTION audit.finalizar_operacao(
    p_operacao_id INTEGER,
    p_status VARCHAR(20),
    p_erro_mensagem TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE audit.operacoes
    SET 
        timestamp_fim = NOW(),
        duracao_segundos = EXTRACT(EPOCH FROM (NOW() - timestamp_inicio)),
        status = p_status,
        erro_mensagem = p_erro_mensagem
    WHERE id = p_operacao_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION audit.finalizar_operacao IS 'Finaliza registro de operação com status e duração';


-- Grants de permissões (ajustar conforme usuários do sistema)
-- GRANT SELECT ON ALL TABLES IN SCHEMA audit TO app_readonly;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO app_readwrite;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO app_readwrite;
