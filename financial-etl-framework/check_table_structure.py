"""Script temporario para verificar estrutura da bonus_view"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.financial_etl.conn import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verifica colunas da tabela
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'byd' 
    AND table_name = 'bonus_view'
    ORDER BY ordinal_position
""")

print("\n=== COLUNAS DA TABELA byd.bonus_view ===\n")
for col_name, data_type in cursor.fetchall():
    print(f"{col_name:30} {data_type}")

cursor.close()
conn.close()
