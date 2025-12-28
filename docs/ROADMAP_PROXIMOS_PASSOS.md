# 🎯 ROADMAP - Próximos Passos do Sistema Financeiro

## Status Atual ✅

### Módulos Implementados:
- ✅ Cadastro de Clientes
- ✅ Cadastro de Fornecedores  
- ✅ Tipos de Serviços (Categorias)
- ✅ Contas a Pagar
- ✅ Contas a Receber
- ✅ Contas Bancárias
- ✅ Centro de Custos
- ✅ Plano de Contas
- ✅ Filiais

### Melhorias Recentes:
- ✅ Flash messages corrigidas (mensagem única flutuante)
- ✅ Formatação de valores monetários (R$ 1.500,00)
- ✅ Carregamento de produtos por cliente em contas a receber
- ✅ Campo de referência (MM/AAAA) para controle de margem
- ✅ Migration 011: campos `conta_bancaria_id` e `referencia`

---

## 📋 FASE 2 - Funcionalidades Essenciais

### 1️⃣ AJUSTAR FLUXO DE BAIXA (Prioridade ALTA)

**Objetivo:** Implementar o vínculo correto com contas bancárias

#### Contas a Pagar - Tela de Baixa/Pagamento

**Rota:** `/contas-pagar/<id>/pagar`

**Campos do formulário:**
```
┌──────────────────────────────────────────┐
│ BAIXAR CONTA A PAGAR                     │
├──────────────────────────────────────────┤
│                                          │
│ Fornecedor: [Energia Elétrica S/A    ]  │
│ Descrição:  [Conta de luz - Dez/25   ]  │
│ Valor:      R$ 1.500,00                  │
│ Vencimento: 15/12/2025                   │
│                                          │
│ ───────────────────────────────────────  │
│                                          │
│ Data Pagamento*:    [17/12/2025     ]   │
│ Conta Bancária*:    [Itaú Corrente ▼]   │
│                                          │
│ Valor a Pagar:      [1.500,00       ]   │
│ Juros:              [30,00          ]   │
│ Multa:              [0,00           ]   │
│ Desconto:           [0,00           ]   │
│                                          │
│ Total a Pagar:      R$ 1.530,00         │
│                                          │
│ Observações:                             │
│ ┌────────────────────────────────────┐  │
│ │ Pago com 2 dias de atraso          │  │
│ └────────────────────────────────────┘  │
│                                          │
│ [Cancelar]  [Confirmar Pagamento]       │
└──────────────────────────────────────────┘
```

**Backend (routes/contas_pagar.py):**
```python
@contas_pagar_bp.route('/<int:conta_id>/pagar', methods=['GET', 'POST'])
def pagar(conta_id):
    if request.method == 'POST':
        dados_pagamento = {
            'conta_bancaria_id': request.form['conta_bancaria_id'],  # ← NOVO
            'data_pagamento': request.form['data_pagamento'],
            'valor_pago': converter_valor_brasileiro(request.form['valor_pago']),
            'valor_juros': converter_valor_brasileiro(request.form.get('valor_juros', '0')),
            'valor_multa': converter_valor_brasileiro(request.form.get('valor_multa', '0')),
            'valor_desconto': converter_valor_brasileiro(request.form.get('valor_desconto', '0'))
        }
        
        # Pagar conta e movimentar conta bancária
        ContaPagarModel.pagar(conta_id, dados_pagamento)
        
        # Atualizar saldo da conta bancária
        ContaBancariaModel.debitar(
            dados_pagamento['conta_bancaria_id'],
            dados_pagamento['valor_pago']
        )
```

