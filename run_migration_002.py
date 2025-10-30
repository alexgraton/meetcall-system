from database import DatabaseManager

CREATE_CONTAS_PAGAR = """
CREATE TABLE IF NOT EXISTS contas_pagar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    tipo_servico_id INT,
    centro_custo_id INT,
    conta_contabil_id INT,
    filial_id INT,
    
    -- Dados da conta
    descricao VARCHAR(255) NOT NULL,
    numero_documento VARCHAR(100),
    observacoes TEXT,
    
    -- Valores
    valor_total DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2) DEFAULT 0,
    
    -- Parcelamento
    numero_parcelas INT DEFAULT 1,
    parcela_atual INT DEFAULT 1,
    
    -- Recorrência
    recorrente BOOLEAN DEFAULT FALSE,
    tipo_recorrencia ENUM('mensal', 'trimestral', 'semestral', 'anual') NULL,
    
    -- Datas
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE NULL,
    
    -- Juros e multa
    percentual_juros DECIMAL(5,2) DEFAULT 0,
    percentual_multa DECIMAL(5,2) DEFAULT 0,
    valor_juros DECIMAL(10,2) DEFAULT 0,
    valor_multa DECIMAL(10,2) DEFAULT 0,
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    
    -- Status
    status ENUM('pendente', 'pago', 'vencido', 'cancelado') DEFAULT 'pendente',
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    
    -- Chaves estrangeiras
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id),
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id),
    FOREIGN KEY (conta_contabil_id) REFERENCES plano_contas(id),
    FOREIGN KEY (filial_id) REFERENCES filiais(id),
    
    INDEX idx_fornecedor (fornecedor_id),
    INDEX idx_vencimento (data_vencimento),
    INDEX idx_status (status),
    INDEX idx_filial (filial_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_ANEXOS = """
CREATE TABLE IF NOT EXISTS anexos_contas_pagar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_pagar_id INT NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho_arquivo VARCHAR(500) NOT NULL,
    tipo_arquivo VARCHAR(50),
    tamanho_bytes INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT,
    
    FOREIGN KEY (conta_pagar_id) REFERENCES contas_pagar(id) ON DELETE CASCADE,
    INDEX idx_conta_pagar (conta_pagar_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

if __name__ == '__main__':
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_CONTAS_PAGAR)
        cursor.execute(CREATE_ANEXOS)
        conn.commit()
        print("✓ Tabelas de Contas a Pagar criadas com sucesso")
