# 🏗️ Arquitetura do Sistema Financeiro - MeetCall

## 📊 Resumo das Especificações

**Objetivo:** Sistema completo de gestão financeira com controle de despesas, receitas, conciliação bancária e relatórios gerenciais.

**Usuários Simultâneos:** 7-8  
**Volume Mensal:** ~4.000 transações  
**Modelo:** Multi-filial com relatórios consolidados e por filial

---

## 🗄️ Modelagem do Banco de Dados

### **Módulo 0 - Filiais**

```sql
CREATE TABLE filiais (
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
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### **Módulo 1 - Tipos de Serviços**

```sql
CREATE TABLE tipos_servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo ENUM('despesa', 'receita') NOT NULL,
    parent_id INT NULL, -- Para hierarquia
    aliquota DECIMAL(5,2), -- Percentual
    margem_esperada DECIMAL(5,2), -- Percentual
    ordem INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES tipos_servicos(id)
);
```

### **Módulo 2 - Fornecedores**

```sql
CREATE TABLE fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    tipo_pessoa ENUM('fisica', 'juridica') NOT NULL,
    cnpj_cpf VARCHAR(18) NOT NULL UNIQUE,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    email VARCHAR(255),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    cep VARCHAR(10),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    tipo_servico_id INT,
    observacoes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE fornecedores_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    is_principal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE
);

CREATE TABLE fornecedores_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fornecedor_id INT NOT NULL,
    campo_alterado VARCHAR(100) NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    alterado_por INT NOT NULL,
    alterado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
    FOREIGN KEY (alterado_por) REFERENCES users(id)
);
```

### **Módulo 3 - Clientes**

```sql
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    tipo_pessoa ENUM('fisica', 'juridica') NOT NULL,
    cnpj_cpf VARCHAR(18) NOT NULL UNIQUE,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    email VARCHAR(255),
    telefone VARCHAR(20),
    celular VARCHAR(20),
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
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE clientes_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tipo_servico_id INT NOT NULL,
    margem_acordada DECIMAL(5,2),
    valor_mensal DECIMAL(15,2),
    data_inicio DATE,
    data_fim DATE,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id)
);

CREATE TABLE clientes_contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    is_principal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE clientes_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    campo_alterado VARCHAR(100) NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    alterado_por INT NOT NULL,
    alterado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (alterado_por) REFERENCES users(id)
);
```

### **Módulo 4 - Plano de Contas**

```sql
CREATE TABLE plano_contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE, -- Ex: 1.1.01.001
    descricao VARCHAR(255) NOT NULL,
    tipo ENUM('receita', 'despesa', 'ativo', 'passivo', 'patrimonio') NOT NULL,
    nivel INT NOT NULL, -- 1, 2, 3, 4
    parent_id INT NULL,
    aceita_lancamento BOOLEAN DEFAULT TRUE, -- Contas sintéticas não aceitam
    dre_grupo ENUM('receita_bruta', 'deducoes', 'receita_liquida', 'custo_servicos', 
                   'lucro_bruto', 'despesas_operacionais', 'ebitda', 'resultado') NULL,
    ordem INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES plano_contas(id)
);

CREATE TABLE centro_custos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    descricao VARCHAR(255) NOT NULL,
    filial_id INT,
    parent_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filial_id) REFERENCES filiais(id),
    FOREIGN KEY (parent_id) REFERENCES centro_custos(id)
);

