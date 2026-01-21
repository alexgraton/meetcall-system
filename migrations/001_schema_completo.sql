-- ============================================================================
-- MIGRATION 001 - SCHEMA COMPLETO
-- Sistema Financeiro MeetCall
-- Data: 2026-01-20
-- Descrição: Migração consolidada com todas as tabelas do sistema
-- ============================================================================

USE meetcall_system;

-- ============================================================================
-- 1. USERS
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. FILIAIS
-- ============================================================================

CREATE TABLE IF NOT EXISTS filiais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18),
    email VARCHAR(255),
    telefone VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    is_matriz BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_cnpj (cnpj),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. TIPOS DE SERVIÇOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS tipos_servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo ENUM('despesa', 'receita') NOT NULL,
    parent_id INT NULL,
    aliquota DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (parent_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. PLANO DE CONTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS plano_contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL,
    tipo ENUM('receita', 'despesa', 'ativo', 'passivo', 'patrimonio') NOT NULL,
    nivel INT NOT NULL,
    parent_id INT NULL,
    aceita_lancamento BOOLEAN DEFAULT TRUE,
    dre_grupo ENUM('receita_bruta', 'deducoes', 'receita_liquida', 'custo_servicos', 
                   'lucro_bruto', 'despesas_operacionais', 'ebitda', 'resultado') NULL,
    ordem INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES plano_contas(id) ON DELETE SET NULL,
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_nivel (nivel),
    INDEX idx_parent (parent_id),
    INDEX idx_dre_grupo (dre_grupo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. CENTRO DE CUSTOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS centro_custos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo ENUM('operacional', 'administrativo', 'comercial', 'financeiro') NOT NULL,
    filial_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_filial (filial_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. FORNECEDORES
-- ============================================================================

CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18),
    tipo_pessoa ENUM('fisica', 'juridica') DEFAULT 'juridica',
    tipo_servico_id INT,
    categoria_padrao_id INT,
    email VARCHAR(255),
    telefone VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    observacoes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (categoria_padrao_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_tipo_servico (tipo_servico_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. FORNECEDOR CONTATOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS fornecedor_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    observacoes TEXT,
    is_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE,
    INDEX idx_fornecedor (fornecedor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. CLIENTES
-- ============================================================================

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18),
    tipo_pessoa ENUM('fisica', 'juridica') DEFAULT 'juridica',
    tipo_servico_id INT,
    categoria_padrao_id INT,
    email VARCHAR(255),
    telefone VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    observacoes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (categoria_padrao_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_tipo_servico (tipo_servico_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 9. CLIENTE CONTATOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cliente_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    observacoes TEXT,
    is_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 10. CLIENTE PRODUTOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cliente_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    valor DECIMAL(15,2),
    valor_mensal DECIMAL(10,2),
    data_inicio DATE,
    data_fim DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 11. CONTAS BANCÁRIAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS contas_bancarias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    banco VARCHAR(100) NOT NULL,
    agencia VARCHAR(50) NOT NULL,
    numero_conta VARCHAR(100) NOT NULL,
    tipo_conta ENUM('corrente','poupanca','caixa') DEFAULT 'corrente',
    descricao VARCHAR(255) NULL,
    saldo_inicial DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    saldo_atual DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    moeda VARCHAR(10) DEFAULT 'BRL',
    filial_id INT NULL,
    ativo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT NULL,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_filial (filial_id),
    INDEX idx_banco (banco),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 12. CONTAS A PAGAR
-- ============================================================================

CREATE TABLE IF NOT EXISTS contas_pagar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    tipo_servico_id INT,
    centro_custo_id INT,
    filial_id INT,
    conta_bancaria_id INT,
    descricao VARCHAR(255) NOT NULL,
    numero_documento VARCHAR(100),
    observacoes TEXT,
    valor_total DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2) DEFAULT 0,
    numero_parcelas INT DEFAULT 1,
    parcela_atual INT DEFAULT 1,
    recorrente BOOLEAN DEFAULT FALSE,
    tipo_recorrencia ENUM('mensal', 'trimestral', 'semestral', 'anual') NULL,
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE NULL,
    percentual_juros DECIMAL(5,2) DEFAULT 0,
    percentual_multa DECIMAL(5,2) DEFAULT 0,
    valor_juros DECIMAL(10,2) DEFAULT 0,
    valor_multa DECIMAL(10,2) DEFAULT 0,
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    status ENUM('pendente', 'pago', 'vencido', 'cancelado') DEFAULT 'pendente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_fornecedor (fornecedor_id),
    INDEX idx_status (status),
    INDEX idx_data_vencimento (data_vencimento),
    INDEX idx_filial (filial_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 13. CONTAS A RECEBER
-- ============================================================================

CREATE TABLE IF NOT EXISTS contas_receber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tipo_servico_id INT,
    centro_custo_id INT,
    filial_id INT,
    conta_bancaria_id INT,
    descricao VARCHAR(255) NOT NULL,
    numero_documento VARCHAR(100),
    observacoes TEXT,
    valor_total DECIMAL(10,2) NOT NULL,
    valor_recebido DECIMAL(10,2) DEFAULT 0,
    numero_parcelas INT DEFAULT 1,
    parcela_atual INT DEFAULT 1,
    recorrente BOOLEAN DEFAULT FALSE,
    tipo_recorrencia ENUM('mensal', 'trimestral', 'semestral', 'anual') NULL,
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_recebimento DATE NULL,
    percentual_juros DECIMAL(5,2) DEFAULT 0,
    percentual_multa DECIMAL(5,2) DEFAULT 0,
    valor_juros DECIMAL(10,2) DEFAULT 0,
    valor_multa DECIMAL(10,2) DEFAULT 0,
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    status ENUM('pendente', 'recebido', 'vencido', 'cancelado') DEFAULT 'pendente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_cliente (cliente_id),
    INDEX idx_status (status),
    INDEX idx_data_vencimento (data_vencimento),
    INDEX idx_filial (filial_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 14. LANÇAMENTOS MANUAIS
-- ============================================================================

CREATE TABLE IF NOT EXISTS lancamentos_manuais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    tipo ENUM('receita', 'despesa') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_lancamento DATE NOT NULL,
    centro_custo_id INT,
    filial_id INT,
    fornecedor_id INT NULL,
    cliente_id INT NULL,
    observacoes TEXT,
    status ENUM('ativo', 'cancelado') DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE SET NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_tipo (tipo),
    INDEX idx_data_lancamento (data_lancamento),
    INDEX idx_filial (filial_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 15. CONCILIAÇÕES BANCÁRIAS
-- ============================================================================

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
    created_by INT,
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_conta_bancaria (conta_bancaria_id),
    INDEX idx_data_importacao (data_importacao),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 16. TRANSAÇÕES DE EXTRATO
-- ============================================================================

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
    similaridade DECIMAL(5,2),
    conciliado_em DATETIME,
    conciliado_por INT,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conciliacao_id) REFERENCES conciliacoes_bancarias(id) ON DELETE CASCADE,
    FOREIGN KEY (conciliado_por) REFERENCES users(id),
    INDEX idx_conciliacao (conciliacao_id),
    INDEX idx_data_transacao (data_transacao),
    INDEX idx_status (status_conciliacao),
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 17. RATEIO DE CONTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS rateio_contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_lancamento ENUM('contas_pagar', 'contas_receber') NOT NULL,
    lancamento_id INT NOT NULL,
    centro_custo_id INT NOT NULL,
    percentual DECIMAL(5,2) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id),
    INDEX idx_tipo_lancamento (tipo_lancamento, lancamento_id),
    INDEX idx_centro_custo (centro_custo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 18. CAPACITY HISTÓRICO
-- ============================================================================

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 19. MARGEM COMPETÊNCIAS
-- ============================================================================

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 20. MARGEM RATEIO RECEITAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS margem_rateio_receitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competencia_id INT NOT NULL,
    conta_receber_id INT NOT NULL,
    cliente_id INT NOT NULL,
    produto_id INT NULL,
    percentual DECIMAL(10,2) NOT NULL DEFAULT 0.00,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 21. MARGEM RATEIO DESPESAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS margem_rateio_despesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competencia_id INT NOT NULL,
    conta_pagar_id INT NOT NULL,
    cliente_id INT NOT NULL,
    produto_id INT NULL,
    tipo_rateio ENUM('percentual', 'valor_fixo', 'capacity') NOT NULL DEFAULT 'percentual',
    percentual DECIMAL(10,2) NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 22. AUDITORIA
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabela VARCHAR(100) NOT NULL,
    registro_id INT NOT NULL,
    acao ENUM('insert', 'update', 'delete') NOT NULL,
    dados_anteriores JSON,
    dados_novos JSON,
    usuario_id INT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (usuario_id) REFERENCES users(id),
    INDEX idx_tabela (tabela),
    INDEX idx_registro (registro_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_data_hora (data_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Capacity Atual
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

-- View: Margem Resumo
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

-- ============================================================================
-- FIM DA MIGRAÇÃO
-- ============================================================================

SELECT 'Migration 001_schema_completo.sql executada com sucesso!' as status;
SELECT '22 tabelas + 2 views criadas' as resultado;
