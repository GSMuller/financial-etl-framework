-- Consulta SQL para filtrar os dados com apontamento 'Revisar Divergência!' :
-- para os meses de Agosto a Dezembro

SELECT * FROM byd.bonus_view
WHERE dta_processamento BETWEEN '2025-08-01' AND '2026-05-30'
                AND apontamento = 'Revisar Divergência!';