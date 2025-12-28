"""
Migration 008: Produtos de Cliente e Rateio de Receitas
Ajusta cliente_produtos para ser centro de resultado e cria sistema de rateio
"""

# 1. Criar tabela de rateio
CREATE_RATEIO_TABLE = """
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
COMMENT='Rateio de Receitas entre Produtos do Cliente';
"""

# 2. Alterar cliente_produtos
ALTER_CLIENTE_PRODUTOS = """
ALTER TABLE cliente_produtos 
  DROP COLUMN IF EXISTS valor,
  ADD COLUMN IF NOT EXISTS codigo VARCHAR(50) NULL AFTER nome,
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE AFTER descricao;
"""

# 3. Adicionar produto e rateio em contas_receber
ALTER_CONTAS_RECEBER = """
ALTER TABLE contas_receber 
  ADD COLUMN IF NOT EXISTS cliente_produto_id INT NULL AFTER cliente_id,
  ADD COLUMN IF NOT EXISTS is_rateada BOOLEAN DEFAULT FALSE AFTER status,
  ADD INDEX IF NOT EXISTS idx_cliente_produto (cliente_produto_id),
  ADD INDEX IF NOT EXISTS idx_is_rateada (is_rateada);
"""

ADD_FK_CONTAS_RECEBER = """
ALTER TABLE contas_receber 
  ADD CONSTRAINT fk_contas_receber_cliente_produto 
    FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL;
"""

# 4. Adicionar produto em contas_pagar
ALTER_CONTAS_PAGAR = """
ALTER TABLE contas_pagar 
  ADD COLUMN IF NOT EXISTS cliente_produto_id INT NULL AFTER fornecedor_id,
  ADD INDEX IF NOT EXISTS idx_cliente_produto (cliente_produto_id);
"""

ADD_FK_CONTAS_PAGAR = """
ALTER TABLE contas_pagar 
  ADD CONSTRAINT fk_contas_pagar_cliente_produto 
    FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL;
"""

# 5. Adicionar produto em lancamentos_manuais
ALTER_LANCAMENTOS = """
ALTER TABLE lancamentos_manuais 
  ADD COLUMN IF NOT EXISTS cliente_produto_id INT NULL AFTER cliente_id,
  ADD INDEX IF NOT EXISTS idx_cliente_produto (cliente_produto_id);
"""

ADD_FK_LANCAMENTOS = """
ALTER TABLE lancamentos_manuais 
  ADD CONSTRAINT fk_lancamentos_cliente_produto 
    FOREIGN KEY (cliente_produto_id) REFERENCES cliente_produtos(id) ON DELETE SET NULL;
"""

def upgrade(cursor):
    """Aplica as mudanças do banco de dados"""
    print("Criando tabela contas_receber_rateio...")
    cursor.execute(CREATE_RATEIO_TABLE)
    
    print("Alterando tabela cliente_produtos...")
    cursor.execute(ALTER_CLIENTE_PRODUTOS)
    
    print("Alterando tabela contas_receber...")
    cursor.execute(ALTER_CONTAS_RECEBER)
    try:
        cursor.execute(ADD_FK_CONTAS_RECEBER)
    except Exception as e:
        if "Duplicate" not in str(e):
            print(f"Aviso ao adicionar FK contas_receber: {e}")
    
    print("Alterando tabela contas_pagar...")
    cursor.execute(ALTER_CONTAS_PAGAR)
    try:
        cursor.execute(ADD_FK_CONTAS_PAGAR)
    except Exception as e:
        if "Duplicate" not in str(e):
            print(f"Aviso ao adicionar FK contas_pagar: {e}")
    
    print("Alterando tabela lancamentos_manuais...")
    cursor.execute(ALTER_LANCAMENTOS)
    try:
        cursor.execute(ADD_FK_LANCAMENTOS)
    except Exception as e:
        if "Duplicate" not in str(e):
            print(f"Aviso ao adicionar FK lancamentos: {e}")
    
    print("Migration 008 aplicada com sucesso!")

def downgrade(cursor):
    """Reverte as mudanças"""
    print("Revertendo migration 008...")
    cursor.execute("DROP TABLE IF EXISTS contas_receber_rateio")
    cursor.execute("ALTER TABLE contas_receber DROP FOREIGN KEY IF EXISTS fk_contas_receber_cliente_produto")
    cursor.execute("ALTER TABLE contas_receber DROP COLUMN IF EXISTS cliente_produto_id, DROP COLUMN IF EXISTS is_rateada")
    cursor.execute("ALTER TABLE contas_pagar DROP FOREIGN KEY IF EXISTS fk_contas_pagar_cliente_produto")
    cursor.execute("ALTER TABLE contas_pagar DROP COLUMN IF EXISTS cliente_produto_id")
    cursor.execute("ALTER TABLE lancamentos_manuais DROP FOREIGN KEY IF EXISTS fk_lancamentos_cliente_produto")
    cursor.execute("ALTER TABLE lancamentos_manuais DROP COLUMN IF EXISTS cliente_produto_id")
    cursor.execute("ALTER TABLE cliente_produtos ADD COLUMN IF NOT EXISTS valor DECIMAL(15,2) NULL, DROP COLUMN IF EXISTS codigo, DROP COLUMN IF EXISTS is_active")
    print("Migration 008 revertida!")

if __name__ == '__main__':
    import sys
    sys.path.append('.')
    from database import DatabaseManager
    
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            upgrade(cursor)
            conn.commit()
            print("✅ Migration executada com sucesso!")
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao executar migration: {e}")
            raise