**Model (models/conta_pagar.py):**
```python
@staticmethod
def pagar(conta_id: int, dados_pagamento: Dict) -> bool:
    """Registra pagamento de uma conta"""
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            UPDATE contas_pagar
            SET status = 'pago',
                conta_bancaria_id = %s,
                data_pagamento = %s,
                valor_pago = %s,
                valor_juros = %s,
                valor_multa = %s,
                valor_desconto = %s
            WHERE id = %s
        """
        
        cursor.execute(query, (
            dados_pagamento['conta_bancaria_id'],  # ← NOVO CAMPO
            dados_pagamento['data_pagamento'],
            dados_pagamento['valor_pago'],
            dados_pagamento['valor_juros'],
            dados_pagamento['valor_multa'],
            dados_pagamento['valor_desconto'],
            conta_id
        ))
        
        conn.commit()
        return True
```

**Model (models/conta_bancaria.py):**
```python
@staticmethod
def debitar(conta_id: int, valor: Decimal) -> bool:
    """Debita valor da conta bancária (pagamento)"""
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            UPDATE contas_bancarias
            SET saldo_atual = saldo_atual - %s
            WHERE id = %s
        """
        
        cursor.execute(query, (valor, conta_id))
        conn.commit()
        return True

@staticmethod
def creditar(conta_id: int, valor: Decimal) -> bool:
    """Credita valor na conta bancária (recebimento)"""
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            UPDATE contas_bancarias
            SET saldo_atual = saldo_atual + %s
            WHERE id = %s
        """
        
        cursor.execute(query, (valor, conta_id))
        conn.commit()
        return True
```

**Arquivos a criar/modificar:**
- [ ] `templates/contas_pagar/baixar.html` (nova tela)
- [ ] `routes/contas_pagar.py` - adicionar rota `/pagar`
- [ ] `models/conta_pagar.py` - atualizar método `pagar()`
- [ ] `models/conta_bancaria.py` - adicionar `debitar()` e `creditar()`

**Mesma lógica para Contas a Receber:**
- [ ] `templates/contas_receber/baixar.html`
- [ ] `routes/contas_receber.py` - adicionar rota `/receber`
- [ ] `models/conta_receber.py` - atualizar método `receber()`

---

### 2️⃣ CONCILIAÇÃO BANCÁRIA (Prioridade MÉDIA)

**Objetivo:** Importar extrato bancário e conciliar com lançamentos

#### Estrutura de Dados

**Migration 012: Tabelas de Conciliação**
```sql
CREATE TABLE extratos_bancarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_bancaria_id INT NOT NULL,
    data_movimento DATE NOT NULL,
    documento VARCHAR(100),
    historico VARCHAR(500),
    valor DECIMAL(10,2) NOT NULL,
    tipo ENUM('debito', 'credito') NOT NULL,
    saldo DECIMAL(10,2),
    conciliado BOOLEAN DEFAULT FALSE,
    arquivo_origem VARCHAR(255),
    linha_arquivo INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id),
    INDEX idx_conta_data (conta_bancaria_id, data_movimento),
    INDEX idx_conciliado (conciliado)
);

CREATE TABLE conciliacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    extrato_id INT NOT NULL,
    tipo_lancamento ENUM('pagar', 'receber', 'manual') NOT NULL,
    lancamento_id INT,  -- ID da conta_pagar ou conta_receber
    valor_extrato DECIMAL(10,2) NOT NULL,
    valor_sistema DECIMAL(10,2),
    diferenca DECIMAL(10,2) GENERATED ALWAYS AS (valor_extrato - valor_sistema),
    status ENUM('pendente', 'conciliado', 'divergente') DEFAULT 'pendente',
    observacao TEXT,
    conciliado_em TIMESTAMP NULL,
    conciliado_por INT,
    
    FOREIGN KEY (extrato_id) REFERENCES extratos_bancarios(id),
    FOREIGN KEY (conciliado_por) REFERENCES users(id),
    INDEX idx_status (status)
);
```

#### Fluxo de Importação

**Tela: `/conciliacao/importar`**