CREATE TABLE plano_contas_vinculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plano_conta_id INT NOT NULL,
    entidade_tipo ENUM('fornecedor', 'cliente') NOT NULL,
    entidade_id INT NOT NULL,
    is_padrao BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id)
);
```

### **Módulo 5 - Contas a Pagar**

```sql
CREATE TABLE contas_pagar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(50),
    filial_id INT NOT NULL,
    fornecedor_id INT NOT NULL,
    plano_conta_id INT NOT NULL,
    centro_custo_id INT,
    tipo_servico_id INT,
    descricao VARCHAR(255) NOT NULL,
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    valor_original DECIMAL(15,2) NOT NULL,
    valor_juros DECIMAL(15,2) DEFAULT 0,
    valor_multa DECIMAL(15,2) DEFAULT 0,
    valor_desconto DECIMAL(15,2) DEFAULT 0,
    valor_total DECIMAL(15,2) NOT NULL,
    valor_pago DECIMAL(15,2),
    status ENUM('pendente', 'pago', 'vencido', 'cancelado') DEFAULT 'pendente',
    forma_pagamento ENUM('dinheiro', 'pix', 'ted', 'doc', 'boleto', 'cheque', 'cartao') NULL,
    conta_bancaria VARCHAR(100),
    observacoes TEXT,
    recorrente BOOLEAN DEFAULT FALSE,
    frequencia_recorrencia ENUM('semanal', 'mensal', 'bimestral', 'trimestral', 
                                 'semestral', 'anual') NULL,
    parcela_numero INT DEFAULT 1,
    parcela_total INT DEFAULT 1,
    conta_pagar_pai_id INT NULL, -- Para parcelamentos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (filial_id) REFERENCES filiais(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
    FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id),
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id),
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id),
    FOREIGN KEY (conta_pagar_pai_id) REFERENCES contas_pagar(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### **Módulo 6 - Contas a Receber**

```sql
CREATE TABLE contas_receber (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(50),
    filial_id INT NOT NULL,
    cliente_id INT NOT NULL,
    plano_conta_id INT NOT NULL,
    centro_custo_id INT,
    tipo_servico_id INT,
    descricao VARCHAR(255) NOT NULL,
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_recebimento DATE,
    valor_original DECIMAL(15,2) NOT NULL,
    valor_juros DECIMAL(15,2) DEFAULT 0,
    valor_multa DECIMAL(15,2) DEFAULT 0,
    valor_desconto DECIMAL(15,2) DEFAULT 0,
    valor_total DECIMAL(15,2) NOT NULL,
    valor_recebido DECIMAL(15,2),
    status ENUM('pendente', 'recebido', 'vencido', 'cancelado') DEFAULT 'pendente',
    forma_recebimento ENUM('dinheiro', 'pix', 'ted', 'doc', 'boleto', 'cheque', 'cartao') NULL,
    conta_bancaria VARCHAR(100),
    observacoes TEXT,
    recorrente BOOLEAN DEFAULT FALSE,
    frequencia_recorrencia ENUM('semanal', 'mensal', 'bimestral', 'trimestral', 
                                 'semestral', 'anual') NULL,
    parcela_numero INT DEFAULT 1,
    parcela_total INT DEFAULT 1,
    conta_receber_pai_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (filial_id) REFERENCES filiais(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (plano_conta_id) REFERENCES plano_contas(id),
    FOREIGN KEY (centro_custo_id) REFERENCES centro_custos(id),
    FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servicos(id),
    FOREIGN KEY (conta_receber_pai_id) REFERENCES contas_receber(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### **Módulo 7 e 8 - Movimentações Bancárias**

```sql
CREATE TABLE contas_bancarias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filial_id INT NOT NULL,
    banco_codigo VARCHAR(10) NOT NULL,
    banco_nome VARCHAR(100) NOT NULL,
    agencia VARCHAR(20) NOT NULL,
    conta VARCHAR(20) NOT NULL,
    tipo ENUM('corrente', 'poupanca', 'investimento') NOT NULL,
    saldo_inicial DECIMAL(15,2) DEFAULT 0,
    saldo_atual DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filial_id) REFERENCES filiais(id)
);

CREATE TABLE movimentacoes_bancarias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_bancaria_id INT NOT NULL,
    tipo ENUM('despesa', 'receita') NOT NULL,
    data_movimentacao DATE NOT NULL,
    data_compensacao DATE,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    saldo_anterior DECIMAL(15,2),
    saldo_posterior DECIMAL(15,2),
    documento VARCHAR(100),
    origem ENUM('manual', 'importacao') DEFAULT 'manual',
    arquivo_importacao VARCHAR(255),
    conciliado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### **Módulo 9 - Conciliação Bancária**

```sql
CREATE TABLE conciliacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movimentacao_bancaria_id INT NOT NULL,
    entidade_tipo ENUM('conta_pagar', 'conta_receber') NOT NULL,
    entidade_id INT NOT NULL,
    tipo_conciliacao ENUM('automatica', 'manual') NOT NULL,
    confianca_score DECIMAL(3,2), -- 0 a 1 para automática
    conciliado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    conciliado_por INT NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (movimentacao_bancaria_id) REFERENCES movimentacoes_bancarias(id),
    FOREIGN KEY (conciliado_por) REFERENCES users(id)
);
```

### **Módulo Anexos**

```sql
CREATE TABLE anexos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entidade_tipo ENUM('conta_pagar', 'conta_receber', 'cliente', 'fornecedor') NOT NULL,
    entidade_id INT NOT NULL,
    tipo_anexo ENUM('nf', 'boleto', 'comprovante', 'contrato', 'outros') NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho_arquivo VARCHAR(500) NOT NULL,
    tamanho_kb INT,
    mime_type VARCHAR(100),
    descricao TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT NOT NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);
```

### **Módulo Auditoria**

```sql
CREATE TABLE auditoria (
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
    FOREIGN KEY (usuario_id) REFERENCES users(id)
);
```

---

## 🎨 Estrutura de Diretórios

