import sys

sys.path.append(r'c:\\Users\\giovanni.5683\\GITHUB\\controlling_postgreSQL')
from conn import get_connection # type: ignore

conn = get_connection()
conn.rollback()
