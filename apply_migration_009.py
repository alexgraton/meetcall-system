from database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== APLICANDO MIGRATION 009 ===\n")
    
    # 1. Verificar duplicatas
    print("1. Verificando duplicatas em tipos_servicos...")
    cursor.execute("SELECT nome, COUNT(*) FROM tipos_servicos GROUP BY nome HAVING COUNT(*) > 1")
    dups = cursor.fetchall()
    print(f"   Duplicatas encontradas: {len(dups)}\n")
    
    # 2. UNIQUE constraint
    print("2. Aplicando UNIQUE constraint...")
    try:
        cursor.execute("ALTER TABLE tipos_servicos ADD UNIQUE INDEX idx_nome_unique (nome)")
        print("   ✓ UNIQUE constraint adicionada\n")
    except Exception as e:
        print(f"   ℹ️  {str(e)[:100]}\n")
    
    # 3. Campo prazo_dias
    print("3. Adicionando campo prazo_dias...")
    try:
        cursor.execute("ALTER TABLE contas_receber ADD COLUMN prazo_dias INT DEFAULT 30 AFTER data_emissao")
        print("   ✓ Campo adicionado\n")
    except Exception as e:
        print(f"   ℹ️  {str(e)[:100]}\n")
    
    # 4. Atualizar registros existentes
    print("4. Atualizando registros existentes...")
    cursor.execute("UPDATE contas_receber SET prazo_dias = DATEDIFF(data_vencimento, data_emissao) WHERE prazo_dias IS NULL AND data_emissao IS NOT NULL")
    print(f"   ✓ {cursor.rowcount} registros atualizados\n")
    
    cursor.execute("UPDATE contas_receber SET prazo_dias = 30 WHERE prazo_dias IS NULL OR prazo_dias < 0")
    print(f"   ✓ {cursor.rowcount} registros corrigidos\n")
    
    conn.commit()

print("=" * 50)
print("✅ MIGRATION CONCLUÍDA!")
print("=" * 50)
