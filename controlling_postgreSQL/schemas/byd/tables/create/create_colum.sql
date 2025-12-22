ALTER TABLE byd.bonus_view
ADD COLUMN total_bonus NUMERIC GENERATED ALWAYS AS (
    COALESCE(valor_bonus, 0) + 
    COALESCE(reembolso_ipva, 0) + 
    COALESCE(trade, 0)
) STORED;