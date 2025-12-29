-- ============================================================================
-- MIGRATION 000 - SCHEMA INICIAL COMPLETO
-- Sistema Financeiro MeetCall
-- Data: 2025-12-28
-- Descrição: Criação consolidada de todas as tabelas do sistema
-- ============================================================================

USE meetcall_system;

-- ============================================================================
-- TABELA 1: USERS (DEVE SER CRIADA PRIMEIRO - OUTRAS TABELAS REFERENCIAM)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Usuários do sistema com controle de acesso baseado em roles';

-- ============================================================================
-- TABELA 2: FILIAIS
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Filiais da empresa';

-- ============================================================================
-- TABELA 3: TIPOS DE SERVIÇOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS tipos_servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo ENUM('despesa', 'receita') NOT NULL,
    parent_id INT NULL,
    aliquota DECIMAL(5,2) COMMENT 'Percentual de alíquota',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (parent_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tipos de serviços (despesas e receitas)';

-- ============================================================================
-- TABELA 4: PLANO DE CONTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS plano_contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE COMMENT 'Ex: 1.1.01.001',
    descricao VARCHAR(255) NOT NULL,
    tipo ENUM('receita', 'despesa', 'ativo', 'passivo', 'patrimonio') NOT NULL,
    nivel INT NOT NULL COMMENT 'Nível hierárquico: 1, 2, 3, 4',
    parent_id INT NULL,
    aceita_lancamento BOOLEAN DEFAULT TRUE COMMENT 'Contas sintéticas não aceitam lançamento',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Plano de contas contábil';

-- ============================================================================
-- TABELA 5: CENTRO DE CUSTOS
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Centros de custos para rateio';

-- ============================================================================
-- TABELA 6: FORNECEDORES
-- ============================================================================

CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18) UNIQUE,
    tipo_servico_id INT,
    categoria_padrao_id INT COMMENT 'Centro de custo padrão',
    email VARCHAR(255),
    telefone VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (categoria_padrao_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_tipo_servico (tipo_servico_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Fornecedores';

-- ============================================================================
-- TABELA 7: FORNECEDOR CONTATOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS fornecedor_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    is_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE,
    INDEX idx_fornecedor (fornecedor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contatos dos fornecedores';

-- ============================================================================
-- TABELA 8: CLIENTES
-- ============================================================================

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18) UNIQUE,
    tipo_servico_id INT,
    categoria_padrao_id INT COMMENT 'Centro de custo padrão',
    email VARCHAR(255),
    telefone VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    FOREIGN KEY (categoria_padrao_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_tipo_servico (tipo_servico_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Clientes';

-- ============================================================================
-- TABELA 9: CLIENTE CONTATOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cliente_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    is_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contatos dos clientes';

-- ============================================================================
-- TABELA 10: CLIENTE PRODUTOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cliente_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    produto VARCHAR(255) NOT NULL,
    descricao TEXT,
    valor_mensal DECIMAL(10,2),
    data_inicio DATE,
    data_fim DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Produtos/serviços contratados pelos clientes';

-- ============================================================================
-- TABELA 11: CONTAS BANCÁRIAS
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contas bancárias da empresa';

-- ============================================================================
-- TABELA 12: CONTAS A PAGAR
-- ============================================================================

CREATE TABLE IF NOT EXISTS contas_pagar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    tipo_servico_id INT,
    centro_custo_id INT,
    filial_id INT,
    conta_bancaria_id INT COMMENT 'Conta bancária usada no pagamento',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contas a pagar';

-- ============================================================================
-- TABELA 13: CONTAS A RECEBER
-- ============================================================================

CREATE TABLE IF NOT EXISTS contas_receber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tipo_servico_id INT,
    centro_custo_id INT,
    filial_id INT,
    conta_bancaria_id INT COMMENT 'Conta bancária onde foi recebido',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Contas a receber';

-- ============================================================================
-- TABELA 14: LANÇAMENTOS MANUAIS
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Lançamentos manuais de receitas e despesas';

-- ============================================================================
-- TABELA 15: CONCILIAÇÕES BANCÁRIAS
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Histórico de importações de extratos bancários';

-- ============================================================================
-- TABELA 16: TRANSAÇÕES DE EXTRATO
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
    similaridade DECIMAL(5,2) COMMENT 'Percentual de similaridade com transação sugerida',
    conciliado_em DATETIME,
    conciliado_por INT COMMENT 'ID do usuário que fez a conciliação',
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conciliacao_id) REFERENCES conciliacoes_bancarias(id) ON DELETE CASCADE,
    FOREIGN KEY (conciliado_por) REFERENCES users(id),
    INDEX idx_conciliacao (conciliacao_id),
    INDEX idx_data_transacao (data_transacao),
    INDEX idx_status (status_conciliacao),
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Transações importadas dos extratos bancários';

-- ============================================================================
-- TABELA 17: RATEIO DE CONTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS rateio_contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_lancamento ENUM('contas_pagar', 'contas_receber') NOT NULL,
    lancamento_id INT NOT NULL COMMENT 'ID da conta a pagar ou receber',
    centro_custo_id INT NOT NULL,
    percentual DECIMAL(5,2) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id),
    INDEX idx_tipo_lancamento (tipo_lancamento, lancamento_id),
    INDEX idx_centro_custo (centro_custo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Rateio de contas por centro de custo';

-- ============================================================================
-- TABELA 18: AUDITORIA
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Log de auditoria de todas as operações do sistema';

-- ============================================================================
-- FIM DA MIGRATION
-- ============================================================================

-- Mensagem de sucesso
SELECT '✓ Migration 000_initial_schema.sql executada com sucesso!' as status;
SELECT 'Total de 18 tabelas criadas' as resultado;
