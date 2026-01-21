"""
Migration 006 - Conciliação Bancária
Adiciona tabelas para controle de conciliação bancária
"""

def up(db):
    """Executa a migration"""
    
    # 1. Tabela de conciliações (histórico de importações)
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS conciliacoes_bancarias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conta_bancaria_id INT NOT NULL,
            nome_arquivo VARCHAR(255) NOT NULL,
            data_importacao DATETIME NOT NULL,
            periodo_inicio DATE,
            periodo_fim DATE,
            total_transacoes INT DEFAULT 0,
            total_conciliadas INT DEFAULT 0,
            total_pendentes INT DEFAULT 0,
            status ENUM('processando', 'concluida', 'erro') DEFAULT 'processando',
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id) ON DELETE CASCADE,
            INDEX idx_conta_bancaria (conta_bancaria_id),
            INDEX idx_data_importacao (data_importacao),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # 2. Tabela de transações importadas do extrato
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS transacoes_extrato (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conciliacao_id INT NOT NULL,
            data_transacao DATE NOT NULL,
            descricao VARCHAR(500) NOT NULL,
            documento VARCHAR(100),
            valor DECIMAL(15,2) NOT NULL,
            tipo ENUM('debito', 'credito') NOT NULL,
            saldo_apos DECIMAL(15,2),
            status_conciliacao ENUM('pendente', 'conciliada', 'ignorada') DEFAULT 'pendente',
            transacao_relacionada_tipo ENUM('contas_pagar', 'contas_receber', 'lancamento_manual'),
            transacao_relacionada_id INT,
            similaridade DECIMAL(5,2) COMMENT 'Percentual de similaridade com transação sugerida',
            conciliado_em DATETIME,
            conciliado_por INT COMMENT 'ID do usuário que fez a conciliação',
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (conciliacao_id) REFERENCES conciliacoes_bancarias(id) ON DELETE CASCADE,
            INDEX idx_conciliacao (conciliacao_id),
            INDEX idx_data_transacao (data_transacao),
            INDEX idx_status (status_conciliacao),
            INDEX idx_tipo (tipo),
            INDEX idx_transacao_relacionada (transacao_relacionada_tipo, transacao_relacionada_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    
    # 3. Adicionar campo de conciliação nas contas a pagar
    db.execute_query("""
        ALTER TABLE contas_pagar
        ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
        ADD COLUMN conciliacao_data DATETIME,
        ADD COLUMN transacao_extrato_id INT,
        ADD INDEX idx_conciliado (conciliado)
    """)
    
    # 4. Adicionar campo de conciliação nas contas a receber
    db.execute_query("""
        ALTER TABLE contas_receber
        ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
        ADD COLUMN conciliacao_data DATETIME,
        ADD COLUMN transacao_extrato_id INT,
        ADD INDEX idx_conciliado (conciliado)
    """)
    
    # 5. Adicionar campo de conciliação nos lançamentos manuais
    db.execute_query("""
        ALTER TABLE lancamentos_manuais
        ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
        ADD COLUMN conciliacao_data DATETIME,
        ADD COLUMN transacao_extrato_id INT,
        ADD INDEX idx_conciliado (conciliado)
    """)
    
    print("Migration 006 executada com sucesso!")
    print("- Tabela conciliacoes_bancarias criada")
    print("- Tabela transacoes_extrato criada")
    print("- Campos de conciliação adicionados em contas_pagar, contas_receber e lancamentos_manuais")


def down(db):
    """Reverte a migration"""
    
    # Remover campos de conciliação das tabelas
    db.execute_query("""
        ALTER TABLE lancamentos_manuais
        DROP COLUMN IF EXISTS conciliado,
        DROP COLUMN IF EXISTS conciliacao_data,
        DROP COLUMN IF EXISTS transacao_extrato_id
    """)
    
    db.execute_query("""
        ALTER TABLE contas_receber
        DROP COLUMN IF EXISTS conciliado,
        DROP COLUMN IF EXISTS conciliacao_data,
        DROP COLUMN IF EXISTS transacao_extrato_id
    """)
    
    db.execute_query("""
        ALTER TABLE contas_pagar
        DROP COLUMN IF EXISTS conciliado,
        DROP COLUMN IF EXISTS conciliacao_data,
        DROP COLUMN IF EXISTS transacao_extrato_id
    """)
    
    # Remover tabelas
    db.execute_query("DROP TABLE IF EXISTS transacoes_extrato")
    db.execute_query("DROP TABLE IF EXISTS conciliacoes_bancarias")
    
    print("Migration 006 revertida com sucesso!")
