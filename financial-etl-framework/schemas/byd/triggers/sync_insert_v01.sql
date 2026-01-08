/**
 * TRIGGER FUNCTION: sync_insert_v01
 * 
 * Objetivo:
 *   Sincroniza dados entre tabelas ao inserir novos registros.
 *   Garante que dados básicos sejam propagados para:
 *   - byd.byd_cadastro (dados cadastrais)
 *   - byd.controladoria (dados financeiros/analíticos)
 * 
 * Comportamento:
 *   - Usa ON CONFLICT DO NOTHING para evitar duplicatas
 *   - Só executa se idnfsexterno estiver preenchido
 *   - Mantém integridade referencial entre tabelas
 * 
 * Tabelas Afetadas:
 *   - byd.byd_cadastro
 *   - byd.controladoria
 * 
 * Versão: v01
 */

BEGIN
    -- Valida se existe identificador único da nota fiscal
    IF NEW.idnfsexterno IS NOT NULL THEN
        
        -- Insere dados cadastrais básicos
        -- ON CONFLICT garante idempotência (pode executar múltiplas vezes sem erro)
        INSERT INTO byd.byd_cadastro (idnfsexterno, status_nf, tipo_transacao)
        VALUES (NEW.idnfsexterno, NEW.status_nf, NEW.tipo_transacao)
        ON CONFLICT (idnfsexterno) DO NOTHING;

        -- Insere dados financeiros/analíticos para controladoria
		INSERT INTO byd.controladoria (
            idnfsexterno, chassi, revenda, empresa, des_modelo, proposta, 
            valor_venda_bruta, val_custo_contabil, lucbru, val_modalidade, 
            bonus, ano_modelo_formatado, competencia, data_final_venda
        )
        VALUES (
            NEW.idnfsexterno, NEW.chassi, NEW.revenda, NEW.empresa, 
            NEW.des_modelo, NEW.proposta, NEW.valor_venda_bruta, 
            NEW.val_custo_contabil, NEW.lucbru, NEW.val_modalidade, 
            NEW.bonus, NEW.ano_modelo_formatado, competencia, NEW.data_final_venda
        )
        ON CONFLICT (idnfsexterno) DO NOTHING;

    END IF;
    RETURN NEW;
END;