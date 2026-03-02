-- Migration 009: Adiciona constraint UNIQUE em tipos_servicos e campo prazo_dias em contas_receber
-- Data: 02/03/2026

-- ======================================
-- 1. UNIQUE constraint para tipos_servicos.nome
-- ======================================

-- Verificar se há duplicatas antes de aplicar
SELECT nome, COUNT(*) as total 
FROM tipos_servicos 
GROUP BY nome 
HAVING COUNT(*) > 1;

-- Se houver duplicatas, elas precisam ser resolvidas manualmente antes de aplicar
-- Adicionar constraint UNIQUE no campo nome
ALTER TABLE tipos_servicos 
ADD UNIQUE INDEX idx_nome_unique (nome);

-- ======================================
-- 2. Campo prazo_dias em contas_receber
-- ======================================

-- Adicionar campo prazo_dias (período de vencimento em dias)
ALTER TABLE contas_receber 
ADD COLUMN prazo_dias INT DEFAULT 30 COMMENT 'Prazo em dias para vencimento (ex: 15, 30, 45, 60, 90, 120)' 
AFTER data_emissao;

-- Calcular o prazo_dias para registros existentes baseado na diferença entre data_emissao e data_vencimento
UPDATE contas_receber 
SET prazo_dias = DATEDIFF(data_vencimento, data_emissao)
WHERE data_emissao IS NOT NULL AND data_vencimento IS NOT NULL;

-- Se prazo_dias ficou NULL ou negativo, definir como 30 dias (padrão)
UPDATE contas_receber 
SET prazo_dias = 30 
WHERE prazo_dias IS NULL OR prazo_dias < 0;

-- Adicionar índice para melhorar performance de consultas por prazo
CREATE INDEX idx_prazo_dias ON contas_receber(prazo_dias);

-- ======================================
-- Comentários
-- ======================================
-- 1. tipos_servicos.nome agora é UNIQUE - não permite duplicatas (ex: dois "Financeiro")
-- 2. contas_receber.prazo_dias - armazena o período em dias (15, 30, 45, 60, 90, 120)
-- 3. data_vencimento continua existindo e é calculada automaticamente: data_emissao + prazo_dias
