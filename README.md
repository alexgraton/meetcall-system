# 🟣🟠 Meet Call - Sistema de Gerenciamento

Sistema web desenvolvido em **Python Flask** com **Tailwind CSS** para gerenciamento de chamadas e indicadores.

## 🎨 Características

- ✅ **Tela de Login** com logo e cores da empresa (roxo e laranja)
- 📊 **Dashboard** com indicadores estilo PowerBI
- 📈 **Gráficos interativos** com Chart.js
- 📱 **Design responsivo** com Tailwind CSS
- 🔐 **Sistema de autenticação** com sessions
- 🎯 **Menu lateral** com navegação completa

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
├── README.md                   # Este arquivo
│
├── templates/                  # Templates HTML
│   ├── base.html              # Template base (navbar, footer)
│   ├── login.html             # Tela de login
│   ├── dashboard.html         # Dashboard com indicadores
│   ├── cadastros.html         # Página de cadastros
│   ├── configuracoes.html     # Configurações do sistema
│   └── perfil.html            # Perfil do usuário
│
└── static/                     # Arquivos estáticos
    ├── css/                   # Estilos customizados
    ├── js/                    # Scripts JavaScript
    └── images/                # Imagens e logos
```

## 🎨 Cores da Empresa

- **Roxo Principal:** `#6B46C1`
- **Roxo Escuro:** `#553C9A`
- **Laranja:** `#FF7A3D`
- **Laranja Escuro:** `#E66A31`
- **Rosa:** `#C794C7`
- **Azul:** `#2C3E7C`

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.x + Flask
- **Banco de Dados:** MySQL 8.0+
- **Frontend:** HTML5 + Tailwind CSS
- **Gráficos:** Chart.js
- **Ícones:** Font Awesome
- **Autenticação:** Flask Sessions + bcrypt
- **Configuração:** python-dotenv

## 📋 Funcionalidades

### ✅ Implementadas

- [x] Sistema de login com autenticação
- [x] **Integração com banco MySQL**
- [x] **Hash seguro de senhas (bcrypt)**
- [x] **Configuração por variáveis de ambiente**
- [x] Dashboard com cards de indicadores
- [x] Gráficos interativos (barras e pizza)
- [x] Tabela de chamadas recentes
- [x] Menu de navegação responsivo
- [x] Páginas: Cadastros, Configurações, Perfil
- [x] Sistema de logout
- [x] Flash messages para feedback

### 🔄 Próximas Implementações

- [ ] CRUD completo de clientes
- [ ] Sistema de relatórios em PDF
- [ ] API REST
- [ ] Filtros e busca avançada
- [ ] Exportação de dados (Excel/CSV)
- [ ] Notificações em tempo real
- [ ] Modo escuro
- [ ] Recuperação de senha
- [ ] Logs de auditoria

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
