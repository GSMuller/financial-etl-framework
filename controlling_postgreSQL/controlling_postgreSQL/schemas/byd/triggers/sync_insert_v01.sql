BEGIN
    IF NEW.idnfsexterno IS NOT NULL THEN
        INSERT INTO byd.byd_cadastro (idnfsexterno, status_nf, tipo_transacao)
        VALUES (NEW.idnfsexterno, NEW.status_nf, NEW.tipo_transacao)
        ON CONFLICT (idnfsexterno) DO NOTHING;

		INSERT INTO byd.controladoria (idnfsexterno, chassi, revenda, empresa, des_modelo, proposta, valor_venda_bruta, val_custo_contabil, lucbru, val_modalidade, bonus, ano_modelo_formatado,competencia , data_final_venda)
        VALUES (NEW.idnfsexterno, NEW.chassi, NEW.revenda, NEW.empresa, NEW.des_modelo, NEW.proposta, NEW.valor_venda_bruta, NEW.val_custo_contabil, NEW.lucbru, NEW.val_modalidade, NEW.bonus, NEW.ano_modelo_formatado,competencia, NEW.data_final_venda )
        ON CONFLICT (idnfsexterno) DO NOTHING;

    END IF;
    RETURN NEW;
END;