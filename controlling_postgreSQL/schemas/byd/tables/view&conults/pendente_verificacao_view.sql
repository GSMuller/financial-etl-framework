-- Consulta SQL para filtrar os CASOS QUE ESTÃO PENDENTES DE VERIFICAÇÃO

SELECT * FROM byd.bonus_view
WHERE competencia IN ('Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')
                AND bonus_utilizado = 'PENDENTE VERIFICACAO';