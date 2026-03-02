# 🚀 Consulta Automática de CNPJ - Guia Rápido

## ✨ O que foi implementado?

Sistema completo de consulta automática de CNPJ que preenche automaticamente os dados de uma empresa ao digitar o CNPJ nos formulários de:
- ✅ **Cadastro de Clientes** (`/clientes/novo`)
- ✅ **Cadastro de Fornecedores** (`/fornecedores/novo`)

## 📦 Arquivos Criados/Modificados

### ✅ Novos Arquivos

1. **`services/cnpj_consulta.py`** - Serviço principal com sistema de fallback entre 3 APIs
2. **`test_cnpj_consulta.py`** - Script de testes
3. **`docs/CONSULTA_CNPJ.md`** - Documentação completa
4. **`docs/CONSULTA_CNPJ_README.md`** - Este guia rápido

### 🔧 Arquivos Modificados

1. **`requirements.txt`** - Adicionado `requests>=2.31.0`
2. **`routes/clientes.py`** - Nova rota `/clientes/buscar-cnpj/<cnpj>`
3. **`routes/fornecedores.py`** - Nova rota `/fornecedores/buscar-cnpj/<cnpj>`
4. **`templates/clientes/form.html`** - JavaScript para consulta automática
5. **`templates/fornecedores/form.html`** - JavaScript para consulta automática

## 🎯 Como Funciona?

### Para o Usuário Final

**Para Clientes:**
1. Acesse **Cadastros > Clientes > Novo Cliente**
2. Selecione **"Pessoa Jurídica (CNPJ)"**
3. Digite o CNPJ (com ou sem formatação)
4. **Automático**: Assim que digitar 14 dígitos, o sistema:
   - Valida o CNPJ
   - Consulta em APIs públicas
   - Preenche todos os campos automaticamente
5. Revise e edite os dados se necessário
6. Salve o cadastro

**Para Fornecedores:**
1. Acesse **Cadastros > Fornecedores > Novo Fornecedor**
2. Selecione **"Pessoa Jurídica (CNPJ)"**
3. Digite o CNPJ (com ou sem formatação)
4. **Automático**: Assim que digitar 14 dígitos, o sistema:
   - Valida o CNPJ
   - Consulta em APIs públicas
   - Preenche todos os campos automaticamente
5. Revise e edite os dados se necessário
6. Salve o cadastro

### Campos Preenchidos Automaticamente

- ✅ Razão Social
- ✅ Nome Fantasia
- ✅ Email
- ✅ Telefone
- ✅ CEP
- ✅ Endereço
- ✅ Número
- ✅ Complemento
- ✅ Bairro
- ✅ Cidade
- ✅ Estado

## 🔌 APIs Utilizadas (com Fallback)

O sistema tenta 3 APIs nesta ordem:

1. **BrasilAPI** (primeira tentativa) ⚡
2. **ReceitaWS** (se a primeira falhar) 🔄
3. **CNPJ.WS** (última opção) 🛡️

## 🧪 Testar a Funcionalidade

Execute o script de teste:

```bash
python test_cnpj_consulta.py
```

Resultado esperado: **✅ SISTEMA FUNCIONANDO CORRETAMENTE!**

## 📋 Instalação

A dependência já foi adicionada ao `requirements.txt`. Se necessário, instale:

```bash
pip install requests
```

ou

```bash
pip install -r requirements.txt
```

## 🎨 Feedback Visual

Durante o uso, você verá:

- 🔄 **"Consultando CNPJ..."** - Buscando dados
- ✅ **"Dados preenchidos automaticamente (BrasilAPI)"** - Sucesso
- ❌ **"CNPJ não encontrado"** - CNPJ inexistente
- ⚠️ **"Limite de consultas atingido"** - Aguarde alguns minutos

## 🔐 Segurança

- ✅ Validação de CNPJ antes de consultar
- ✅ Timeout de 10 segundos por API
- ✅ Tratamento robusto de erros
- ✅ Logs detalhados
- ✅ Não sobrescreve dados já preenchidos

## 📊 Exemplo de Uso

**Digite:** `33.000.167/0001-01` ou `33000167000101`

**Resultado automático:**
```
Razão Social: PETROLEO BRASILEIRO S A PETROBRAS
Nome Fantasia: PETROBRAS
Endereço: REPUBLICA DO CHILE
Número: 65
Bairro: CENTRO
Cidade: RIO DE JANEIRO
Estado: RJ
CEP: 20031-170
... e mais
```

## 🐛 Problemas Comuns

### "Erro ao consultar CNPJ"
- Verifique sua conexão com internet
- Aguarde alguns minutos e tente novamente

### "Limite de consultas atingido"
- Aguarde 1-2 minutos
- O sistema tentará outra API automaticamente

### "CNPJ não encontrado"
- Verifique se digitou corretamente
- CNPJ pode ser muito recente
- Preencha manualmente os dados

## 📚 Documentação Completa

Para detalhes técnicos, consulte: **`docs/CONSULTA_CNPJ.md`**

## ✅ Status da Implementação

- [x] Serviço de consulta com 3 APIs
- [x] Sistema de fallback
- [x] Endpoint backend
- [x] Interface JavaScript
- [x] Validação de CNPJ
- [x] Tratamento de erros
- [x] Feedback visual
- [x] Testes automatizados
- [x] Documentação completa
- [x] Logs detalhados

## 🎉 Pronto para Usar!

A funcionalidade está **100% implementada e testada**. Acesse os formulários e comece a usar:

- **Clientes**: Cadastros > Clientes > Novo Cliente
- **Fornecedores**: Cadastros > Fornecedores > Novo Fornecedor

---

**Desenvolvido em:** 19 de Fevereiro de 2026  
**Versão:** 1.0.0  
**Status:** ✅ Produção
