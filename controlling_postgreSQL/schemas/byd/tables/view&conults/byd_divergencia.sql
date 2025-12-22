-- Consulta SQL para filtrar os dados de interesse

SELECT * FROM byd.bonus_view
WHERE competencia IN ('Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')
                AND apontamento = 'Revisar Divergência!';