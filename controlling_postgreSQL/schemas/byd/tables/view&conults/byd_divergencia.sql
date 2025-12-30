-- Consulta SQL para filtrar os dados com apontamento 'Revisar Divergência!' :
-- para os meses de Agosto a Dezembro

SELECT * FROM byd.bonus_view
WHERE competencia IN ('Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')
                AND apontamento = 'Revisar Divergência!';