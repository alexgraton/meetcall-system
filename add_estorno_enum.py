from database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== ADICIONANDO 'estorno' AO ENUM ===\n")
    
    print("1. Verificando valores atuais...")
    cursor.execute("SHOW COLUMNS FROM auditoria WHERE Field = 'acao'")
    col = cursor.fetchone()
    print(f"   Valores atuais: {col[1]}\n")
    
    print("2. Adicionando 'estorno'...")
    cursor.execute("""
        ALTER TABLE auditoria 
        MODIFY COLUMN acao ENUM('insert','update','delete','login','logout','view','estorno') NOT NULL
    """)
    print("   ✓ 'estorno' adicionado\n")
    
    print("3. Verificando novos valores...")
    cursor.execute("SHOW COLUMNS FROM auditoria WHERE Field = 'acao'")
    col = cursor.fetchone()
    print(f"   Novos valores: {col[1]}\n")
    
    conn.commit()
    
print("=" * 50)
print("✅ ENUM ATUALIZADO COM SUCESSO!")
print("=" * 50)
