# 🧪 GUIA DE TESTES - Sistema Financeiro MeetCall

## ✅ Testes Automatizados (Concluídos)

Acabamos de executar os testes automatizados e **TUDO PASSOU**:
- ✅ Parsers de extrato bancário (Itaú e Banco do Brasil)
- ✅ Movimentação de contas bancárias (débito/crédito)
- ✅ Estrutura do banco de dados
- ✅ 347 lançamentos processados dos 3 extratos

---

## 📋 TESTES MANUAIS NO NAVEGADOR

### **PASSO 1: Iniciar o Sistema**

```powershell
python app.py
```

**Resultado esperado:**
- Sistema inicia na porta 5000
- Mensagem: "Running on http://127.0.0.1:5000"

---

### **PASSO 2: Fazer Login**

1. Abrir navegador: `http://localhost:5000`
2. Fazer login com usuário **admin**
3. Você verá o dashboard principal

---

### **TESTE A: Fluxo Completo de Contas a Pagar** 💳

#### **A.1 - Cadastrar uma Conta a Pagar**

1. Menu → **Contas a Pagar** → **Nova Conta**
2. Preencher:
   - **Fornecedor**: Selecione qualquer fornecedor
   - **Descrição**: `Teste de Pagamento - Energia Elétrica`
   - **Valor**: `1500,00`
   - **Data Emissão**: Hoje
   - **Data Vencimento**: Hoje
   - **Referência**: `12/2025` (já preenche automaticamente)
3. **Salvar**

**✅ Verificar:**
- Mensagem de sucesso aparece (canto superior direito)
- Conta criada com status **PENDENTE**
- **Conta bancária**: Vazia (não preenchida)

---

#### **A.2 - Dar Baixa/Pagar a Conta**

1. Na lista de contas a pagar, clicar em **"Baixar/Pagar"** na conta criada
2. Você verá a tela de pagamento com:
   - ℹ️ Informações da conta (fornecedor, valor, vencimento)
   - **Campo novo**: **Conta Bancária** (obrigatório)
3. Preencher:
   - **Data Pagamento**: Hoje
   - **Conta Bancária**: Selecione qualquer conta (ex: Banco do Brasil)
   - **Juros**: `0,00`
   - **Multa**: `0,00`
   - **Desconto**: `0,00`
4. **Total a Pagar**: Deve mostrar R$ 1.500,00
5. Clicar em **"Confirmar Pagamento"**

**✅ Verificar:**
- Mensagem de sucesso aparece
- Conta mudou para status **PAGO**
- **Importante**: Vá em **Contas Bancárias** e veja que o saldo foi **debitado automaticamente**!

**Exemplo:**
```
Saldo antes: R$ 50.000,00
Pagamento: - R$ 1.500,00
Saldo depois: R$ 48.500,00 ✅
```

---

### **TESTE B: Fluxo Completo de Contas a Receber** 💰

#### **B.1 - Cadastrar uma Conta a Receber**

1. Menu → **Contas a Receber** → **Nova Conta**
2. Preencher:
   - **Cliente**: Selecione qualquer cliente
   - **Descrição**: `Teste de Recebimento - Serviço Prestado`
   - **Valor**: `5000,00`
   - **Data Emissão**: Hoje
   - **Data Vencimento**: Hoje
   - **Referência**: `12/2025` (já preenche automaticamente)
3. **Salvar**

**✅ Verificar:**
- Conta criada com status **PENDENTE**
- **Conta bancária**: Vazia

---

#### **B.2 - Dar Baixa/Receber a Conta**

1. Na lista de contas a receber, clicar em **"Receber"** na conta criada
2. Você verá a tela de recebimento
3. Preencher:
   - **Data Recebimento**: Hoje
   - **Conta Bancária**: Selecione qualquer conta (ex: Itaú)
   - **Desconto**: `0,00`
4. Clicar em **"Confirmar Recebimento"**

**✅ Verificar:**
- Mensagem de sucesso aparece
- Conta mudou para status **RECEBIDO**
- Vá em **Contas Bancárias** e veja que o saldo foi **creditado automaticamente**!

**Exemplo:**
```
Saldo antes: R$ 48.500,00
Recebimento: + R$ 5.000,00
Saldo depois: R$ 53.500,00 ✅
```

---

### **TESTE C: Validações e Alertas** ⚠️

#### **C.1 - Tentar dar baixa sem conta bancária**

1. Cadastre uma nova conta a pagar
2. Tente dar baixa **SEM selecionar** conta bancária
3. **Resultado esperado**: Mensagem de erro "Conta bancária é obrigatória"

---

#### **C.2 - Alerta de saldo insuficiente**

