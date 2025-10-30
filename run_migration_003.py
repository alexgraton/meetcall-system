"""
Script para executar a migration 003 (Contas a Receber)
"""
from database import DatabaseManager

CREATE_CONTAS_RECEBER = """
CREATE TABLE IF NOT EXISTS contas_receber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Relacionamentos
    cliente_id INT NOT NULL,
    filial_id INT NULL,
    tipo_servico_id INT NULL,
    centro_custo_id INT NULL,
    conta_contabil_id INT NULL COMMENT 'Plano de Contas (Receita)',
    
    -- Informacoes Principais
    descricao VARCHAR(255) NOT NULL,
    numero_documento VARCHAR(100) NULL COMMENT 'Numero da NF, recibo, etc',
    
    -- Valores
    valor_total DECIMAL(15,2) NOT NULL,
    valor_pago DECIMAL(15,2) DEFAULT 0.00,
    valor_desconto DECIMAL(15,2) DEFAULT 0.00,
    valor_juros DECIMAL(15,2) DEFAULT 0.00,
    valor_multa DECIMAL(15,2) DEFAULT 0.00,
    
    -- Datas
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_recebimento DATE NULL,
    
    -- Parcelamento
    numero_parcelas INT DEFAULT 1,
    parcela_atual INT DEFAULT 1,
    intervalo_parcelas INT DEFAULT 30 COMMENT 'Dias entre parcelas',
    
    -- Encargos
    percentual_juros DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Juros ao dia',
    percentual_multa DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Multa por atraso',
    
    -- Recorrencia
    is_recorrente BOOLEAN DEFAULT FALSE,
    recorrencia_tipo ENUM('mensal', 'trimestral', 'semestral', 'anual') NULL,
    
    -- Status e Controle
    status ENUM('pendente', 'vencido', 'recebido', 'cancelado') DEFAULT 'pendente',
    observacoes TEXT NULL,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NULL,
    
    -- Indices
    INDEX idx_cliente (cliente_id),
    INDEX idx_filial (filial_id),
    INDEX idx_status (status),
    INDEX idx_data_vencimento (data_vencimento),
    INDEX idx_data_recebimento (data_recebimento),
    
    -- Chaves estrangeiras
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (conta_contabil_id) REFERENCES plano_contas(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contas a Receber de Clientes';
"""

CREATE_ANEXOS = """
CREATE TABLE IF NOT EXISTS anexos_contas_receber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_receber_id INT NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho_arquivo VARCHAR(500) NOT NULL,
    tipo_arquivo VARCHAR(50) NULL,
    tamanho_bytes INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id) ON DELETE CASCADE,
    INDEX idx_conta (conta_receber_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Anexos das Contas a Receber (NFs, comprovantes, etc)';
"""

def main():
    print("=" * 60)
    print("MIGRATION 003: Contas a Receber")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Executar migration
            print("Criando tabela contas_receber...")
            cursor.execute(CREATE_CONTAS_RECEBER)
            print("✓ Tabela contas_receber criada")
            
            print("Criando tabela anexos_contas_receber...")
            cursor.execute(CREATE_ANEXOS)
            print("✓ Tabela anexos_contas_receber criada")
            
            conn.commit()
            print("\n✅ Migration 003 executada com sucesso!")
            
    except Exception as e:
        print(f"\n❌ Erro ao executar migration: {e}")
        raise

if __name__ == "__main__":
    main()
