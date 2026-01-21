"""
Script para executar a migration 004 (Lancamentos Manuais)
"""
from database import DatabaseManager

CREATE_LANCAMENTOS_MANUAIS = """
CREATE TABLE IF NOT EXISTS lancamentos_manuais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Tipo e Classificacao
    tipo ENUM('despesa', 'receita') NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    
    -- Vinculos Opcionais
    filial_id INT NULL,
    tipo_servico_id INT NULL,
    centro_custo_id INT NULL,
    conta_contabil_id INT NULL COMMENT 'Plano de Contas (Despesa ou Receita)',
    fornecedor_id INT NULL COMMENT 'Opcional - para despesas',
    cliente_id INT NULL COMMENT 'Opcional - para receitas',
    
    -- Valores e Datas
    valor DECIMAL(15,2) NOT NULL,
    data_lancamento DATE NOT NULL,
    data_competencia DATE NULL COMMENT 'Mes/ano de competencia do lancamento',
    
    -- Informacoes Adicionais
    numero_documento VARCHAR(100) NULL,
    forma_pagamento ENUM('dinheiro', 'pix', 'transferencia', 'debito', 'credito', 'boleto', 'cheque', 'outros') NULL,
    observacoes TEXT NULL,
    
    -- Controle
    status ENUM('ativo', 'cancelado') DEFAULT 'ativo',
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NULL,
    
    -- Indices
    INDEX idx_tipo (tipo),
    INDEX idx_filial (filial_id),
    INDEX idx_data_lancamento (data_lancamento),
    INDEX idx_data_competencia (data_competencia),
    INDEX idx_status (status),
    
    -- Chaves estrangeiras
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (conta_contabil_id) REFERENCES plano_contas(id) ON DELETE SET NULL,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Lancamentos Manuais de Despesas e Receitas';
"""

def main():
    print("=" * 60)
    print("MIGRATION 004: Lancamentos Manuais")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("Criando tabela lancamentos_manuais...")
            cursor.execute(CREATE_LANCAMENTOS_MANUAIS)
            print("✓ Tabela lancamentos_manuais criada")
            
            conn.commit()
            print("\n✅ Migration 004 executada com sucesso!")
            
    except Exception as e:
        print(f"\n❌ Erro ao executar migration: {e}")
        raise

if __name__ == "__main__":
    main()
