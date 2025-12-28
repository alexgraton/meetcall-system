"""
Migração 012: Tabelas para Conciliação Bancária
Data: 2025-12-27

Cria as tabelas necessárias para:
- Importar extratos bancários
- Fazer conciliação automática e manual
- Registrar divergências
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

def upgrade():
    """Aplica a migração"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("Iniciando migração 012 - Conciliação Bancária...")
        
        # 1. Tabela de extratos bancários importados
        print("1. Criando tabela extratos_bancarios...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extratos_bancarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conta_bancaria_id INT NOT NULL,
                
                -- Dados do lançamento
                data_lancamento DATE NOT NULL,
                data_processamento DATE NULL,
                documento VARCHAR(100),
                historico VARCHAR(500) NOT NULL,
                complemento TEXT,
                
                -- Valores
                valor DECIMAL(15,2) NOT NULL,
                tipo_movimento ENUM('credito', 'debito') NOT NULL,
                saldo_apos DECIMAL(15,2),
                
                -- Origem
                banco_origem VARCHAR(100),
                agencia_origem VARCHAR(20),
                codigo_historico VARCHAR(20),
                
                -- Controle de importação
                arquivo_origem VARCHAR(255) NOT NULL,
                linha_arquivo INT NOT NULL,
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importado_por INT,
                
                -- Status de conciliação
                conciliado BOOLEAN DEFAULT FALSE,
                data_conciliacao TIMESTAMP NULL,
                conciliado_por INT NULL,
                
                FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id),
                FOREIGN KEY (importado_por) REFERENCES users(id),
                FOREIGN KEY (conciliado_por) REFERENCES users(id),
                
                INDEX idx_conta_data (conta_bancaria_id, data_lancamento),
                INDEX idx_conciliado (conciliado),
                INDEX idx_valor (valor),
                INDEX idx_historico (historico(100))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 2. Tabela de conciliações
        print("2. Criando tabela conciliacoes...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conciliacoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                extrato_id INT NOT NULL,
                
                -- Referência ao lançamento do sistema
                tipo_lancamento ENUM('pagar', 'receber', 'manual', 'nenhum') NOT NULL,
                lancamento_id INT NULL COMMENT 'ID da conta_pagar ou conta_receber',
                
                -- Valores para comparação
                valor_extrato DECIMAL(15,2) NOT NULL,
                valor_sistema DECIMAL(15,2) NULL,
                diferenca DECIMAL(15,2) GENERATED ALWAYS AS (ABS(valor_extrato - COALESCE(valor_sistema, 0))) STORED,
                
                -- Status
                status ENUM('pendente', 'conciliado', 'divergente', 'ignorado') DEFAULT 'pendente',
                tipo_divergencia VARCHAR(100) NULL COMMENT 'Ex: valor_diferente, data_diferente, nao_encontrado',
                
                -- Observações
                observacao TEXT,
                
                -- Auditoria
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                conciliado_em TIMESTAMP NULL,
                conciliado_por INT NULL,
                
                FOREIGN KEY (extrato_id) REFERENCES extratos_bancarios(id) ON DELETE CASCADE,
                FOREIGN KEY (conciliado_por) REFERENCES users(id),
                
                INDEX idx_status (status),
                INDEX idx_lancamento (tipo_lancamento, lancamento_id),
                INDEX idx_extrato (extrato_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 3. Tabela de importações (log de arquivos importados)
        print("3. Criando tabela importacoes_extratos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS importacoes_extratos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conta_bancaria_id INT NOT NULL,
                
                -- Arquivo
                nome_arquivo VARCHAR(255) NOT NULL,
                caminho_arquivo VARCHAR(500),
                tipo_banco ENUM('itau', 'banco_brasil', 'bradesco', 'santander', 'outros') NOT NULL,
                
                -- Estatísticas
                total_linhas INT NOT NULL,
                linhas_processadas INT NOT NULL,
                linhas_erro INT DEFAULT 0,
                
                -- Período do extrato
                data_inicio DATE,
                data_fim DATE,
                
                -- Status
                status ENUM('processando', 'concluido', 'erro') DEFAULT 'processando',
                mensagem_erro TEXT,
                
                -- Auditoria
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importado_por INT NOT NULL,
                
                FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id),
                FOREIGN KEY (importado_por) REFERENCES users(id),
                
                INDEX idx_conta (conta_bancaria_id),
                INDEX idx_data_importacao (data_importacao),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        print("✓ Migração 012 concluída com sucesso!")
        print("")
        print("📌 Tabelas criadas:")
        print("   - extratos_bancarios: Lançamentos importados do banco")
        print("   - conciliacoes: Vínculo entre extrato e sistema")
        print("   - importacoes_extratos: Log de arquivos importados")
        print("")

def downgrade():
    """Reverte a migração"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("Revertendo migração 012...")
        
        cursor.execute("DROP TABLE IF EXISTS conciliacoes")
        cursor.execute("DROP TABLE IF EXISTS extratos_bancarios")
        cursor.execute("DROP TABLE IF EXISTS importacoes_extratos")
        
        conn.commit()
        print("✓ Migração 012 revertida")

if __name__ == '__main__':
    import sys
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            downgrade()
        else:
            upgrade()
    except Exception as e:
        print(f"❌ Erro na migração: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
