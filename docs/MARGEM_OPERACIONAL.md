# Sistema de Análise de Margem Operacional

## 📊 Visão Geral

Sistema completo para análise de rentabilidade por cliente e produto, permitindo controle detalhado de capacity (operadores) e rateio preciso de receitas e despesas.

## 🎯 Funcionalidades

### 1. **Gerenciamento de Capacity** (`/capacity`)
- Controle de operadores por cliente/produto
- Histórico completo de alterações com data e usuário
- Acompanhamento de capacity atual vs. necessário
- Cálculo automático de variação percentual
- Consulta de capacity por período para análise histórica

**Campos:**
- Capacity Atual: Número de operadores atualmente alocados
- Capacity Necessário: Número de operadores ideais para o cliente/produto
- Data de Vigência: Data a partir da qual o capacity é válido
- Observações: Notas sobre a alteração

### 2. **Margem Operacional** (`/margem`)

#### 2.1 Gestão de Competências
- Criação de competências mensais (formato MM/YYYY)
- Controle de status: Aberta, Em Processamento, Fechada
- Competências fechadas bloqueiam alterações (auditoria)
- Reabertura disponível para administradores

#### 2.2 Rateio de Receitas
- Listagem de todas as receitas da competência
- Rateio automático quando cliente não tem produtos
- Rateio manual por percentual quando cliente tem produtos
- Validação: soma dos percentuais deve ser 100%
- Histórico de rateios anteriores visível

**Regras:**
- Cliente SEM produtos → receita vai direto para o cliente (100%)
- Cliente COM produtos → OBRIGATÓRIO ratear entre produtos (soma = 100%)

#### 2.3 Rateio de Despesas
Três formas de rateio disponíveis:

**a) Rateio Manual por Percentual**
- Usuário define % para cada cliente/produto
- Valor calculado automaticamente
- Validação: soma não pode exceder 100%

**b) Rateio Manual por Valor Fixo**
- Usuário define valor em R$ para cada cliente/produto
- Validação: soma não pode exceder valor da despesa

**c) Rateio Automático por Capacity** ⭐
- Sistema calcula proporção baseado no capacity cadastrado
- Exemplo: Cliente A tem 10 operadores, Cliente B tem 5 operadores
  - Total: 15 operadores
  - Cliente A recebe 66,67% da despesa
  - Cliente B recebe 33,33% da despesa
- Ajuste automático de arredondamento

#### 2.4 Dashboard de Margem
**Visão por Competência:**
- Resumo geral: Total Receitas, Total Despesas, Lucro, Margem %
- Tabela detalhada por cliente/produto
- Indicadores visuais de performance:
  - 🟢 Margem ≥ 20%: Excelente
  - 🟡 Margem ≥ 10%: Atenção
  - 🔴 Margem < 10%: Crítico
- Gráfico comparativo (receitas vs despesas)
- Detalhamento de despesas por tipo de serviço

**Visão Anual:**
- Comparação mês a mês
- Evolução de margem ao longo do ano
- Identificação de tendências

## 🗄️ Estrutura do Banco de Dados

### Tabelas Criadas (Migration 013)

#### `capacity_historico`
```sql
- id: INT (PK)
- cliente_id: INT (FK → clientes)
- produto_id: INT NULL (FK → cliente_produtos)
- capacity_atual: INT
- capacity_necessario: INT
- percentual_variacao: DECIMAL (calculado automaticamente)
- data_vigencia: DATE
- data_alteracao: TIMESTAMP
- usuario_alteracao: INT (FK → users)
- observacoes: TEXT
```

#### `margem_competencias`
```sql
- id: INT (PK)
- competencia: CHAR(7) UNIQUE (formato MM/YYYY)
- status: ENUM('aberta', 'em_processamento', 'fechada')
- data_abertura: TIMESTAMP
- data_fechamento: TIMESTAMP NULL
- usuario_abertura: INT (FK → users)
- usuario_fechamento: INT NULL (FK → users)
```

#### `margem_rateio_receitas`
```sql
- id: INT (PK)
- competencia_id: INT (FK → margem_competencias)
- conta_receber_id: INT (FK → contas_receber)
- cliente_id: INT (FK → clientes)
- produto_id: INT NULL (FK → cliente_produtos)
- percentual: DECIMAL(10,2)
- valor_rateado: DECIMAL(15,2)
- data_rateio: TIMESTAMP
- usuario_rateio: INT (FK → users)
```

#### `margem_rateio_despesas`
```sql
- id: INT (PK)
- competencia_id: INT (FK → margem_competencias)
- conta_pagar_id: INT (FK → contas_pagar)
- cliente_id: INT (FK → clientes)
- produto_id: INT NULL (FK → cliente_produtos)
- tipo_rateio: ENUM('percentual', 'valor_fixo', 'capacity')
- percentual: DECIMAL(10,2) NULL
- valor_rateado: DECIMAL(15,2)
- data_rateio: TIMESTAMP
- usuario_rateio: INT (FK → users)
- observacoes: TEXT
```