1. Encontre uma conta bancária com saldo baixo
2. Tente pagar uma conta com valor **maior que o saldo**
3. **Resultado esperado**: 
   - Alerta JavaScript: "⚠️ ATENÇÃO: Saldo insuficiente!"
   - Mostra saldo disponível vs valor a pagar
   - Pergunta se deseja continuar mesmo assim
   - Se confirmar, permite (saldo fica negativo)

---

### **TESTE D: Consultar Movimentações** 📊

#### **D.1 - Ver contas pagas/recebidas**

1. Menu → **Contas a Pagar**
2. Filtrar por **Status: PAGO**
3. **Verificar** que as contas têm:
   - ✅ Campo **"Conta Bancária"** preenchido
   - ✅ Data de pagamento
   - ✅ Referência (MM/AAAA)

---

#### **D.2 - Ver saldos das contas bancárias**

1. Menu → **Contas Bancárias**
2. Você verá todas as contas com seus saldos atualizados
3. **Conferir** que os saldos refletem os pagamentos/recebimentos feitos

---

## 🎯 CHECKLIST DE VALIDAÇÃO COMPLETA

Use esta checklist para confirmar que tudo está funcionando:

### **Funcionalidades Básicas**
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Menu de navegação funciona

### **Contas a Pagar**
- [ ] Consegue cadastrar nova conta
- [ ] Conta fica com status PENDENTE
- [ ] Campo "referência" preenche automaticamente (MM/AAAA)
- [ ] Tela de baixa abre corretamente
- [ ] Campo "Conta Bancária" é obrigatório
- [ ] Ao confirmar pagamento:
  - [ ] Status muda para PAGO
  - [ ] Saldo da conta bancária diminui automaticamente
  - [ ] Mensagem de sucesso aparece

### **Contas a Receber**
- [ ] Consegue cadastrar nova conta
- [ ] Conta fica com status PENDENTE
- [ ] Campo "referência" preenche automaticamente
- [ ] Tela de recebimento abre corretamente
- [ ] Campo "Conta Bancária" é obrigatório
- [ ] Ao confirmar recebimento:
  - [ ] Status muda para RECEBIDO
  - [ ] Saldo da conta bancária aumenta automaticamente
  - [ ] Mensagem de sucesso aparece

### **Contas Bancárias**
- [ ] Lista todas as contas
- [ ] Mostra saldos atualizados
- [ ] Método debitar() funciona (testes automatizados ✅)
- [ ] Método creditar() funciona (testes automatizados ✅)

### **Extratos Bancários** (Preparado)
- [ ] Parser Itaú funciona (testes automatizados ✅)
- [ ] Parser Banco do Brasil funciona (testes automatizados ✅)
- [ ] Tabelas de conciliação criadas ✅
- [ ] 347 lançamentos processados com sucesso ✅

---

## 📊 ESTATÍSTICAS DOS TESTES AUTOMATIZADOS

### **Extrato Itaú:**
- ✅ 113 lançamentos processados
- 38 créditos = R$ 67.811.228,00
- 75 débitos = R$ 55.630.694,00

### **Extrato BB Filial:**
- ✅ 94 lançamentos processados
- 13 créditos = R$ 4.071.054,17
- 81 débitos = R$ 4.071.982,62

### **Extrato BB Matriz:**
- ✅ 140 lançamentos processados
- 20 créditos = R$ 2.997.380,16
- 120 débitos = R$ 2.997.380,16

**TOTAL: 347 lançamentos bancários prontos para conciliação!**

---

## 🚀 PRÓXIMOS PASSOS

Após validar tudo acima, podemos implementar:

1. **Tela de Importação de Extrato**
   - Upload de arquivo Excel
   - Processamento automático
   - Salvar no banco de dados

2. **Tela de Conciliação**
   - Listar lançamentos do extrato
   - Matching automático com contas pagas/recebidas
   - Conciliação manual para divergências

3. **Margem Gerencial**
   - Dashboard de análise
   - Filtros por cliente, período, tipo
   - Gráficos e exportação

---

## 💡 DICAS

- **Flash Messages**: Agora aparece apenas 1 mensagem no canto superior direito (não empurra mais o conteúdo)
- **Valores**: Todos formatados em R$ 1.500,00
- **Referência**: Preenche automaticamente como MM/AAAA baseado na data de emissão
- **Saldos**: Atualizam em tempo real após cada baixa

---

## ❓ PROBLEMAS COMUNS

**"Conta bancária é obrigatória"**
→ É esperado! Selecione uma conta antes de confirmar

**"Saldo insuficiente"**
→ Alerta preventivo, mas permite continuar se confirmar

**Flash message não aparece**
→ Verificar se está logado como admin

**Saldo não atualizou**
→ Verificar se a baixa foi confirmada com sucesso (mensagem verde)

---

**Última atualização:** 27/12/2025
