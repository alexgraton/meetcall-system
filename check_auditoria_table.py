from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('DESCRIBE auditoria')
    cols = cursor.fetchall()
    
    print("Estrutura da tabela auditoria:")
    print("-" * 80)
    for row in cols:
        print(f"{row[0]:20} {row[1]:30} {row[2]:10} {row[3]:10} {row[4]}")
