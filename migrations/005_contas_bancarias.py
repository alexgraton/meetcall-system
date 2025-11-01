"""
Migration 005: Contas Bancárias
Cria tabela para gerenciar contas bancárias da empresa (saldo, agência, conta, tipo)
"""

CREATE_CONTAS_BANCARIAS = """
CREATE TABLE IF NOT EXISTS contas_bancarias (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Identificação
    banco VARCHAR(100) NOT NULL,
    agencia VARCHAR(50) NOT NULL,
    numero_conta VARCHAR(100) NOT NULL,
    tipo_conta ENUM('corrente','poupanca','caixa') DEFAULT 'corrente',
    descricao VARCHAR(255) NULL,

    -- Saldo e moeda
    saldo_inicial DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    saldo_atual DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    moeda VARCHAR(10) DEFAULT 'BRL',

    -- Vinculo opcional
    filial_id INT NULL,

    -- Controle
    ativo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NULL,

    -- Indices
    INDEX idx_filial (filial_id),
    INDEX idx_banco (banco),

    -- Chaves estrangeiras
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contas Bancárias da empresa (contas correntes, poupança, caixa)';
"""


def upgrade(cursor):
    """Aplica a migration: cria a tabela contas_bancarias"""
    print("Criando tabela contas_bancarias...")
    cursor.execute(CREATE_CONTAS_BANCARIAS)
    print("✓ Tabela contas_bancarias criada")


def downgrade(cursor):
    """Reverte a migration: remove a tabela contas_bancarias"""
    print("Removendo tabela contas_bancarias...")
    cursor.execute("DROP TABLE IF EXISTS contas_bancarias")
    print("✓ Tabela contas_bancarias removida")
