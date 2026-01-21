from database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Verificar loops diretos (id = parent_id)
    cursor.execute('SELECT id, codigo, parent_id FROM plano_contas WHERE id = parent_id')
    loops = cursor.fetchall()
    print('Contas com loop direto (id = parent_id):', loops)
    
    # Contar total
    cursor.execute('SELECT COUNT(*) FROM plano_contas')
    total = cursor.fetchone()[0]
    print(f'Total de contas: {total}')
    
    # Verificar hierarquia
    cursor.execute('SELECT id, codigo, nivel, parent_id FROM plano_contas ORDER BY codigo LIMIT 20')
    print('\nPrimeiras 20 contas:')
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, Codigo: {row[1]}, Nivel: {row[2]}, Parent: {row[3]}')
