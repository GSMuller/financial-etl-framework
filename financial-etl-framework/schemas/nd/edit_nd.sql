-- =========================================
-- UPDATE: Alterar valor de uma Nota de Débito
-- =========================================
-- Exemplo: Alterar o valor da ND 7-2025-053
-- Substitua os valores conforme necessário

-- 1. Verificar dados atuais da ND
SELECT 
    id,
    numero_nd,
    valor AS valor_atual,
    data_emissao,
    descricao,
    filial_id
FROM gerador_nd.notadebito
WHERE numero_nd = '7-2025-053';

-- 2. Atualizar o valor da ND
UPDATE gerador_nd.notadebito
SET valor = 352000.00  -- NOVO VALOR AQUI
WHERE numero_nd = '7-2025-053';

-- 3. Verificar alteração
SELECT 
    id,
    numero_nd,
    valor AS valor_novo,
    data_emissao,
    descricao,
    filial_id
FROM gerador_nd.notadebito
WHERE numero_nd = '7-2025-053';

-- =========================================
-- TEMPLATE GENÉRICO:
-- =========================================
/*
UPDATE gerador_nd.notadebito
SET valor_atual = [NOVO_VALOR]
WHERE numero_nd = '[NUMERO_ND]';
*/
