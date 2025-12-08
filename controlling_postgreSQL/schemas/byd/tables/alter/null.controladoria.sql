UPDATE byd.controladoria
SET 
    bonus_dpto = CASE 
        WHEN bonus_dpto = 'NaN' OR bonus_dpto = '0.0' THEN NULL 
        ELSE bonus_dpto 
    END,
    rebate_dpto = CASE 
        WHEN rebate_dpto = 'NaN' OR rebate_dpto = '0.0' THEN NULL 
        ELSE rebate_dpto 
    END,
    ipva_dpto = CASE 
        WHEN ipva_dpto = 'NaN' OR ipva_dpto = '0.0' THEN NULL 
        ELSE ipva_dpto 
    END,
    trade_mkt_dpto = CASE 
        WHEN trade_mkt_dpto = 'NaN' OR trade_mkt_dpto = '0.0' THEN NULL 
        ELSE trade_mkt_dpto 
    END
WHERE 
    bonus_dpto IN ('NaN', '0.0')
    OR rebate_dpto IN ('NaN', '0.0')
    OR ipva_dpto IN ('NaN', '0.0')
    OR trade_mkt_dpto IN ('NaN', '0.0');