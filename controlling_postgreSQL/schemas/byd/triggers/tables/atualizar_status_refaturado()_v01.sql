BEGIN
    UPDATE byd.db_vendas_byd AS v
    SET refaturado = sub.status
    FROM (
        SELECT 
            idnfsexterno,
            -- FALSE (Não refaturado) para o registro mais recente (ranking = 1)
            CASE 
                WHEN ROW_NUMBER() OVER (
                    PARTITION BY chassi 
                    ORDER BY dta_processamento DESC, idnfsexterno DESC
                ) = 1 THEN FALSE 
                ELSE TRUE -- TRUE (Refaturado) para os históricos
            END AS status
        FROM byd.db_vendas_byd
        WHERE chassi = NEW.chassi
    ) AS sub
    WHERE v.idnfsexterno = sub.idnfsexterno;
    
    RETURN NEW;
END;