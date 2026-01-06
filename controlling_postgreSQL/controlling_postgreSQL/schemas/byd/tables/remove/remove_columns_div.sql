-- Remove todas as colunas exceto as especificadas
ALTER TABLE byd.byd_view_div
DROP COLUMN IF EXISTS column1,
DROP COLUMN IF EXISTS column2,
DROP COLUMN IF EXISTS column3;

-- Para gerar o script correto, você precisaria saber o nome de todas as colunas da tabela
-- Você pode obter essa lista executando:
-- SELECT column_name 
-- FROM information_schema.columns 
-- WHERE table_schema = 'byd' AND table_name = 'byd_view_div'
-- E então gerar DROP COLUMN para cada coluna que NÃO está na sua lista de exceções

-- Script para gerar os comandos DROP automaticamente:
SELECT 
    'DROP COLUMN IF EXISTS ' || column_name || ','
FROM information_schema.columns
WHERE table_schema = 'byd' 
  AND table_name = 'byd_view_div'
  AND column_name NOT IN (
    'idnfsexterno', 
    'revenda', 
    'dta_processamento', 
    'proposta', 
    'chassi', 
    'des_modelo', 
    'val_modalidade', 
    'lucbru', 
    'bonus', 
    'ano_modelo_formatado', 
    'dias_em_estoque', 
    'apontamento', 
    'valor_bonus', 
    'rebate', 
    'reembolso_ipva', 
    'comissao_vd', 
    'trade', 
    'opt_comercial', 
    'campanha', 
    'detalhes', 
    'bonus_utilizado', 
    'bonus_dpto', 
    'rebate_dpto', 
    'ipva_dpto', 
    'trade_mkt_dpto'
  );