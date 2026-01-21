-- Migration 013: Sistema de Margem Operacional
-- Criado em: 2025-12-28
-- Descrição: Tabelas para controle de capacity e rateio de receitas/despesas por cliente/produto

-- Tabela de histórico de capacity (operadores por cliente/produto)
CREATE TABLE IF NOT EXISTS capacity_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    produto_id INT NULL,
    capacity_atual INT NOT NULL DEFAULT 0,
    capacity_necessario INT NOT NULL DEFAULT 0,
    percentual_variacao DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE 
            WHEN capacity_necessario > 0 
            THEN ((capacity_atual - capacity_necessario) / capacity_necessario) * 100
            ELSE 0
        END
    ) STORED,
    data_vigencia DATE NOT NULL,
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alteracao INT NOT NULL,
    observacoes TEXT,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES cliente_produtos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_alteracao) REFERENCES users(id),
    
    INDEX idx_cliente_data (cliente_id, data_vigencia),
    INDEX idx_produto_data (produto_id, data_vigencia),
    INDEX idx_data_vigencia (data_vigencia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Histórico de capacity (operadores) por cliente/produto';

-- Tabela de competências para controle de margem
CREATE TABLE IF NOT EXISTS margem_competencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competencia CHAR(7) NOT NULL UNIQUE COMMENT 'Formato: MM/YYYY',
    status ENUM('aberta', 'em_processamento', 'fechada') DEFAULT 'aberta',
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fechamento TIMESTAMP NULL,
    usuario_abertura INT NOT NULL,
    usuario_fechamento INT NULL,
    
    FOREIGN KEY (usuario_abertura) REFERENCES users(id),
    FOREIGN KEY (usuario_fechamento) REFERENCES users(id),
    
    INDEX idx_competencia (competencia),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Controle de competências (meses) para análise de margem';

-- Tabela de rateio de receitas
CREATE TABLE IF NOT EXISTS margem_rateio_receitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competencia_id INT NOT NULL,
    conta_receber_id INT NOT NULL,
    cliente_id INT NOT NULL,
    produto_id INT NULL COMMENT 'NULL = rateio no nível do cliente',
    percentual DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Percentual do rateio (0-100)',
    valor_rateado DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    data_rateio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_rateio INT NOT NULL,
    
    FOREIGN KEY (competencia_id) REFERENCES margem_competencias(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES cliente_produtos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_rateio) REFERENCES users(id),
    
    INDEX idx_competencia (competencia_id),
    INDEX idx_conta_receber (conta_receber_id),
    INDEX idx_cliente (cliente_id),
    INDEX idx_produto (produto_id),
    
    CONSTRAINT chk_percentual_receita CHECK (percentual >= 0 AND percentual <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Rateio de receitas por cliente/produto';

-- Tabela de rateio de despesas
CREATE TABLE IF NOT EXISTS margem_rateio_despesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competencia_id INT NOT NULL,
    conta_pagar_id INT NOT NULL,
    cliente_id INT NOT NULL,
    produto_id INT NULL COMMENT 'NULL = rateio no nível do cliente',
    tipo_rateio ENUM('percentual', 'valor_fixo', 'capacity') NOT NULL DEFAULT 'percentual',
    percentual DECIMAL(10,2) NULL COMMENT 'Usado quando tipo_rateio = percentual',
    valor_rateado DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    data_rateio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_rateio INT NOT NULL,
    observacoes TEXT,
    
    FOREIGN KEY (competencia_id) REFERENCES margem_competencias(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_pagar_id) REFERENCES contas_pagar(id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES cliente_produtos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_rateio) REFERENCES users(id),
    
    INDEX idx_competencia (competencia_id),
    INDEX idx_conta_pagar (conta_pagar_id),
    INDEX idx_cliente (cliente_id),
    INDEX idx_produto (produto_id),
    INDEX idx_tipo_rateio (tipo_rateio),
    
    CONSTRAINT chk_percentual_despesa CHECK (percentual IS NULL OR (percentual >= 0 AND percentual <= 100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Rateio de despesas por cliente/produto';

-- View para facilitar consulta de capacity atual
CREATE OR REPLACE VIEW vw_capacity_atual AS
SELECT 
    ch.cliente_id,
    ch.produto_id,
    ch.capacity_atual,
    ch.capacity_necessario,
    ch.percentual_variacao,
    ch.data_vigencia,
    c.nome as cliente_nome,
    cp.nome as produto_nome
FROM capacity_historico ch
INNER JOIN clientes c ON ch.cliente_id = c.id
LEFT JOIN cliente_produtos cp ON ch.produto_id = cp.id
INNER JOIN (
    SELECT 
        cliente_id,
        COALESCE(produto_id, 0) as produto_id,
        MAX(data_vigencia) as max_data
    FROM capacity_historico
    GROUP BY cliente_id, COALESCE(produto_id, 0)
) latest ON ch.cliente_id = latest.cliente_id 
    AND COALESCE(ch.produto_id, 0) = latest.produto_id 
    AND ch.data_vigencia = latest.max_data;

-- View para resumo de margem por competência
CREATE OR REPLACE VIEW vw_margem_resumo AS
SELECT
    mc.id as competencia_id,
    mc.competencia,
    mrr.cliente_id,
    mrr.produto_id,
    c.nome as cliente_nome,
    cp.nome as produto_nome,
    COALESCE(SUM(DISTINCT mrr.valor_rateado), 0) as total_receitas,
    COALESCE(SUM(DISTINCT mrd.valor_rateado), 0) as total_despesas,
    COALESCE(SUM(DISTINCT mrr.valor_rateado), 0) - COALESCE(SUM(DISTINCT mrd.valor_rateado), 0) as lucro,
    CASE 
        WHEN COALESCE(SUM(DISTINCT mrr.valor_rateado), 0) > 0 
        THEN ((COALESCE(SUM(DISTINCT mrr.valor_rateado), 0) - COALESCE(SUM(DISTINCT mrd.valor_rateado), 0)) / COALESCE(SUM(DISTINCT mrr.valor_rateado), 0)) * 100
        ELSE 0
    END as margem_percentual
FROM margem_competencias mc
LEFT JOIN margem_rateio_receitas mrr ON mc.id = mrr.competencia_id
LEFT JOIN margem_rateio_despesas mrd ON mc.id = mrd.competencia_id 
    AND mrr.cliente_id = mrd.cliente_id 
    AND (mrr.produto_id = mrd.produto_id OR (mrr.produto_id IS NULL AND mrd.produto_id IS NULL))
LEFT JOIN clientes c ON mrr.cliente_id = c.id
LEFT JOIN cliente_produtos cp ON mrr.produto_id = cp.id
WHERE mrr.cliente_id IS NOT NULL
GROUP BY mc.id, mc.competencia, mrr.cliente_id, mrr.produto_id, c.nome, cp.nome;
