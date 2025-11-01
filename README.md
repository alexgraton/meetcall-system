# 🟣🟠 MeetCall System - Sistema de Gestão Empresarial

Sistema web completo desenvolvido em **Python Flask** com **Tailwind CSS** para gestão empresarial integrada.

## 🎨 Características

- ✅ **Sistema de Autenticação** com login seguro e controle de sessão
- 📊 **Dashboard Interativo** com indicadores estilo PowerBI
- 📈 **Gráficos Dinâmicos** com Chart.js
- 📱 **Design Responsivo** com Tailwind CSS 3.x
- 🎯 **Menu de Navegação** lateral com organização por módulos
- � **Gestão Completa** de clientes, fornecedores e produtos
- 💰 **Controle Financeiro** avançado com relatórios gerenciais
- 🏦 **Conciliação Bancária** automática com matching inteligente
- 📧 **Notificações por Email** com alertas automáticos

## 📦 Módulos Implementados

### 1. Cadastros
- **Clientes**: CNPJ/CPF, contatos, endereços
- **Fornecedores**: Gestão completa de parceiros
- **Produtos**: Catálogo com categorias e preços
- **Usuários**: Controle de acesso ao sistema

### 2. Financeiro
- **Contas a Pagar**: Controle de despesas com fornecedores
- **Contas a Receber**: Gestão de recebíveis de clientes
- **Lançamentos Manuais**: Ajustes e movimentações diversas
- **Contas Bancárias**: Múltiplas contas com saldo em tempo real

### 3. Relatórios Financeiros
- **DRE** (Demonstração do Resultado do Exercício): Análise de receitas, despesas e lucro líquido
- **Balanço Patrimonial**: Ativos, passivos e patrimônio líquido com indicadores
- **DFC** (Demonstração de Fluxo de Caixa): Método direto com análise de atividades
- **Análise Horizontal**: Comparação entre períodos com variação percentual
- **Análise Vertical**: Composição percentual com gráficos

### 4. Conciliação Bancária
- **Import CSV**: Parser automático para extratos bancários (Bradesco, Itaú, genérico)
- **Matching Inteligente**: Algoritmo fuzzy com similaridade de 60%+
- **Reconciliação**: Vinculação automática de transações bancárias
- **Histórico**: Acompanhamento de conciliações realizadas

### 5. Notificações
- **Alertas de Vencimento**: Email automático para contas vencendo em N dias
- **Alertas de Saldo Baixo**: Notificação quando conta bancária < limite
- **Emails HTML**: Templates responsivos com tabelas formatadas
- **Agendamento**: Suporte para execução automática via cron/Task Scheduler

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.8+
- MySQL Server 8.0+
- pip (gerenciador de pacotes Python)

### 2. Configuração do Banco de Dados

1. **Instale e configure o MySQL Server**
2. **Crie um arquivo `.env`** baseado no `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. **Edite o arquivo `.env`** com suas credenciais do MySQL:
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=sua_senha_aqui
   MYSQL_DATABASE=meetcall_system
   ```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Inicializar o Banco de Dados

```bash
python init_database.py
```

Este script irá:
- Criar o banco de dados `meetcall_system`
- Criar a tabela `users`
- Solicitar a criação de um usuário administrador
- Opcionalmente criar um usuário de teste

**Modo não interativo** (usa senha padrão - apenas desenvolvimento):
```bash
python init_database.py --no-interactive
```

### 5. Criar Novos Usuários (Opcional)

Para adicionar novos usuários após a inicialização:

```bash
python create_user.py
```

Para listar usuários existentes:

```bash
python create_user.py --list
```

### 6. Executar o Sistema

```bash
python app.py
```

### 7. Acessar no Navegador

Abra: `http://localhost:5000`

### 8. Testar Conexão com Banco (Opcional)

```bash
python test_connection.py
```

Ou acesse: `http://localhost:5000/test-db`

## 🔑 Acesso ao Sistema

As credenciais são definidas durante a inicialização do banco de dados.

Se você executou em modo não interativo, use:
- Email: `admin@meetcall.com`
- Senha: `Admin@123`

**⚠️ Importante:** Altere a senha padrão após o primeiro login!

## 📂 Estrutura do Projeto