```
meetcall-system/
├── app.py                          # Aplicação principal
├── config.py                       # Configurações
├── database.py                     # Gerenciador de DB
├── requirements.txt                # Dependências
├── .env                            # Variáveis de ambiente
│
├── models/                         # Modelos de dados
│   ├── __init__.py
│   ├── filial.py
│   ├── tipo_servico.py
│   ├── fornecedor.py
│   ├── cliente.py
│   ├── plano_conta.py
│   ├── conta_pagar.py
│   ├── conta_receber.py
│   ├── movimentacao.py
│   └── conciliacao.py
│
├── routes/                         # Rotas/Controllers
│   ├── __init__.py
│   ├── auth.py
│   ├── filiais.py
│   ├── tipos_servicos.py
│   ├── fornecedores.py
│   ├── clientes.py
│   ├── plano_contas.py
│   ├── contas_pagar.py
│   ├── contas_receber.py
│   ├── movimentacoes.py
│   ├── conciliacoes.py
│   └── relatorios.py
│
├── services/                       # Lógica de negócio
│   ├── __init__.py
│   ├── cnpj_validator.py          # Validação CNPJ
│   ├── import_service.py          # Importação extratos
│   ├── conciliacao_service.py     # Lógica conciliação
│   └── relatorio_service.py       # Geração relatórios
│
├── utils/                          # Utilitários
│   ├── __init__.py
│   ├── decorators.py              # Decorators customizados
│   ├── validators.py              # Validações
│   └── file_handler.py            # Upload de arquivos
│
├── templates/                      # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   │
│   ├── filiais/
│   │   ├── lista.html
│   │   └── form.html
│   │
│   ├── cadastros/                 # Cadastros base
│   │   ├── tipos_servicos.html
│   │   ├── fornecedores.html
│   │   ├── clientes.html
│   │   └── plano_contas.html
│   │
│   ├── financeiro/                # Movimentações
│   │   ├── contas_pagar.html
│   │   ├── contas_receber.html
│   │   ├── movimentacoes.html
│   │   └── conciliacao.html
│   │
│   └── relatorios/                # Relatórios
│       ├── extrato_diario.html
│       ├── extrato_mensal.html
│       ├── margem_operacional.html
│       ├── ranking_clientes.html
│       └── ranking_despesas.html
│
├── static/                         # Arquivos estáticos
│   ├── css/
│   ├── js/
│   ├── img/
│   └── uploads/                   # Anexos
│
└── migrations/                     # Scripts de migração
    ├── 001_create_tables.sql
    ├── 002_seed_data.sql
    └── 003_add_indexes.sql
```

---

## 🔧 Tecnologias

- **Backend:** Python 3.13 + Flask
- **Banco de Dados:** MySQL 8.0
- **Frontend:** HTML5 + Tailwind CSS + JavaScript
- **Gráficos:** Chart.js
- **Upload:** Flask-Upload
- **Validações:** WTForms
- **Export:** ReportLab (PDF), openpyxl (Excel)

---

## 📅 Cronograma Detalhado

### **Semana 1-2: Cadastros Base**
- [ ] Filiais (CRUD completo)
- [ ] Tipos de Serviços (com hierarquia)
- [ ] Plano de Contas (estrutura DRE)
- [ ] Centro de Custos

### **Semana 3-4: Cadastros de Parceiros**
- [ ] Fornecedores (com contatos e histórico)
- [ ] Clientes (com produtos e histórico)
- [ ] Validação de CNPJ
- [ ] Upload de documentos

### **Semana 5-6: Contas a Pagar/Receber**
- [ ] Contas a Pagar (parcelamento/recorrência)
- [ ] Contas a Receber (parcelamento/recorrência)
- [ ] Anexos (NF, boletos, comprovantes)
- [ ] Alertas de vencimento

### **Semana 7-8: Movimentações Bancárias**
- [ ] Cadastro de contas bancárias
- [ ] Lançamento manual de despesas
- [ ] Lançamento manual de receitas
- [ ] Importação de extratos (BB, Santander, Bradesco, Itaú)

### **Semana 9-10: Conciliação**
- [ ] Algoritmo de conciliação automática
- [ ] Interface de conciliação manual
- [ ] Sugestões inteligentes
- [ ] Detecção de duplicados

### **Semana 11-12: Relatórios**
- [ ] Dashboard principal
- [ ] Extrato diário (filtros por filial/banco/tipo)
- [ ] Extrato mensal (consolidado e comparativo)
- [ ] DRE (Demonstração do Resultado do Exercício)
- [ ] Margem operacional
- [ ] Ranking de clientes
- [ ] Ranking de despesas
- [ ] Exportação PDF/Excel

### **Semana 13-14: Finalização**
- [ ] Sistema de permissões refinado
- [ ] Auditoria completa
- [ ] Testes de performance
- [ ] Documentação
- [ ] Deploy

---

**Pronto para começar a implementação! Por qual módulo você quer que eu comece?** 🚀
