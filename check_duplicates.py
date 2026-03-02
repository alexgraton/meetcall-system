from database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    
    print("=== DUPLICATAS EM TIPOS_SERVICOS ===\n")
    
    cursor.execute("""
        SELECT id, nome, codigo, descricao, is_active 
        FROM tipos_servicos 
        WHERE nome IN (
            SELECT nome 
            FROM tipos_servicos 
            GROUP BY nome 
            HAVING COUNT(*) > 1
        ) 
        ORDER BY nome, id
    """)
    
    duplicatas = cursor.fetchall()
    
    for dup in duplicatas:
        print(f"ID: {dup['id']:3d} | Nome: {dup['nome']:20s} | Código: {dup['codigo']:10s} | Ativo: {dup['is_active']} | Desc: {dup['descricao']}")
    
    print(f"\nTotal de registros duplicados: {len(duplicatas)}")
