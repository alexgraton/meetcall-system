# 📊 GUIA COMPLETO - Sistema de Controle Financeiro
## Fluxo de Trabalho e Boas Práticas

---

## 🎯 CONCEITOS FUNDAMENTAIS

### 1. **Regime de Competência vs Regime de Caixa**

#### **Regime de Competência** (quando aconteceu)
- Registra receitas/despesas na **data de emissão**
- Usado para: Demonstrativo de Resultado (DRE), análise de margem
- Exemplo: Nota fiscal emitida dia 10/12, mas paga dia 30/12
  - Na competência: receita em 10/12
  - No caixa: receita em 30/12

#### **Regime de Caixa** (quando o dinheiro entrou/saiu)
- Registra na **data de pagamento/recebimento**
- Usado para: Fluxo de caixa, saldo bancário
- É o que importa para saber quanto dinheiro você TEM

### 2. **Estados de uma Conta**

```
┌─────────────────┐
│   CADASTRADA    │  Status: PENDENTE
│  (Previsão)     │  Sem conta bancária
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   BAIXADA       │  Status: PAGO/RECEBIDO
│ (Realizado)     │  COM conta bancária
│                 │  Movimenta saldo
└─────────────────┘
```

---

## 🔄 FLUXO OPERACIONAL

### **ETAPA 1: CADASTRO** (Contas a Pagar/Receber)

**O que acontece:**
- Registra a OBRIGAÇÃO financeira
- Status: PENDENTE
- **NÃO movimenta conta bancária**
- Campos preenchidos:
  - Fornecedor/Cliente
  - Descrição
  - Valor
  - Data emissão (competência)
  - Data vencimento
  - Referência (MM/AAAA) - para análise gerencial
  - Centro de custo
  - Tipo de serviço

**Quando usar:**
- Recebeu uma nota fiscal de fornecedor
- Emitiu uma nota fiscal para cliente
- Precisa planejar pagamentos futuros

---

### **ETAPA 2: BAIXA/PAGAMENTO** (O MOMENTO IMPORTANTE!)

**O que acontece:**
- **AQUI você escolhe a conta bancária**
- Status: PAGO/RECEBIDO
- Movimenta o saldo da conta bancária
- Registra data real de pagamento/recebimento
- Pode ter:
  - Juros (atraso)
  - Multa (atraso)
  - Desconto (antecipação)

**Campos adicionais na baixa:**
- `conta_bancaria_id` ← **CAMPO NOVO**
- `data_pagamento`/`data_recebimento`
- `valor_pago`/`valor_recebido`
- `valor_juros`, `valor_multa`, `valor_desconto`

**Exemplo prático:**

```
CADASTRO (dia 01/12):
├─ Fornecedor: Energia Elétrica S/A
├─ Valor: R$ 1.500,00
├─ Vencimento: 15/12/2025
├─ Referência: 12/2025
└─ Status: PENDENTE
    Conta bancária: (vazio)
    Saldo conta corrente: R$ 10.000,00
    
BAIXA (dia 17/12 - 2 dias de atraso):
├─ Conta bancária: Itaú - Conta Corrente ← ESCOLHE AQUI
├─ Data pagamento: 17/12/2025
├─ Valor pago: R$ 1.530,00
├─ Juros: R$ 30,00 (2% ao dia)
├─ Status: PAGO
└─ Saldo conta corrente: R$ 8.470,00 (diminuiu)
```

---

### **ETAPA 3: CONCILIAÇÃO BANCÁRIA**

**O que é:**
- Comparar lançamentos do sistema com extrato do banco
- Garantir que estão "batendo"
- Identificar:
  - Lançamentos no sistema que não estão no banco
  - Lançamentos no banco que não estão no sistema
  - Diferenças de valores

**Como funciona:**
1. Importa arquivo Excel do extrato bancário
2. Sistema lista lançamentos do período
3. Faz matching automático (mesma data + valor similar)
4. Marca como "conciliado" quando bate
5. Mostra divergências para análise manual