### Views Criadas

#### `vw_capacity_atual`
Retorna o capacity mais recente de cada cliente/produto para consultas rápidas.

#### `vw_margem_resumo`
Consolida receitas, despesas, lucro e margem percentual por competência/cliente/produto.

## 🔄 Fluxo de Trabalho Recomendado

### Passo 1: Configurar Capacity (Início do mês)
1. Acessar `/capacity`
2. Atualizar capacity atual e necessário para cada cliente/produto
3. Informar data de vigência (geralmente 1º dia do mês)
4. Salvar observações se houver mudanças significativas

### Passo 2: Criar Competência
1. Acessar `/margem`
2. Criar nova competência (ex: 12/2025)
3. Sistema busca automaticamente receitas e despesas do período

### Passo 3: Ratear Receitas
1. Acessar "Ratear Receitas"
2. Para cada receita:
   - Se cliente não tem produtos: sistema rateia automaticamente 100%
   - Se cliente tem produtos: informar % para cada produto (total = 100%)
3. Salvar rateios

### Passo 4: Ratear Despesas
1. Acessar "Ratear Despesas"
2. Para cada despesa, escolher método:
   - **Manual (%)**: Informar percentual para cada cliente/produto
   - **Manual (R$)**: Informar valor fixo para cada cliente/produto
   - **Por Capacity**: Sistema calcula automaticamente baseado em operadores
3. Salvar rateios

### Passo 5: Analisar Dashboard
1. Acessar "Dashboard"
2. Visualizar:
   - Resumo geral da competência
   - Margem por cliente/produto
   - Gráficos comparativos
   - Detalhamento de despesas por tipo
3. Identificar clientes/produtos com baixa rentabilidade
4. Tomar decisões estratégicas

### Passo 6: Fechar Competência
1. Após conferir todos os rateios
2. Clicar em "Fechar Competência"
3. Sistema bloqueia alterações (auditoria)
4. Competência pode ser reaberta se necessário

## 📈 Métricas Calculadas

### Margem Operacional %
```
Margem % = (Receitas - Despesas) / Receitas × 100
```

### Lucro
```
Lucro = Total Receitas - Total Despesas
```

### Rateio por Capacity
```
% Cliente A = (Capacity Cliente A / Total Capacity) × 100
Valor Rateado = Valor Despesa × % Cliente A / 100
```

### Variação de Capacity
```
Variação % = ((Atual - Necessário) / Necessário) × 100
```

## 🎨 Interface

### Menu Principal
- **Financeiro** → Margem Operacional
- **Financeiro** → Capacity

### Ícones
- 💰 Margem Operacional (percent icon)
- 📊 Capacity (users icon)
- 📈 Receitas (cash-coin icon)
- 📉 Despesas (receipt icon)
- 📊 Dashboard (graph-up icon)

## 🔐 Segurança

- Todas as rotas protegidas por autenticação
- Registro de usuário em todas as operações
- Histórico completo de alterações
- Competências fechadas bloqueiam edições
- Validações de dados em backend e frontend

## 📋 Validações Implementadas

### Receitas
- ✅ Soma de percentuais = 100%
- ✅ Produtos obrigatórios quando cliente tem produtos
- ✅ Valores positivos

### Despesas
- ✅ Soma de valores ≤ valor total da despesa
- ✅ Percentuais entre 0 e 100
- ✅ Capacity existente para rateio automático

### Capacity
- ✅ Valores não-negativos
- ✅ Data de vigência obrigatória
- ✅ Cliente obrigatório

## 🚀 Como Usar

1. **Instalar dependências** (já incluídas no requirements.txt)
2. **Executar migration 013**:
   ```bash
   python run_migrations.py
   ```
3. **Acessar o sistema**: Novos menus aparecerão automaticamente
4. **Começar pelo Capacity**: Cadastrar operadores por cliente/produto
5. **Criar primeira competência**: Começar análise de margem

## 💡 Dicas

- Configure capacity no início de cada mês
- Use rateio automático por capacity para despesas fixas (aluguel, limpeza, etc.)
- Use rateio manual para despesas específicas de um cliente
- Feche competências mensalmente para manter histórico confiável
- Acompanhe tendências no dashboard anual

## 🔧 Manutenção

### Adicionar Nova Competência
Automático - basta criar pelo sistema.

### Corrigir Rateio
1. Reabrir competência (se fechada)
2. Acessar rateio de receitas/despesas
3. Clicar em "Ratear" novamente
4. Sistema limpa rateios anteriores e salva novos
5. Fechar competência novamente

### Consultar Histórico
- Capacity: botão "Histórico" em cada cliente/produto
- Margem: todos os rateios ficam salvos no banco

---

**Desenvolvido em:** 28/12/2025
**Versão:** 1.0
**Migration:** 013_margem_operacional.sql
