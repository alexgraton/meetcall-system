-- ============================================================================
-- MIGRATION 001 - Criação de Tabelas Base
-- Sistema Financeiro MeetCall
-- Data: 2025-10-29
-- ============================================================================

USE meetcall_system;

-- ============================================================================
-- MÓDULO 0: FILIAIS
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
-- MÓDULO 1: TIPOS DE SERVIÇOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS tipos_servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo ENUM('despesa', 'receita') NOT NULL,
    parent_id INT NULL,
    aliquota DECIMAL(5,2) COMMENT 'Percentual de alíquota',
    margem_esperada DECIMAL(5,2) COMMENT 'Percentual de margem esperada',
    ordem INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES tipos_servicos(id) ON DELETE SET NULL,
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_parent (parent_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- MÓDULO 4: PLANO DE CONTAS
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
    INDEX idx_aceita_lancamento (aceita_lancamento),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS centro_custos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL,
    filial_id INT,
    parent_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (filial_id) REFERENCES filiais(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES centro_custos(id) ON DELETE SET NULL,
    INDEX idx_codigo (codigo),
    INDEX idx_filial (filial_id),
    INDEX idx_parent (parent_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABELA DE AUDITORIA
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    acao ENUM('create', 'update', 'delete', 'login', 'logout', 'export', 'import') NOT NULL,
    tabela VARCHAR(100),
    registro_id INT,
    dados_anteriores JSON,
    dados_novos JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES users(id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_acao (acao),
    INDEX idx_tabela (tabela),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- FIM DA MIGRATION 001
-- ============================================================================
