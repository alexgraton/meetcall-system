"""Verifica tabelas no banco"""
from database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tabelas = [t[0] for t in cur.fetchall()]
    print("\n=== Tabelas existentes ===")
    for t in tabelas:
        print(f"  - {t}")
    print()
    
    # Verificar se fornecedores existe
    if 'fornecedores' in tabelas:
        print("✅ Tabela 'fornecedores' já existe")
    else:
        print("❌ Tabela 'fornecedores' NÃO existe - precisa criar migration")
