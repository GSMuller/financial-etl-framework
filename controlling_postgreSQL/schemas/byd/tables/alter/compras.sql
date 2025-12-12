UPDATE byd.db_compras_byd

        SET status_pdi = CASE 
        WHEN val_pdi IS NULL THEN 'PENDENTE'
        ELSE 'Bonus aplicado'
        END,
        status_atacado = CASE
        WHEN percentil_atacado IS NULL THEN 'PENDENTE'
        ELSE 'Bonus aplicado'
        END



