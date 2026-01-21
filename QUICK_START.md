# Quick Start - Meet Call System - Produção

## Início Rápido

### 1. Primeira Instalação

```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente virtual
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar banco de dados
# Editar .env com suas credenciais MySQL (copiar de .env.example)
cp .env.example .env
# Editar .env com suas configurações

# 5. Inicializar banco de dados
python init_database.py

# 6. Criar usuário administrador
python create_user.py
```

### 2. Iniciar Sistema

#### Desenvolvimento
```bash
python app.py
```

#### Produção
```bash
# Windows:
start_production.bat

# Linux/Mac:
chmod +x start_production.sh
./start_production.sh
```

### 3. Acessar Sistema
- URL: http://localhost:5000
- Login: usar email e senha criados em create_user.py

## Novas Funcionalidades - Configurações

### Acesse: Configurações > Gerenciamento de Usuários

1. **Cadastrar Novo Usuário**
   - Clique em "Cadastrar Novo Usuário"
   - Preencha: Nome, Email, Senha, Perfil
   - Perfis disponíveis: Usuário ou Administrador

2. **Listar e Editar Usuários**
   - Clique em "Listar e Editar Usuários"
   - Lista todos os usuários cadastrados
   - Botão amarelo: Editar dados do usuário
   - Botão laranja: Resetar senha do usuário

3. **Alterar Minha Senha**
   - Em "Segurança" > "Alterar Minha Senha"
   - Informe senha atual e nova senha

4. **Backup do Banco de Dados**
   - Clique em "Gerar Backup Agora"
   - Arquivo .sql será baixado automaticamente
   - Nome do arquivo inclui data e hora

## Requisitos do Sistema

### Para funcionar corretamente:
- Python 3.8 ou superior
- MySQL Server 5.7 ou superior
- MySQL Client Tools (mysqldump) - necessário para backups

### Verificar mysqldump
```bash
mysqldump --version
```

Se não estiver instalado:
- **Windows**: Instalar MySQL Server ou adicionar ao PATH
- **Linux/Ubuntu**: `sudo apt-get install mysql-client`
- **Linux/CentOS**: `sudo yum install mysql`

## Segurança

### IMPORTANTE antes de produção:
1. ✅ Alterar SECRET_KEY no .env
2. ✅ Usar senha forte no MySQL
3. ✅ Não versionar arquivo .env no Git
4. ✅ Fazer backup inicial vazio
5. ✅ Testar recuperação de backup
6. ✅ Configurar firewall adequadamente

### Gerar SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Backup e Restauração

### Backup Manual
```bash
mysqldump -u usuario -p meetcall_system > backup.sql
```

### Restaurar Backup
```bash
mysql -u usuario -p meetcall_system < backup.sql
```

### Backup pela Interface
- Acessar Configurações
- Clicar em "Gerar Backup Agora"
- Arquivo será baixado automaticamente

## Problemas Comuns

### mysqldump não encontrado
**Solução Windows:**
1. Localizar pasta bin do MySQL: `C:\Program Files\MySQL\MySQL Server X.X\bin\`
2. Adicionar ao PATH do sistema
3. Reiniciar terminal/CMD

**Solução Linux:**
```bash
sudo apt-get install mysql-client  # Ubuntu/Debian
sudo yum install mysql             # CentOS/RHEL
```

### Erro ao conectar no banco
1. Verificar se MySQL está rodando
2. Verificar credenciais no .env
3. Verificar se banco de dados existe
4. Executar: `python init_database.py`

### Porta 5000 em uso
Editar scripts de inicialização para usar outra porta:
- `start_production.bat`: trocar `--port=5000`
- `start_production.sh`: trocar `-b 0.0.0.0:5000`

## Suporte

### Documentação Completa
- [DEPLOY_PRODUCAO.md](DEPLOY_PRODUCAO.md) - Guia completo de deploy
- [README.md](README.md) - Documentação geral do sistema
- [docs/](docs/) - Documentação detalhada de módulos

### Logs
- Console mostra erros em tempo real
- Logs de acesso aparecem no terminal
- Para logs em arquivo, redirecionar saída

## Manutenção

### Backup Regular
- Configure backup automático diário (cron ou Task Scheduler)
- Mantenha backups dos últimos 30 dias
- Teste restauração periodicamente

### Atualizações
```bash
# Atualizar dependências
pip install --upgrade -r requirements.txt

# Executar novas migrações (se houver)
python run_migrations.py
```

### Monitoramento
- Verificar uso de disco (backups crescem)
- Monitorar logs de erro
- Revisar acessos de usuários
- Atualizar senhas periodicamente
