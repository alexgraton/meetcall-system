"""
Migration 009: Adicionar categoria padrão para clientes e fornecedores
Adiciona campo plano_conta_id nas tabelas clientes e fornecedores
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

def run():
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("Executando Migration 009: Categoria padrão para clientes e fornecedores...")
        
        try:
            # Adicionar coluna plano_conta_id em clientes
            cursor.execute("""
                ALTER TABLE clientes 
                ADD COLUMN plano_conta_id INT DEFAULT NULL,
                ADD CONSTRAINT fk_clientes_plano_conta 
                    FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id) 
                    ON DELETE SET NULL
            """)
            print("✓ Coluna plano_conta_id adicionada em clientes")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ Coluna plano_conta_id já existe em clientes")
            else:
                print(f"✗ Erro ao adicionar coluna em clientes: {e}")
        
        try:
            # Adicionar coluna plano_conta_id em fornecedores
            cursor.execute("""
                ALTER TABLE fornecedores 
                ADD COLUMN plano_conta_id INT DEFAULT NULL,
                ADD CONSTRAINT fk_fornecedores_plano_conta 
                    FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id) 
                    ON DELETE SET NULL
            """)
            print("✓ Coluna plano_conta_id adicionada em fornecedores")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠ Coluna plano_conta_id já existe em fornecedores")
            else:
                print(f"✗ Erro ao adicionar coluna em fornecedores: {e}")
        
        conn.commit()
        print("✅ Migration 009 concluída com sucesso!")

if __name__ == '__main__':
    run()
