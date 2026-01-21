# Migrations - MeetCall System

## Arquivo Único de Migração

Este diretório contém a migração consolidada com todo o schema do banco de dados.

### Arquivo
- `001_schema_completo.sql` - Schema completo do sistema (22 tabelas + 2 views)

### Como Executar

Na raiz do projeto:

```bash
python run_migrations.py
```

Ou execute diretamente o SQL no MySQL:

```bash
mysql -u usuario -p meetcall_system < migrations/001_schema_completo.sql
```

### Estrutura Criada

**22 Tabelas:**
1. users
2. filiais
3. tipos_servicos
4. plano_contas
5. centro_custos
6. fornecedores
7. fornecedor_contatos
8. clientes
9. cliente_contatos
10. cliente_produtos
11. contas_bancarias
12. contas_pagar
13. contas_receber
14. lancamentos_manuais
15. conciliacoes_bancarias
16. transacoes_extrato
17. rateio_contas
18. capacity_historico
19. margem_competencias
20. margem_rateio_receitas
21. margem_rateio_despesas
22. auditoria

**2 Views:**
- vw_capacity_atual
- vw_margem_resumo

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
