"""
Script para executar a migration 006 - Conciliação Bancária
"""
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def main():
    """Executa a migration 006"""
    db = DatabaseManager()
    
    print("Executando migration 006 - Conciliação Bancária...")
    print("-" * 60)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabela de conciliações
            print("Criando tabela conciliacoes_bancarias...")
            cursor.execute("""
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
            print("✓ Tabela conciliacoes_bancarias criada")
            
            # 2. Tabela de transações do extrato
            print("Criando tabela transacoes_extrato...")
            cursor.execute("""
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
            print("✓ Tabela transacoes_extrato criada")
            
            # 3. Adicionar campos nas contas a pagar
            print("Adicionando campos de conciliação em contas_pagar...")
            try:
                cursor.execute("""
                    ALTER TABLE contas_pagar
                    ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
                    ADD COLUMN conciliacao_data DATETIME,
                    ADD COLUMN transacao_extrato_id INT,
                    ADD INDEX idx_conciliado (conciliado)
                """)
                print("✓ Campos adicionados em contas_pagar")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠ Campos já existem em contas_pagar")
                else:
                    raise
            
            # 4. Adicionar campos nas contas a receber
            print("Adicionando campos de conciliação em contas_receber...")
            try:
                cursor.execute("""
                    ALTER TABLE contas_receber
                    ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
                    ADD COLUMN conciliacao_data DATETIME,
                    ADD COLUMN transacao_extrato_id INT,
                    ADD INDEX idx_conciliado (conciliado)
                """)
                print("✓ Campos adicionados em contas_receber")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠ Campos já existem em contas_receber")
                else:
                    raise
            
            # 5. Adicionar campos nos lançamentos manuais
            print("Adicionando campos de conciliação em lancamentos_manuais...")
            try:
                cursor.execute("""
                    ALTER TABLE lancamentos_manuais
                    ADD COLUMN conciliado TINYINT(1) DEFAULT 0,
                    ADD COLUMN conciliacao_data DATETIME,
                    ADD COLUMN transacao_extrato_id INT,
                    ADD INDEX idx_conciliado (conciliado)
                """)
                print("✓ Campos adicionados em lancamentos_manuais")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠ Campos já existem em lancamentos_manuais")
                else:
                    raise
            
            conn.commit()
            cursor.close()
            
            print("-" * 60)
            print("✓ Migration 006 executada com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro ao executar migration: {e}")
        raise


if __name__ == "__main__":
    main()
