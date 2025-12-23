"""
Migration 007: Ajustar Tipos de Serviços para Call Center de Cobrança
- Remove campos aliquota e margem_esperada (não aplicáveis ao modelo de negócio)
- Tipos de Serviços representa categorias de despesas operacionais
"""

def migrate(db):
    """Executa a migração"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Iniciando migração 007: Ajuste para Call Center...")
        
        # Remover colunas aliquota e margem_esperada da tabela tipos_servicos
        print("   ➜ Removendo colunas aliquota e margem_esperada...")
        
        cursor.execute("""
            ALTER TABLE tipos_servicos 
            DROP COLUMN aliquota
        """)
        print("   ✓ Coluna 'aliquota' removida")
        
        cursor.execute("""
            ALTER TABLE tipos_servicos 
            DROP COLUMN margem_esperada
        """)
        print("   ✓ Coluna 'margem_esperada' removida")
        
        conn.commit()
        print("✅ Migração 007 concluída com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro na migração 007: {str(e)}")
        return False
        
    finally:
        cursor.close()


if __name__ == '__main__':
    from database import DatabaseManager
    db = DatabaseManager()
    migrate(db)
