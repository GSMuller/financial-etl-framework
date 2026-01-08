-- Consulta SQL para filtrar os dados com apontamento 'Revisar Divergência!' :
-- para os meses de Agosto a Dezembro

SELECT * FROM byd.bonus_view
WHERE dta_processamento BETWEEN '2026-01-01' AND '2026-12-31'
                AND apontamento = 'Revisar Divergência!';