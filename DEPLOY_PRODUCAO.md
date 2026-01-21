# Guia de Deploy para Produção - Meet Call System

## Preparativos Realizados

### Tela de Configurações Atualizada
- ✅ Removido: Notificações por E-mail
- ✅ Removido: Modo Escuro
- ✅ Removido: Idioma
- ✅ Removido: Autenticação em 2 Fatores
- ✅ Removido: Encerrar todas as sessões
- ✅ Adicionado: Gerenciamento de Usuários (cadastrar, editar, resetar senha)
- ✅ Adicionado: Backup do Banco de Dados

## Funcionalidades de Gerenciamento

### Gerenciamento de Usuários
A tela de configurações agora permite:
- **Cadastrar novos usuários**: Definir nome, email, senha e perfil (usuário ou admin)
- **Editar usuários**: Atualizar dados de usuários existentes
- **Resetar senhas**: Administradores podem resetar senhas de outros usuários
- **Alterar própria senha**: Cada usuário pode alterar sua senha

### Backup do Banco de Dados
- Botão para gerar backup completo do banco de dados MySQL
- Utiliza o comando `mysqldump` para gerar arquivo .sql
- Download automático do arquivo de backup com timestamp
- **IMPORTANTE**: Requer que o `mysqldump` esteja instalado e disponível no PATH do sistema

## Checklist para Deploy

### 1. Requisitos do Servidor
```bash
# Instalar Python 3.8+
python --version

# Instalar MySQL Server
mysql --version

# Instalar MySQL Client Tools (inclui mysqldump)
mysqldump --version
```

### 2. Configuração do Ambiente
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados
```bash
# Editar config.py com as credenciais de produção
# Verificar:
# - MYSQL_CONFIG (host, user, password, database)
# - SECRET_KEY (usar uma chave forte e única)

# Inicializar banco de dados
python init_database.py

# Criar usuário administrador inicial
python create_user.py
```

### 4. Verificações de Segurança
- [ ] Alterar SECRET_KEY em `config.py` para valor único e seguro
- [ ] Configurar credenciais MySQL fortes
- [ ] Criar backup inicial do banco de dados vazio
- [ ] Testar funcionalidade de backup
- [ ] Criar usuário administrador inicial
- [ ] Testar login e permissões

### 5. Servidor de Produção

#### Opção 1: Usando Gunicorn (Recomendado para Linux)
```bash
# Instalar Gunicorn
pip install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Opção 2: Usando Waitress (Recomendado para Windows)
```bash
# Instalar Waitress
pip install waitress

# Executar
waitress-serve --port=5000 --host=0.0.0.0 app:app
```

#### Opção 3: Usando Apache/Nginx com mod_wsgi
Consultar documentação específica do servidor web escolhido.

### 6. Configurações Adicionais

#### Variáveis de Ambiente (Opcional)
Criar arquivo `.env` para variáveis sensíveis:
```env
SECRET_KEY=sua_chave_secreta_aqui
MYSQL_HOST=localhost
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=meetcall_db
```

#### Firewall
```bash
# Permitir porta da aplicação (ex: 5000)
# Windows Firewall ou Linux iptables/ufw
```

### 7. Backup Automático (Recomendado)

#### Script de Backup Automático (Linux/Cron)
```bash
# Criar script backup.sh
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mysqldump -u usuario -psenha meetcall_db > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
# Manter apenas últimos 30 dias
find "$BACKUP_DIR" -name "backup_*.sql" -mtime +30 -delete
```

```bash
# Adicionar ao crontab (executar diariamente às 2h)
crontab -e
0 2 * * * /path/to/backup.sh
```

#### Script de Backup Automático (Windows/Task Scheduler)
```batch
@echo off
set BACKUP_DIR=C:\backups
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
mysqldump -u usuario -psenha meetcall_db > "%BACKUP_DIR%\backup_%TIMESTAMP%.sql"
```

### 8. Monitoramento
- [ ] Configurar logs da aplicação
- [ ] Monitorar uso de disco (backups podem crescer)
- [ ] Configurar alertas de erro
- [ ] Testar recuperação de backup

### 9. Primeira Execução
```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# 2. Inicializar banco de dados
python init_database.py

# 3. Criar usuário admin
python create_user.py

# 4. Executar aplicação
python app.py  # Desenvolvimento
# ou
waitress-serve --port=5000 app:app  # Produção Windows
# ou
gunicorn -w 4 -b 0.0.0.0:5000 app:app  # Produção Linux
```

### 10. Teste de Funcionalidades
- [ ] Login com usuário admin
- [ ] Acessar Configurações
- [ ] Cadastrar novo usuário
- [ ] Editar usuário
- [ ] Resetar senha de usuário
- [ ] Alterar própria senha
- [ ] Gerar backup do banco de dados
- [ ] Verificar arquivo de backup gerado

## Notas Importantes

### Sobre mysqldump
O backup do banco de dados requer que o `mysqldump` esteja instalado e disponível no PATH do sistema:

**Windows:**
- Geralmente instalado com MySQL Server em: `C:\Program Files\MySQL\MySQL Server X.X\bin\`
- Adicionar este diretório ao PATH do sistema

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install mysql-client

# CentOS/RHEL
sudo yum install mysql
```

**Testar:**
```bash
mysqldump --version
```

### Segurança
- NUNCA commitar `config.py` com credenciais reais no Git
- Usar `.gitignore` para excluir arquivos sensíveis
- Fazer backup regular do banco de dados
- Manter registro de alterações de usuários

### Manutenção
- Backups devem ser testados periodicamente
- Monitorar espaço em disco para backups
- Revisar logs de acesso regularmente
- Atualizar dependências com segurança: `pip list --outdated`

## Contato e Suporte
Para dúvidas sobre o sistema, consultar a documentação em `/docs/` ou os arquivos README específicos de cada módulo.
