"""Verifica estrutura da tabela tipos_servicos"""
from database import DatabaseManager

dm = DatabaseManager()
with dm.get_connection() as db:
    cursor = db.cursor()
    cursor.execute("DESCRIBE tipos_servicos")
    print("\n=== Estrutura da tabela tipos_servicos ===\n")
    for row in cursor.fetchall():
        print(row)
