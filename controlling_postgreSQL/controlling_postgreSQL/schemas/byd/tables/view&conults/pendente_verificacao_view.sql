-- Consulta SQL para filtrar os CASOS QUE ESTÃO PENDENTES DE VERIFICAÇÃO


SELECT * FROM byd.bonus_view
WHERE dta_processamento BETWEEN '2026-01-01' AND '2026-12-31'
                AND bonus_utilizado = 'PENDENTE VERIFICACAO';