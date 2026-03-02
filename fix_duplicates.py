from database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== RESOLVENDO DUPLICATAS ===\n")
    
    # Deletar registros inativos que são duplicatas
    print("1. Removendo duplicatas inativas...")
    cursor.execute("DELETE FROM tipos_servicos WHERE id IN (85, 36)")
    print(f"   ✓ {cursor.rowcount} registros removidos\n")
    
    # Aplicar UNIQUE constraint
    print("2. Aplicando UNIQUE constraint...")
    try:
        cursor.execute("ALTER TABLE tipos_servicos ADD UNIQUE INDEX idx_nome_unique (nome)")
        print("   ✓ UNIQUE constraint adicionada com sucesso!\n")
    except Exception as e:
        print(f"   ⚠️  Erro: {e}\n")
    
    conn.commit()
    
print("=" * 50)
print("✅ DUPLICATAS RESOLVIDAS!")
print("=" * 50)
