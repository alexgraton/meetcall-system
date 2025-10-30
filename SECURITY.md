# 🔒 Guia de Segurança - MeetCall System

## ✅ Melhorias de Segurança Implementadas

### 1. Remoção de Credenciais Hardcoded

❌ **ANTES:**
- Senhas fixas no código (`admin123`, `user123`)
- Credenciais visíveis em `init_database.py`
- Risco de segurança se o código for compartilhado

✅ **DEPOIS:**
- Senhas solicitadas de forma interativa
- Sem credenciais fixas no código
- Senhas com hash bcrypt no banco

### 2. Scripts de Gerenciamento de Usuários

#### `init_database.py` - Inicialização do Sistema
```bash
# Modo interativo (recomendado)
python init_database.py

# Modo não interativo (desenvolvimento)
python init_database.py --no-interactive
```

**Funcionalidades:**
- ✅ Solicita criação de usuário admin com senha personalizada
- ✅ Validação de senha (mínimo 6 caracteres)
- ✅ Confirmação de senha
- ✅ Opção de criar usuário de teste

#### `create_user.py` - Criar Novos Usuários
```bash
# Criar novo usuário
python create_user.py

# Listar usuários existentes
python create_user.py --list
```

**Funcionalidades:**
- ✅ Criação de usuários após inicialização
- ✅ Listagem de todos os usuários
- ✅ Validação de senha
- ✅ Verificação de email duplicado

#### `change_password.py` - Alterar Senha
```bash
python change_password.py
```

**Funcionalidades:**
- ✅ Alteração de senha de qualquer usuário
- ✅ Validação e confirmação de senha
- ✅ Busca por email
- ✅ Hash seguro com bcrypt

### 3. Gestão de Configurações

#### `.env` - Variáveis de Ambiente (NÃO COMMITAR!)
```env
MYSQL_PASSWORD=sua_senha_real_aqui
```
- ✅ Senhas isoladas do código
- ✅ Arquivo ignorado pelo Git
- ✅ Não é compartilhado

#### `.env.example` - Template (pode commitar)
```env
MYSQL_PASSWORD=sua_senha_mysql_aqui
```
- ✅ Template sem senhas reais
- ✅ Pode ser compartilhado
- ✅ Guia para outros desenvolvedores

### 4. Segurança de Senhas

**Características:**
- 🔐 Hash bcrypt (força 12)
- 🔐 Salt automático único por senha
- 🔐 Senhas nunca armazenadas em texto puro
- 🔐 Validação de comprimento mínimo
- 🔐 Confirmação obrigatória

**Exemplo de hash no banco:**
```
$2b$12$KIXvRGv3VxEZzVxq0.qO8OxGpVxKy6dZm7VyQzQgZCxQzQgZCxQz
```

### 5. Fluxo de Trabalho Recomendado

#### Primeira vez (Setup):
```bash
# 1. Configure o .env com sua senha MySQL
cp .env.example .env
# Edite .env e adicione sua senha

# 2. Teste a conexão
python test_connection.py

# 3. Inicialize o banco e crie o admin
python init_database.py

# 4. Inicie a aplicação
python app.py
```

#### Gerenciamento de Usuários:
```bash
# Criar novo usuário
python create_user.py

# Listar usuários
python create_user.py --list

# Alterar senha
python change_password.py
```

### 6. Boas Práticas

✅ **FAÇA:**
- Use senhas fortes (mínimo 8 caracteres, letras, números, símbolos)
- Altere senhas padrão imediatamente
- Mantenha `.env` fora do controle de versão
- Use `.env.example` como template
- Execute `init_database.py` no modo interativo

❌ **NÃO FAÇA:**
- Commitar arquivo `.env` com senhas reais
- Usar senhas fracas ou previsíveis
- Compartilhar credenciais em código
- Reutilizar senhas de outros sistemas
- Executar em produção com senhas padrão

### 7. Checklist de Segurança

- [ ] Arquivo `.env` está no `.gitignore`
- [ ] Senhas foram alteradas dos valores padrão
- [ ] Usuários desnecessários foram removidos
- [ ] Senhas têm no mínimo 8 caracteres
- [ ] Backup das credenciais em local seguro
- [ ] SECRET_KEY do Flask foi alterada
- [ ] Senha do MySQL é diferente da senha do admin

### 8. Arquivo de Demonstração

O arquivo `app_demo.py` mantém credenciais fixas porque é apenas para **demonstração sem banco de dados**. Ele não deve ser usado em produção.

**Demo (apenas visualização):**
- Email: `demo@meetcall.com`
- Senha: `demo123`

---

## 📚 Documentação Adicional

Para mais informações, consulte:
- `README.md` - Instruções de instalação
- `database.py` - Implementação do banco de dados
- `config.py` - Configurações do sistema
