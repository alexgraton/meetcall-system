"""
Migração 010: Alterar campo de plano_conta_id para tipo_servico_id
Renomeia o campo de categoria para usar tipos_servicos ao invés de plano_contas
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

def run():
    """Executa a migração"""
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("=== Migração 010: Alterar categoria para tipo_servico_id ===")
        
        # 1. Alterar tabela clientes
        print("1. Alterando tabela clientes...")
        
        # Remover FK antiga se existir
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'clientes' 
            AND COLUMN_NAME = 'plano_conta_id'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        fk_result = cursor.fetchone()
        if fk_result:
            fk_name = fk_result[0]
            print(f"   - Removendo FK antiga: {fk_name}")
            cursor.execute(f"ALTER TABLE clientes DROP FOREIGN KEY {fk_name}")
        
        # Verificar se a coluna tipo_servico_id já existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'clientes' 
            AND COLUMN_NAME = 'tipo_servico_id'
        """)
        if cursor.fetchone():
            print("   - Coluna tipo_servico_id já existe em clientes")
        else:
            # Renomear coluna
            print("   - Renomeando plano_conta_id para tipo_servico_id")
            cursor.execute("""
                ALTER TABLE clientes 
                CHANGE COLUMN plano_conta_id tipo_servico_id INT NULL
            """)
        
        # Adicionar FK nova
        print("   - Adicionando FK para tipos_servicos")
        cursor.execute("""
            ALTER TABLE clientes 
            ADD CONSTRAINT fk_clientes_tipo_servico 
            FOREIGN KEY (tipo_servico_id) 
            REFERENCES tipos_servicos(id) 
            ON DELETE SET NULL
        """)
        
        # 2. Alterar tabela fornecedores
        print("2. Alterando tabela fornecedores...")
        
        # Remover FK antiga se existir
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'fornecedores' 
            AND COLUMN_NAME = 'plano_conta_id'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        fk_result = cursor.fetchone()
        if fk_result:
            fk_name = fk_result[0]
            print(f"   - Removendo FK antiga: {fk_name}")
            cursor.execute(f"ALTER TABLE fornecedores DROP FOREIGN KEY {fk_name}")
        
        # Verificar se a coluna tipo_servico_id já existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'fornecedores' 
            AND COLUMN_NAME = 'tipo_servico_id'
        """)
        if cursor.fetchone():
            print("   - Coluna tipo_servico_id já existe em fornecedores")
        else:
            # Renomear coluna
            print("   - Renomeando plano_conta_id para tipo_servico_id")
            cursor.execute("""
                ALTER TABLE fornecedores 
                CHANGE COLUMN plano_conta_id tipo_servico_id INT NULL
            """)
        
        # Adicionar FK nova
        print("   - Adicionando FK para tipos_servicos")
        cursor.execute("""
            ALTER TABLE fornecedores 
            ADD CONSTRAINT fk_fornecedores_tipo_servico 
            FOREIGN KEY (tipo_servico_id) 
            REFERENCES tipos_servicos(id) 
            ON DELETE SET NULL
        """)
        
        conn.commit()
        print("✓ Migração 010 concluída com sucesso!")

if __name__ == '__main__':
    run()
