from database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contas_pagar')
    conn.commit()
    print(f'✅ Deletadas {cursor.rowcount} contas a pagar')
