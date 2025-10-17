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

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Sistema

```bash
python app.py
```

### 3. Acessar no Navegador

Abra: `http://localhost:5000`

## 🔑 Credenciais de Teste

**Usuário Administrador:**
- Email: `admin@meetcall.com`
- Senha: `admin123`

**Usuário Comum:**
- Email: `usuario@meetcall.com`
- Senha: `user123`

## 📂 Estrutura do Projeto

```
meetcall-system/
│
├── app.py                      # Aplicação Flask principal
├── requirements.txt            # Dependências Python
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
- **Frontend:** HTML5 + Tailwind CSS
- **Gráficos:** Chart.js
- **Ícones:** Font Awesome
- **Autenticação:** Flask Sessions

## 📋 Funcionalidades

### ✅ Implementadas

- [x] Sistema de login com autenticação
- [x] Dashboard com cards de indicadores
- [x] Gráficos interativos (barras e pizza)
- [x] Tabela de chamadas recentes
- [x] Menu de navegação responsivo
- [x] Páginas: Cadastros, Configurações, Perfil
- [x] Sistema de logout
- [x] Flash messages para feedback

### 🔄 Próximas Implementações

- [ ] Integração com banco de dados (SQLite/PostgreSQL)
- [ ] CRUD completo de clientes
- [ ] Sistema de relatórios em PDF
- [ ] API REST
- [ ] Filtros e busca avançada
- [ ] Exportação de dados (Excel/CSV)
- [ ] Notificações em tempo real
- [ ] Modo escuro

## 🔒 Segurança

⚠️ **IMPORTANTE:** Este é um projeto de demonstração. Para produção:

1. Altere a `SECRET_KEY` em `app.py`
2. Use um banco de dados real (não dicionários em memória)
3. Implemente hash de senhas (bcrypt)
4. Configure HTTPS
5. Adicione validação de formulários
6. Implemente proteção CSRF
7. Use variáveis de ambiente para configurações sensíveis

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