```
┌──────────────────────────────────────────────────────┐
│ 📤 IMPORTAR EXTRATO BANCÁRIO                         │
├──────────────────────────────────────────────────────┤
│                                                       │
│ Conta Bancária*: [Itaú Conta Corrente          ▼]   │
│                                                       │
│ Arquivo Excel*:  [Escolher arquivo...] [Browse]     │
│                                                       │
│ Formato:                                             │
│ ┌───────────────────────────────────────────────┐   │
│ │ ☑ Padrão OFX (maioria dos bancos)            │   │
│ │ ☐ Excel Personalizado                        │   │
│ └───────────────────────────────────────────────┘   │
│                                                       │
│ Período:                                             │
│ De: [01/12/2025] Até: [31/12/2025]                  │
│                                                       │
│                                   [Importar Extrato] │
└──────────────────────────────────────────────────────┘
```

**Processamento Excel:**
```python
# routes/conciliacao.py

import pandas as pd

@conciliacao_bp.route('/importar', methods=['POST'])
def importar_extrato():
    arquivo = request.files['arquivo']
    conta_bancaria_id = request.form['conta_bancaria_id']
    
    # Ler Excel
    df = pd.read_excel(arquivo)
    
    # Colunas esperadas: Data, Documento, Histórico, Débito, Crédito, Saldo
    for idx, row in df.iterrows():
        dados = {
            'conta_bancaria_id': conta_bancaria_id,
            'data_movimento': row['Data'],
            'documento': row['Documento'],
            'historico': row['Histórico'],
            'valor': row['Débito'] if pd.notna(row['Débito']) else row['Crédito'],
            'tipo': 'debito' if pd.notna(row['Débito']) else 'credito',
            'saldo': row['Saldo'],
            'arquivo_origem': arquivo.filename,
            'linha_arquivo': idx + 2  # +2 por causa do cabeçalho
        }
        
        ExtratoBancarioModel.create(dados)
    
    # Tentar conciliação automática
    ConciliacaoModel.auto_conciliar(conta_bancaria_id)
    
    flash('Extrato importado com sucesso!', 'success')
    return redirect(url_for('conciliacao.listar'))
```

