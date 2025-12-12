-- View para mostrar apenas registros com status PENDENTE VERIFICACAO
-- Esta view é automaticamente atualizada sempre que bonus_view é modificada
-- pois views são dinâmicas e refletem os dados em tempo real

CREATE OR REPLACE VIEW byd.pendente_verificacao_view AS
SELECT *
FROM byd.bonus_view
WHERE bonus_utilizado = 'PENDENTE VERIFICACAO'
ORDER BY dta_processamento DESC;

-- Adicionar comentário à view
COMMENT ON VIEW byd.pendente_verificacao_view IS 
'View que filtra apenas os registros com bonus_utilizado = PENDENTE VERIFICACAO da bonus_view. 
Atualização automática: sempre reflete os dados mais recentes da bonus_view.';