```
meetcall-system/
│
├── app.py                      # Aplicação Flask principal
├── config.py                   # Configurações do sistema
├── database.py                 # Gerenciador do banco MySQL
├── init_database.py           # Script para inicializar o banco
├── requirements.txt            # Dependências Python
├── .env.example               # Exemplo de configuração
├── enviar_alertas.py          # Script de notificações por email
├── README.md                   # Este arquivo
│
├── migrations/                 # Migrações do banco de dados
│   ├── 001_initial_schema.py
│   ├── 002_cadastros.py
│   ├── 003_financeiro.py
│   ├── 004_lancamentos.py
│   ├── 005_contas_bancarias.py
│   └── 006_conciliacao_bancaria.py
│
├── models/                     # Modelos de negócio
│   ├── relatorios.py          # Relatórios financeiros (DRE, Balanço, DFC)
│   └── conciliacao.py         # Conciliação bancária
│
├── routes/                     # Rotas/Controllers
│   ├── auth.py                # Autenticação
│   ├── clientes.py            # CRUD clientes
│   ├── fornecedores.py        # CRUD fornecedores
│   ├── produtos.py            # CRUD produtos
│   ├── contas_pagar.py        # Contas a pagar
│   ├── contas_receber.py      # Contas a receber
│   ├── lancamentos.py         # Lançamentos manuais
│   ├── contas_bancarias.py    # Contas bancárias
│   ├── relatorios.py          # Relatórios gerenciais
│   └── conciliacao.py         # Conciliação bancária
│
├── utils/                      # Utilitários
│   ├── csv_parser.py          # Parser de extratos CSV
│   └── notificacoes.py        # Sistema de notificações
│
├── templates/                  # Templates HTML
│   ├── base.html              # Template base (navbar, footer)
│   ├── login.html             # Tela de login
│   ├── dashboard.html         # Dashboard com indicadores
│   ├── cadastros/             # Páginas de cadastros
│   ├── financeiro/            # Páginas financeiras
│   ├── relatorios/            # Relatórios gerenciais
│   └── conciliacao/           # Conciliação bancária
│
├── docs/                       # Documentação
│   └── NOTIFICACOES.md        # Manual do sistema de notificações
│
└── uploads/                    # Arquivos enviados
    └── extratos/              # Extratos bancários CSV
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.x + Flask 3.0.0
- **Banco de Dados:** MySQL 8.0+ (18 tabelas)
- **Frontend:** HTML5 + Tailwind CSS 3.x
- **Gráficos:** Chart.js 4.x
- **Ícones:** Font Awesome 6.x
- **Autenticação:** Flask Sessions + bcrypt
- **Configuração:** python-dotenv
- **Email:** smtplib (nativo Python)
- **Matching:** difflib.SequenceMatcher (fuzzy matching)
- **Upload:** Werkzeug secure_filename

## 📊 Relatórios Disponíveis

### DRE - Demonstração do Resultado do Exercício
- Receita Operacional Bruta
- Deduções da Receita (devoluções, impostos)
- Receita Operacional Líquida
- Custos e Despesas
- EBITDA, EBIT, Lucro Líquido
- Margens: Bruta, Operacional, Líquida

### Balanço Patrimonial
- **Ativo**: Circulante + Não Circulante
- **Passivo**: Circulante + Não Circulante
- **Patrimônio Líquido**: Capital Social + Reservas + Lucros
- **Indicadores**: Liquidez Corrente, Liquidez Seca, Endividamento

### DFC - Demonstração de Fluxo de Caixa
- Fluxo Operacional (recebimentos e pagamentos)
- Fluxo de Investimentos
- Fluxo de Financiamentos
- Variação Líquida de Caixa

### Análises Comparativas
- **Horizontal**: Comparação entre períodos (mês a mês, ano a ano)
- **Vertical**: Composição percentual de receitas e despesas

## 🏦 Conciliação Bancária

### Funcionalidades
- Upload de extratos CSV (múltiplos formatos)
- Detecção automática de formato (Bradesco, Itaú, genérico)
- Matching inteligente com algoritmo fuzzy
- Similaridade ponderada:
  - Descrição: 40%
  - Valor: 30%
  - Data: 20%
  - Documento: 10%
- Tolerância: ±3 dias, ±1% valor
- Interface visual com cards de sugestões
- Histórico de conciliações

### Formatos CSV Suportados
- Bradesco (padrão)
- Itaú (padrão)
- Genérico (configurável)
- Delimitadores: `;`, `,`, `|`, `\t`
- Encodings: UTF-8, Latin1, CP1252

## 📧 Sistema de Notificações

### Tipos de Alertas
1. **Vencimentos**: Contas a pagar/receber vencendo em N dias
2. **Saldo Baixo**: Contas bancárias < limite de alerta
3. **Resumo Diário**: Consolidado de pendências

### Configuração
```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=senha-app-gmail
```

### Uso Manual
```bash
# Alertas de vencimentos (7 dias)
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 7 --email admin@empresa.com

