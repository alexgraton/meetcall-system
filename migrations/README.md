# 🗄️ Migrations do Sistema MeetCall

## Migration Consolidada

Este diretório contém a **migration inicial consolidada** do sistema.

### 📄 Arquivo Principal

**`000_initial_schema.sql`** - Schema completo do banco de dados

### 🎯 O que esta migration cria:

| # | Tabela | Descrição |
|---|--------|-----------|
| 1 | `users` | Usuários do sistema (admin/user) |
| 2 | `filiais` | Filiais da empresa |
| 3 | `tipos_servicos` | Tipos de serviços/despesas/receitas |
| 4 | `plano_contas` | Plano de contas contábil |
| 5 | `centro_custos` | Centros de custos para rateio |
| 6 | `fornecedores` | Cadastro de fornecedores |
| 7 | `fornecedor_contatos` | Contatos dos fornecedores |
| 8 | `clientes` | Cadastro de clientes |
| 9 | `cliente_contatos` | Contatos dos clientes |
| 10 | `cliente_produtos` | Produtos/serviços contratados |
| 11 | `contas_bancarias` | Contas bancárias da empresa |
| 12 | `contas_pagar` | Contas a pagar |
| 13 | `contas_receber` | Contas a receber |
| 14 | `lancamentos_manuais` | Lançamentos manuais |
| 15 | `conciliacoes_bancarias` | Histórico de conciliações |
| 16 | `transacoes_extrato` | Transações de extratos importados |
| 17 | `rateio_contas` | Rateio por centro de custo |
| 18 | `auditoria` | Log de auditoria |

**Total: 18 tabelas**

---

## 🚀 Como Usar

### 1️⃣ Executar a Migration

Na raiz do projeto:

```bash
python run_migrations.py
```

Isso irá:
- ✅ Criar todas as 18 tabelas
- ✅ Configurar todas as foreign keys
- ✅ Criar todos os índices
- ✅ Preparar o banco para uso

### 2️⃣ Criar Primeiro Usuário Admin

Após executar a migration:

```bash
python init_database.py
```

Siga as instruções para criar o usuário administrador.

---

## ⚠️ Notas Importantes

### Para Instalação Fresh (banco vazio):
1. Execute `python run_migrations.py`
2. Execute `python init_database.py`
3. Acesse o sistema

### Para Banco Já Existente:
⚠️ A migration usa `CREATE TABLE IF NOT EXISTS`
- Se as tabelas já existem, **não serão recriadas**
- Se as tabelas não existem, **serão criadas**
- É seguro executar múltiplas vezes

### Ordem de Criação:
A migration respeita a ordem de dependências:
1. `users` é criada **primeiro** (outras tabelas referenciam)
2. Tabelas base (filiais, tipos_servicos, etc.)
3. Tabelas de cadastro (fornecedores, clientes)
4. Tabelas transacionais (contas_pagar, contas_receber)
5. Tabelas auxiliares (rateio, auditoria)

---

## 🔄 Histórico

### Versão 1.0 (2025-12-28)
- ✅ Migration consolidada criada
- ✅ 18 tabelas do sistema
- ✅ Schema completo para produção
- ✅ Removidas migrations fragmentadas antigas

---

## 📝 Schema Completo

O schema foi consolidado a partir do sistema em **produção atual** (28/12/2025), incluindo:

✅ Sistema de usuários com roles (admin/user)  
✅ Gestão de filiais  
✅ Cadastro de fornecedores e clientes  
✅ Contas a pagar e receber  
✅ Contas bancárias  
✅ Conciliação bancária  
✅ Centro de custos e rateio  
✅ Lançamentos manuais  
✅ Auditoria completa  

---

## 🎉 Pronto para Produção!

Esta migration representa o **ponto zero** do sistema:
- Schema validado e testado
- Todas as funcionalidades operacionais
- Pronto para deploy em novos ambientes
