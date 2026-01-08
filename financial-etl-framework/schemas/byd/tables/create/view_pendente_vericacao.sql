## -- VIEW: byd.pendente_verificacao_view

CREATE OR REPLACE VIEW byd.pendente_verificacao_view AS
SELECT *
FROM byd.bonus_view
WHERE bonus_utilizado = 'PENDENTE VERIFICACAO'
ORDER BY dta_processamento DESC