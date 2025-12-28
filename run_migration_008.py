"""
Executa a migration 008: Produtos de Cliente e Rateio de Receitas
"""
import sys
sys.path.append('.')

from database import DatabaseManager

def upgrade(cursor):
    """Aplica as mudanças do banco de dados"""
    # 1. Criar tabela de rateio
    print("Criando tabela contas_receber_rateio...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas_receber_rateio (
        id INT AUTO_INCREMENT PRIMARY KEY,
        conta_receber_id INT NOT NULL COMMENT 'Receita original (sem produto)',
        cliente_produto_id INT NOT NULL COMMENT 'Produto que recebe parte do valor',
        tipo_rateio ENUM('percentual', 'valor') NOT NULL DEFAULT 'percentual',
        percentual DECIMAL(5,2) NULL COMMENT 'Percentual do rateio (ex: 24.00)',
        valor_fixo DECIMAL(15,2) NULL COMMENT 'Valor fixo do rateio',
        valor_rateado DECIMAL(15,2) NOT NULL COMMENT 'Valor final calculado',
        observacoes TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INT NULL,
        INDEX idx_conta_receber (conta_receber_id),
        INDEX idx_cliente_produto (cliente_produto_id),
        FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id) ON DELETE CASCADE,
        FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE RESTRICT,
        CONSTRAINT chk_percentual CHECK (percentual IS NULL OR (percentual > 0 AND percentual <= 100)),
        CONSTRAINT chk_valor_fixo CHECK (valor_fixo IS NULL OR valor_fixo > 0)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    COMMENT='Rateio de Receitas entre Produtos do Cliente'
    """)
    
    # 2. Alterar cliente_produtos
    print("Alterando tabela cliente_produtos...")
    try:
        cursor.execute("ALTER TABLE cliente_produtos DROP COLUMN valor")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE cliente_produtos ADD COLUMN codigo VARCHAR(50) NULL AFTER nome")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE cliente_produtos ADD COLUMN is_active BOOLEAN DEFAULT TRUE AFTER descricao")
    except:
        pass
    
    # 3. Adicionar produto e rateio em contas_receber
    print("Alterando tabela contas_receber...")
    try:
        cursor.execute("ALTER TABLE contas_receber ADD COLUMN cliente_produto_id INT NULL AFTER cliente_id")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE contas_receber ADD COLUMN is_rateada BOOLEAN DEFAULT FALSE AFTER status")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE contas_receber ADD INDEX idx_cliente_produto (cliente_produto_id)")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE contas_receber ADD INDEX idx_is_rateada (is_rateada)")
    except:
        pass
    
    try:
        cursor.execute("""
        ALTER TABLE contas_receber 
        ADD CONSTRAINT fk_contas_receber_cliente_produto 
        FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL
        """)
    except:
        pass
    
    # 4. Adicionar produto em contas_pagar
    print("Alterando tabela contas_pagar...")
    try:
        cursor.execute("ALTER TABLE contas_pagar ADD COLUMN cliente_produto_id INT NULL AFTER fornecedor_id")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE contas_pagar ADD INDEX idx_cliente_produto_pagar (cliente_produto_id)")
    except:
        pass
    
    try:
        cursor.execute("""
        ALTER TABLE contas_pagar 
        ADD CONSTRAINT fk_contas_pagar_cliente_produto 
        FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL
        """)
    except:
        pass
    
    # 5. Adicionar produto em lancamentos_manuais
    print("Alterando tabela lancamentos_manuais...")
    try:
        cursor.execute("ALTER TABLE lancamentos_manuais ADD COLUMN cliente_produto_id INT NULL AFTER cliente_id")
    except:
        pass
    
    try:
        cursor.execute("ALTER TABLE lancamentos_manuais ADD INDEX idx_cliente_produto_lanc (cliente_produto_id)")
    except:
        pass
    
    try:
        cursor.execute("""
        ALTER TABLE lancamentos_manuais 
        ADD CONSTRAINT fk_lancamentos_cliente_produto 
        FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL
        """)
    except:
        pass
    
    print("Migration 008 aplicada com sucesso!")


def main():
    print("=" * 60)
    print("EXECUTANDO MIGRATION 008: Produtos Cliente e Rateio")
    print("=" * 60)
    
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            upgrade(cursor)
            conn.commit()
            print("\n" + "=" * 60)
            print("✅ MIGRATION 008 CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
        except Exception as e:
            conn.rollback()
            print("\n" + "=" * 60)
            print(f"❌ ERRO AO EXECUTAR MIGRATION 008: {e}")
            print("=" * 60)
            raise

if __name__ == '__main__':
    main()
