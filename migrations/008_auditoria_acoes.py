"""
Migration 008: Adicionar tipos de ação na tabela de auditoria
Adiciona 'login', 'logout' e 'view' aos tipos de ação permitidos
"""

def up(connection):
    """Aplica a migração"""
    cursor = connection.cursor()
    
    print("Alterando tabela auditoria para adicionar novos tipos de ação...")
    
    # Alterar o ENUM para incluir os novos tipos
    alter_query = """
        ALTER TABLE auditoria 
        MODIFY COLUMN acao ENUM('insert', 'update', 'delete', 'login', 'logout', 'view') NOT NULL
    """
    
    cursor.execute(alter_query)
    connection.commit()
    
    print("✓ Tabela auditoria atualizada com sucesso!")
    print("  - Tipos de ação disponíveis: insert, update, delete, login, logout, view")

def down(connection):
    """Reverte a migração"""
    cursor = connection.cursor()
    
    print("Revertendo alteração na tabela auditoria...")
    
    # Voltar para o ENUM original
    alter_query = """
        ALTER TABLE auditoria 
        MODIFY COLUMN acao ENUM('insert', 'update', 'delete') NOT NULL
    """
    
    cursor.execute(alter_query)
    connection.commit()
    
    print("✓ Tabela auditoria revertida!")

if __name__ == '__main__':
    import sys
    import os
    
    # Adicionar o diretório pai ao path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database import db
    
    print("=== Migration 008: Auditoria - Novos tipos de ação ===\n")
    
    with db.get_connection() as conn:
        try:
            up(conn)
            print("\n✓ Migration aplicada com sucesso!")
        except Exception as e:
            print(f"\n✗ Erro ao aplicar migration: {e}")
            conn.rollback()
            raise
