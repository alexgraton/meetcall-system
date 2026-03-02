from database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM auditoria WHERE Field = 'acao'")
    col = cursor.fetchone()
    print(f"Coluna acao atual: {col}")
    print(f"\nTipo: {col[1]}")