**Tela: `/conciliacao/listar`**

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🔄 CONCILIAÇÃO BANCÁRIA - Itaú Conta Corrente                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Período: [01/12/2025] a [31/12/2025]   Status: [Todos ▼]   [Filtrar] │
│                                                                         │
│ ┌────────────────────────────────────────────────────────────────┐    │
│ │ EXTRATO BANCÁRIO          │  SISTEMA          │  STATUS        │    │
│ ├────────────────────────────────────────────────────────────────┤    │
│ │ 15/12 │ R$ 1.500,00 (D)   │ R$ 1.500,00      │ ✅ Conciliado  │    │
│ │       │ ENERGIA ELET S/A  │ Conta #1234      │                │    │
│ │                           │                  │                │    │
│ │ 17/12 │ R$ 2.300,00 (D)   │ R$ 2.300,00      │ ✅ Conciliado  │    │
│ │       │ FORNECEDOR XYZ    │ Conta #1235      │                │    │
│ │                           │                  │                │    │
│ │ 20/12 │ R$ 350,00 (D)     │ (sem registro)   │ ⚠️  Divergente  │    │
│ │       │ TARIFA BANCARIA   │                  │ [Lançar Manual]│    │
│ │                           │                  │                │    │
│ │ 25/12 │ R$ 8.000,00 (C)   │ R$ 8.000,00      │ ✅ Conciliado  │    │
│ │       │ CLIENTE ABC       │ Conta #5678      │                │    │
│ └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│ Resumo:                                                                 │
│ Total Conciliado: 3  │  Divergências: 1  │  Pendentes: 0              │
│                                                                         │
│ [Exportar Relatório] [Marcar Todos Conciliados]                       │
└────────────────────────────────────────────────────────────────────────┘
```

**Arquivos a criar:**
- [ ] `migrations/012_conciliacao_bancaria.py`
- [ ] `models/extrato_bancario.py`
- [ ] `models/conciliacao.py`
- [ ] `routes/conciliacao.py`
- [ ] `templates/conciliacao/importar.html`
- [ ] `templates/conciliacao/listar.html`

---

### 3️⃣ MARGEM GERENCIAL (Prioridade ALTA)

**Objetivo:** Dashboard completo de análise de resultados

#### Estrutura da Tela

**Rota:** `/relatorios/margem-gerencial`

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 📊 ANÁLISE DE MARGEM GERENCIAL                                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ ┌─────────────────── FILTROS ───────────────────────────────────────┐   │
│ │                                                                     │   │
│ │ Período:                                                           │   │
│ │ ○ Por Referência:  [12/2025 ▼]                                    │   │
│ │ ○ Por Data:        De [01/12/25] Até [31/12/25]                   │   │
│ │                                                                     │   │
│ │ Cliente:           [Todos ▼]         Filial: [Todas ▼]           │   │
│ │ Tipo Serviço:      [Todos ▼]         Centro Custo: [Todos ▼]     │   │
│ │                                                                     │   │
│ │ Regime:  ○ Competência (referência)  ○ Caixa (data pagamento)     │   │
│ │                                                                     │   │
│ │                        [Limpar] [Aplicar Filtros]                  │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ ┌────────────────────── RESUMO ──────────────────────────────────────┐   │
│ │                                                                     │   │
│ │  💰 RECEITAS                    📉 DESPESAS                        │   │
│ │  R$ 150.000,00                  R$ 95.000,00                       │   │
│ │                                                                     │   │
│ │  📊 MARGEM BRUTA                📈 MARGEM %                        │   │
│ │  R$ 55.000,00                   36.67%                             │   │
│ │                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ ┌─────────────────── RECEITAS POR CLIENTE ──────────────────────────┐   │
│ │                                                                     │   │
│ │  Cliente A          [████████████████████] 53.33%    R$ 80.000,00 │   │
│ │  Cliente B          [████████████░░░░░░░░] 33.33%    R$ 50.000,00 │   │
│ │  Cliente C          [████░░░░░░░░░░░░░░░░] 13.33%    R$ 20.000,00 │   │
│ │                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ ┌─────────────────── DESPESAS POR TIPO ─────────────────────────────┐   │
│ │                                                                     │   │
│ │  Pessoal            [████████████████████] 63.16%    R$ 60.000,00 │   │
│ │  Operacional        [████████░░░░░░░░░░░░] 26.32%    R$ 25.000,00 │   │
│ │  Administrativa     [████░░░░░░░░░░░░░░░░] 10.53%    R$ 10.000,00 │   │
│ │                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ ┌─────────────────── EVOLUÇÃO MENSAL ───────────────────────────────┐   │
│ │                                                                     │   │
│ │  R$                                                                 │   │
│ │  150k ┤          ╭─╮                                               │   │
│ │  100k ┤     ╭────╯ ╰──╮                                            │   │
│ │   50k ┤╭────╯         ╰───╮                                        │   │
│ │     0 └┴────┴────┴────┴────┴                                       │   │
│ │       Out   Nov   Dez   Jan                                        │   │
│ │                                                                     │   │
│ │       ─── Receitas    ─── Despesas    ─── Margem                  │   │
│ │                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ ┌───────────── DETALHAMENTO POR CLIENTE ────────────────────────────┐   │
│ │                                                                     │   │
│ │ Cliente A                                      Total: R$ 80.000,00 │   │
│ │ ├─ Receitas:                                          R$ 80.000,00 │   │
│ │ ├─ Despesas Diretas:                                  R$ 45.000,00 │   │
│ │ │  ├─ Pessoal (Ref: 12/2025)                          R$ 35.000,00 │   │
│ │ │  └─ Operacional (Ref: 12/2025)                      R$ 10.000,00 │   │
│ │ └─ Margem:                                            R$ 35.000,00 │   │
│ │    Margem %:                                                43.75% │   │
│ │                                                                     │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│ [📥 Exportar Excel] [📄 Exportar PDF] [📊 Ver Gráficos Detalhados]      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Backend

**Model: `models/margem_gerencial.py`**
```python
class MargemGerencialModel:
    
    @staticmethod
    def calcular_margem(filtros: Dict) -> Dict:
        """
        Calcula margem gerencial com base nos filtros
        
        Filtros:
        - referencia: MM/AAAA
        - data_inicio, data_fim
        - cliente_id
        - filial_id
        - tipo_servico_id
        - centro_custo_id
        - regime: 'competencia' ou 'caixa'
        """
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Query base para receitas
            query_receitas = """
                SELECT 
                    SUM(valor_total) as total_receitas,
                    cliente_id,
                    c.razao_social as cliente_nome
                FROM contas_receber cr
                LEFT JOIN clientes c ON cr.cliente_id = c.id
                WHERE 1=1
            """
            
            # Query base para despesas
            query_despesas = """
                SELECT 
                    SUM(valor_total) as total_despesas,
                    tipo_servico_id,
                    ts.nome as tipo_nome
                FROM contas_pagar cp
                LEFT JOIN tipos_servicos ts ON cp.tipo_servico_id = ts.id
                WHERE 1=1
            """
            
            # Aplicar filtros
            params = {}
            
            if filtros.get('referencia'):
                query_receitas += " AND cr.referencia = %(referencia)s"
                query_despesas += " AND cp.referencia = %(referencia)s"
                params['referencia'] = filtros['referencia']
            
            if filtros.get('regime') == 'caixa':
                query_receitas += " AND cr.status = 'recebido'"
                query_despesas += " AND cp.status = 'pago'"
            
            # Group by
            query_receitas += " GROUP BY cliente_id"
            query_despesas += " GROUP BY tipo_servico_id"
            
            # Executar queries
            cursor.execute(query_receitas, params)
            receitas_por_cliente = cursor.fetchall()
            
            cursor.execute(query_despesas, params)
            despesas_por_tipo = cursor.fetchall()
            
            # Calcular totais
            total_receitas = sum(r['total_receitas'] for r in receitas_por_cliente)
            total_despesas = sum(d['total_despesas'] for d in despesas_por_tipo)
            margem = total_receitas - total_despesas
            margem_percentual = (margem / total_receitas * 100) if total_receitas > 0 else 0
            
            return {
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'margem_bruta': margem,
                'margem_percentual': margem_percentual,
                'receitas_por_cliente': receitas_por_cliente,
                'despesas_por_tipo': despesas_por_tipo
            }