# Alertas de saldo baixo
.venv\Scripts\python.exe enviar_alertas.py --tipo saldo --email admin@empresa.com

# Enviar todos os alertas
.venv\Scripts\python.exe enviar_alertas.py --tipo todos --dias 5 --email gestao@empresa.com
```

### Automação
- **Windows**: Task Scheduler (diário às 8:00)
- **Linux**: Cron job (configurável)

Ver documentação completa em `docs/NOTIFICACOES.md`

## 📋 Funcionalidades Implementadas

### ✅ Fase 1 - Base do Sistema
- [x] Sistema de login com autenticação
- [x] Integração com MySQL 8.0+
- [x] Hash seguro de senhas (bcrypt)
- [x] Configuração por variáveis de ambiente
- [x] Dashboard com cards de indicadores
- [x] Menu de navegação responsivo
- [x] Flash messages para feedback
- [x] 18 tabelas estruturadas

### ✅ Fase 2 - Módulos Avançados
- [x] **Relatórios Financeiros**: DRE, Balanço, DFC, Análises H/V
- [x] **Conciliação Bancária**: Import CSV, matching fuzzy, histórico
- [x] **Notificações**: Alertas de vencimento e saldo baixo por email

### ✅ Cadastros Completos
- [x] CRUD de Clientes (CNPJ/CPF, endereços, contatos)
- [x] CRUD de Fornecedores
- [x] CRUD de Produtos (categorias, preços)
- [x] CRUD de Usuários

### ✅ Financeiro Operacional
- [x] Contas a Pagar (fornecedores, parcelas, status)
- [x] Contas a Receber (clientes, recebimentos)
- [x] Lançamentos Manuais (ajustes, transferências)
- [x] Contas Bancárias (saldos, múltiplas contas)

### 🔄 Roadmap Futuro
- [ ] Dashboard com dados reais (integração completa)
- [ ] Gráficos dinâmicos Chart.js com dados do banco
- [ ] API REST para integração externa
- [ ] Exportação PDF dos relatórios
- [ ] Excel/CSV export
- [ ] Modo escuro
- [ ] Recuperação de senha
- [ ] Logs de auditoria
- [ ] Controle de permissões (roles)

## 🔒 Segurança

✅ **Implementações de Segurança:**

1. ✅ Hash seguro de senhas com bcrypt
2. ✅ Banco de dados MySQL (não mais dicionários em memória)
3. ✅ Variáveis de ambiente para configurações sensíveis
4. ✅ Context managers para conexões seguras com banco
5. ✅ Validação de usuários ativos

⚠️ **Para Produção, implemente também:**

1. Configure HTTPS/SSL
2. Adicione validação rigorosa de formulários
3. Implemente proteção CSRF
4. Configure firewall do banco de dados
5. Adicione rate limiting
6. Implemente logs de auditoria
7. Use SECRET_KEY mais robusta

## 📱 Screenshots

### Tela de Login
- Logo centralizado com círculos decorativos
- Cores roxo e laranja da empresa
- Design moderno e limpo

### Dashboard
- 4 cards de indicadores principais
- Gráfico de barras (chamadas por dia)
- Gráfico de pizza (status das chamadas)
- Tabela de chamadas recentes com paginação

## 🤝 Contribuindo

Este é um projeto inicial. Sugestões e melhorias são bem-vindas!

## 📄 Licença

Projeto desenvolvido para Meet Call © 2025

---

**Desenvolvido com 💜🧡 usando Python Flask + Tailwind CSS**
