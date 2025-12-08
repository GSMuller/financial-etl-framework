DECLARE
    bonus_list TEXT[];
    trade_marketing_ativo BOOLEAN; 
BEGIN
    
    -- 1. REGRA: VEÍCULO DE DEVOLUÇÃO (V07)
    IF NEW.tipo_transacao = 'V07' THEN
        NEW.bonus_utilizado := 'Veículo de Devolução';
        RETURN NEW;
    END IF;

    -- 2. REGRA: HISTÓRICO (REFATURADO)
    IF COALESCE(NEW.refaturado, FALSE) THEN 
        NEW.bonus_utilizado := 'Refaturado';
        RETURN NEW;
    END IF;

    -- 3. REGRA: VENDA DIRETA (VD)
    IF NEW.tipo_transacao = 'VD' THEN
        NEW.bonus_utilizado := 'Venda Direta';
        RETURN NEW;
    END IF;

    -- (Opcional) Venda Cancelada
    IF NEW.status_nf = 'C' THEN
        NEW.bonus_utilizado := 'Venda Cancelada';
        RETURN NEW;
    END IF;
    
    -- 4. REGRA: PENDENTE VERIFICACAO
    -- Verifica apenas as colunas que realmente compõem o bônus
    IF NEW.taxa_0 IS NULL AND NEW.ipva IS NULL AND NEW.wallbox IS NULL
        AND NEW.portatil IS NULL AND NEW.seguro IS NULL
        AND NEW.trade_in IS NULL AND NEW.equalizacao IS NULL
        AND NEW.varejo IS NULL 
        AND NEW.em_valid IS NULL 
        -- Numérico (apenas Trade conta)
        AND COALESCE(NEW.trade, 0) = 0 
    THEN
        NEW.bonus_utilizado := 'PENDENTE VERIFICACAO';
        RETURN NEW;
    END IF;
    
    -- 5. CÁLCULO DA LISTA DE BÔNUS
    
    -- Verifica se Trade Marketing está ativo (> 0)
    trade_marketing_ativo := COALESCE(NEW.trade, 0) > 0;

    -- Coleta os bônus BOOLEAN que são TRUE
    -- (Removidos: portal, comissao_vd, rebate)
    SELECT ARRAY_AGG(b.nome) INTO bonus_list
    FROM (VALUES
        (NEW.taxa_0, 'Taxa 0'), 
        (NEW.ipva, 'IPVA'), 
        (NEW.wallbox, 'Wallbox'),
        (NEW.portatil, 'Portatil'), 
        (NEW.seguro, 'Seguro'),
        (NEW.trade_in, 'Trade_in'), 
        (NEW.equalizacao, 'Equalização'), 
        (NEW.varejo, 'Varejo'),
        (NEW.em_valid, 'Em Validação')
    ) AS b(status, nome)
    WHERE COALESCE(b.status, FALSE) = TRUE;

    -- Adiciona TRADE MARKETING ao final da lista se for > 0
    IF trade_marketing_ativo THEN
        bonus_list := array_append(bonus_list, 'Trade Marketing');
    END IF;

    -- 6. REGRA FINAL: SEM BÔNUS ou CONCATENAÇÃO
    IF array_length(bonus_list, 1) IS NULL THEN
        NEW.bonus_utilizado := 'Sem Bônus';
    ELSE
        NEW.bonus_utilizado := array_to_string(bonus_list, ', ');
    END IF;

    RETURN NEW;
END;