```

**Arquivos a criar:**
- [ ] `models/margem_gerencial.py`
- [ ] `routes/relatorios.py` (ou expandir existente)
- [ ] `templates/relatorios/margem_gerencial.html`
- [ ] `static/js/chart.js` (para gráficos)

---

## 📅 CRONOGRAMA SUGERIDO

### Semana 1-2: Ajustar Fluxo de Baixa
- Dia 1-2: Tela de baixa contas a pagar
- Dia 3-4: Backend de baixa + movimentação bancária
- Dia 5-6: Tela de baixa contas a receber
- Dia 7: Testes e ajustes

### Semana 3-4: Margem Gerencial
- Dia 1-2: Model de cálculo de margem
- Dia 3-4: Tela com filtros
- Dia 5-6: Gráficos e visualizações
- Dia 7: Exportação Excel/PDF

### Semana 5-6: Conciliação Bancária
- Dia 1-2: Migration e models
- Dia 3-4: Importação de Excel
- Dia 5-6: Tela de conciliação
- Dia 7: Algoritmo de matching automático

---

## 💡 DICAS DE IMPLEMENTAÇÃO

1. **Use Transações**: Ao movimentar conta bancária, use transações SQL
2. **Logs de Auditoria**: Registre quem fez cada baixa/conciliação
3. **Validações**: Não permitir baixa sem conta bancária
4. **Permissões**: Apenas admin pode fazer baixas
5. **Backup**: Antes de qualquer alteração em massa

---

## 📚 REFERÊNCIAS ÚTEIS

- Chart.js: https://www.chartjs.org/ (para gráficos)
- Pandas: https://pandas.pydata.org/ (para importar Excel)
- ReportLab: https://www.reportlab.com/ (para gerar PDF)

---

**Última atualização:** 27/12/2025