**Estrutura da tabela de conciliação:**
```sql
conciliacao_bancaria
├─ extrato_id (lançamento do banco)
├─ conta_pagar_id ou conta_receber_id (lançamento do sistema)
├─ tipo (pagar/receber)
├─ status (pendente/conciliado/divergente)
├─ valor_extrato
├─ valor_sistema
├─ diferenca
└─ observacao
```

---

## 📊 MARGEM GERENCIAL

### **Objetivo:**
Analisar rentabilidade da empresa por diferentes dimensões:
- Por período (mês/trimestre/ano)
- Por cliente
- Por tipo de despesa/receita
- Por centro de custo
- Por filial

### **Estrutura da análise:**

```
MARGEM GERENCIAL - 12/2025
═══════════════════════════════════════════

RECEITAS                          R$ 150.000,00
├─ Cliente A (Ref: 12/2025)       R$ 80.000,00
├─ Cliente B (Ref: 12/2025)       R$ 50.000,00
└─ Cliente C (Ref: 12/2025)       R$ 20.000,00

DESPESAS                          R$ 95.000,00
├─ Pessoal (Ref: 12/2025)         R$ 60.000,00
├─ Operacional (Ref: 12/2025)     R$ 25.000,00
└─ Administrativa (Ref: 12/2025)  R$ 10.000,00

MARGEM BRUTA                      R$ 55.000,00
MARGEM %                          36.67%
```

### **Filtros importantes:**
- Período (data início/fim ou referência)
- Cliente específico
- Tipo de serviço (categoria)
- Centro de custo
- Filial
- Status (competência ou caixa)

---

## 🎨 INTERFACE SUGERIDA

### **Tela de Margem Gerencial:**

```
┌────────────────────────────────────────────────────────┐
│  📊 ANÁLISE DE MARGEM GERENCIAL                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Filtros:                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Referência  │  │   Cliente   │  │   Filial    │   │
│  │  12/2025    │  │  Todos      │  │  Todas      │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │  RECEITAS            R$ 150.000,00           │     │
│  │  ─────────────────────────────────────────   │     │
│  │  Cliente A           R$  80.000,00           │     │
│  │  Cliente B           R$  50.000,00           │     │
│  │  Cliente C           R$  20.000,00           │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │  DESPESAS             R$  95.000,00          │     │
│  │  ─────────────────────────────────────────   │     │
│  │  Pessoal             R$  60.000,00           │     │
│  │  Operacional         R$  25.000,00           │     │
│  │  Administrativa      R$  10.000,00           │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │  MARGEM BRUTA         R$  55.000,00          │     │
│  │  MARGEM %             36.67%                 │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
│  [Exportar Excel] [Exportar PDF] [Gráficos]          │
└────────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Ajustar Fluxo Atual ✅
- [x] Adicionar campo `conta_bancaria_id` (migration 011)
- [x] Adicionar campo `referencia` para análise gerencial
- [ ] Atualizar tela de baixa (pagar/receber) para escolher conta bancária
- [ ] Atualizar models para movimentar saldo bancário na baixa

### Fase 2: Conciliação Bancária 🔄
- [ ] Criar tabela de extratos bancários
- [ ] Criar tela de importação de Excel
- [ ] Criar algoritmo de matching automático
- [ ] Criar tela de conciliação manual

### Fase 3: Margem Gerencial 🔄
- [ ] Criar model de relatório de margem
- [ ] Criar tela com filtros avançados
- [ ] Criar gráficos de análise
- [ ] Exportação Excel/PDF

---

## 📚 REFERÊNCIAS

**Livros/Materiais:**
- "Contabilidade Gerencial" - Eliseu Martins
- "Fluxo de Caixa" - Alexandre Assaf Neto
- ERP SAP - Módulo FI (Financial)
- ERP TOTVS - Módulo Financeiro

**Sistemas similares:**
- ContaAzul
- Omie
- Bling
- NFe.io + Controlle

---

## 💡 DICAS IMPORTANTES

1. **Sempre use Referência (MM/AAAA)** para análises gerenciais
2. **Conta bancária só na baixa**, nunca no cadastro
3. **Conciliação bancária** deve ser feita pelo menos 1x por semana
4. **Margem gerencial** deve considerar regime de competência (referência)
5. **Fluxo de caixa** considera regime de caixa (data pagamento)
