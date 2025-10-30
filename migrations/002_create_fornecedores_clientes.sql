-- Migration 002: Criar tabelas de Fornecedores e Clientes
-- Data: 2025-10-29

-- ============================================
-- FORNECEDORES
-- ============================================

CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18),
    tipo_pessoa ENUM('fisica', 'juridica') DEFAULT 'juridica',
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
    INDEX idx_codigo (codigo),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_cidade (cidade),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Contatos de fornecedores (multi-contact)
CREATE TABLE IF NOT EXISTS fornecedor_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    cargo VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE,
    INDEX idx_fornecedor (fornecedor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- CLIENTES
-- ============================================

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    razao_social VARCHAR(255),
    cnpj VARCHAR(18),
    tipo_pessoa ENUM('fisica', 'juridica') DEFAULT 'juridica',
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
    INDEX idx_codigo (codigo),
    INDEX idx_nome (nome),
    INDEX idx_cnpj (cnpj),
    INDEX idx_cidade (cidade),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Contatos de clientes (multi-contact)
CREATE TABLE IF NOT EXISTS cliente_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    cargo VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Produtos vinculados aos clientes
CREATE TABLE IF NOT EXISTS cliente_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    valor DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    INDEX idx_cliente (cliente_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
