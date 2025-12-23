# 📘 Guia de Uso - MeetCall System

## � Documentação Disponível

- **📖 Este Guia**: Uso geral do sistema
- **📋 Manual de Cadastros**: `CADASTROS.md` - Explicação detalhada sobre Tipos de Serviços, Alíquotas e Margens
- **📧 Sistema de Notificações**: `NOTIFICACOES.md` - Como configurar alertas por email
- **📊 Resumo da Fase 2**: `FASE2_RESUMO.md` - Histórico de implementação

---

## �🚀 Início Rápido

### 1. Configuração Inicial

```bash
# Clone ou entre no diretório
cd c:\PROJETOS\meetcall-system

# Copie o .env.example
copy .env.example .env

# Edite o .env com suas configurações
notepad .env

# Instale dependências (se ainda não fez)
pip install -r requirements.txt

# Inicialize o banco (se ainda não fez)
python init_database.py

# Execute o servidor
python app.py
```

Acesse: http://127.0.0.1:5000

---

## 📊 Usando os Relatórios Financeiros

### DRE - Demonstração do Resultado

1. Acesse: **Financeiro → Relatórios Financeiros**
2. Clique em **"Ver DRE"**
3. Selecione o período:
   - Mês/Ano específico
   - Ou clique em **"Mês Atual"** / **"Ano Atual"**
4. Visualize:
   - Receitas Operacionais
   - Deduções
   - Custos e Despesas
   - EBITDA, EBIT, Lucro Líquido
   - Margens: Bruta, Operacional, Líquida

### Balanço Patrimonial

1. Acesse: **Financeiro → Relatórios Financeiros → Balanço Patrimonial**
2. Escolha a data de referência
3. Analise:
   - Ativo Circulante e Não Circulante
   - Passivo Circulante e Não Circulante
   - Patrimônio Líquido
   - Indicadores financeiros calculados automaticamente

### Análise Horizontal

1. Selecione **dois períodos** para comparação
2. Veja a variação absoluta e percentual
3. Identifique tendências de crescimento/redução

### Análise Vertical

1. Escolha o período
2. Visualize a composição percentual
3. Gráfico de pizza mostra distribuição
4. Top 5 receitas e despesas destacados

---

## 🏦 Conciliação Bancária

### Passo 1: Preparar Extrato CSV

Exporte o extrato do seu banco em formato CSV ou TXT com:
- Data da transação
- Descrição/Histórico
- Valor (débito ou crédito)
- Documento (opcional)

**Formatos suportados:**
- Bradesco (padrão)
- Itaú (padrão)
- Genérico (configurável)

### Passo 2: Importar Extrato

1. Acesse: **Financeiro → Conciliação Bancária**
2. Clique em **"Nova Conciliação"**
3. Selecione a **Conta Bancária**
4. Escolha o **Arquivo CSV/TXT**
5. Configure:
   - Delimitador (`;` padrão, ou `,`, `|`, `tab`)
   - Encoding (`UTF-8` padrão, ou `Latin1`, `CP1252`)
6. Clique em **"Importar Extrato"**

### Passo 3: Matching Automático

O sistema automaticamente:
- Importa todas as transações do extrato
- Busca matches em:
  - Contas a Pagar
  - Contas a Receber
  - Lançamentos Manuais
- Calcula similaridade baseada em:
  - Descrição (40%)
  - Valor (30%)
  - Data (20%)
  - Documento (10%)

### Passo 4: Revisar e Conciliar

1. Veja as **sugestões de matching** com % de similaridade
2. Para cada transação:
   - **Verde**: Já conciliada
   - **Azul**: Sugestões disponíveis
   - **Cinza**: Sem match encontrado

3. Clique em **"Conciliar"** para aceitar a sugestão
4. Ou clique em **"Desconciliar"** para desfazer

### Passo 5: Finalizar

1. Revise o **resumo**:
   - Total de transações
   - Conciliadas
   - Pendentes
2. Status atualizado automaticamente:
   - **Completa**: 100% conciliadas
   - **Parcial**: Algumas pendentes
   - **Pendente**: Nenhuma conciliada

---

## 📧 Sistema de Notificações

### Configuração Inicial

#### 1. Configurar SMTP

Edite o arquivo `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM=noreply@meetcall.com
```

#### 2. Gerar Senha de App (Gmail)

Para Gmail:
1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione **"App"** → **"Outro (nome personalizado)"**
3. Digite: **"MeetCall System"**
4. Copie a senha gerada (16 caracteres)
5. Cole em `SMTP_PASSWORD`

#### 3. Testar Envio

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 7 --email seu-email@gmail.com
```

Se receber o email, configuração está correta! ✅

---

### Tipos de Alertas

#### Alertas de Vencimentos

**Quando usar:** Receber notificação de contas vencendo em X dias

```bash
# Vencendo em 7 dias
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 7 --email financeiro@empresa.com

# Vencendo em 3 dias (urgente)
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 3 --email admin@empresa.com

# Vencendo em 15 dias (planejamento)
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 15 --email gestao@empresa.com
```

**Email inclui:**
- Tabela de contas a pagar com fornecedor, descrição, vencimento e valor
- Tabela de contas a receber com cliente, descrição, vencimento e valor
- Totais calculados
- Cores: Vermelho (pagar), Verde (receber)

#### Alertas de Saldo Baixo

**Quando usar:** Receber notificação quando conta bancária < limite de alerta

**Pré-requisito:** Configure o `limite_alerta` nas contas bancárias

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo saldo --email admin@empresa.com
```

**Email inclui:**
- Banco, agência, conta
- Saldo atual
- Limite de alerta configurado
- Percentual do saldo em relação ao limite
- Alerta vermelho para criticidade

#### Alertas Completos

**Quando usar:** Enviar todos os tipos de alerta de uma vez

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo todos --dias 7 --email gestao@empresa.com
```

Envia:
1. Alertas de vencimentos (se houver contas vencendo)
2. Alertas de saldo baixo (se houver contas abaixo do limite)

---

### Automação de Alertas

#### Windows - Task Scheduler

1. Abra o **Agendador de Tarefas** (Win+R → `taskschd.msc`)
2. Clique em **"Criar Tarefa Básica"**
3. Configurações:
   - **Nome:** MeetCall - Alertas Diários
   - **Gatilho:** Diariamente às 8:00
   - **Ação:** Iniciar programa
   - **Programa:** `C:\PROJETOS\meetcall-system\.venv\Scripts\python.exe`
   - **Argumentos:** `enviar_alertas.py --tipo todos --dias 7 --email admin@empresa.com`
   - **Iniciar em:** `C:\PROJETOS\meetcall-system`
4. Salvar

Agora você receberá alertas todos os dias às 8:00!

#### Linux - Cron

```bash
crontab -e
```

Adicione:
```bash
# Alertas diários às 8:00
0 8 * * * cd /caminho/para/meetcall-system && .venv/bin/python enviar_alertas.py --tipo todos --dias 7 --email admin@empresa.com
```

---

## 🎯 Fluxo de Trabalho Recomendado

### Diário (8:00 AM)
1. ✅ **Receber email** com alertas automáticos
2. ✅ **Revisar** contas vencendo hoje
3. ✅ **Verificar** saldos bancários

### Semanal (Segunda-feira)
1. ✅ **Importar** extratos bancários da semana anterior
2. ✅ **Conciliar** transações automaticamente
3. ✅ **Revisar** pendências de matching
4. ✅ **Gerar** relatórios semanais

### Mensal (Final do mês)
1. ✅ **Fechar** contas do mês
2. ✅ **Gerar DRE** do mês
3. ✅ **Gerar Balanço** do mês
4. ✅ **Análise Horizontal** (mês atual vs anterior)
5. ✅ **Análise Vertical** para composição de custos
6. ✅ **Exportar** relatórios para apresentação

---

## 💡 Dicas e Boas Práticas

### Cadastros
- ✅ Mantenha CNPJ/CPF sempre atualizados
- ✅ Use categorias para classificar produtos
- ✅ Cadastre contatos para facilitar comunicação

### Financeiro
- ✅ Lançar contas assim que emitidas/recebidas
- ✅ Usar `observacoes` para detalhes importantes
- ✅ Anexar documentos (nota fiscal, boleto)
- ✅ Manter status atualizado (pendente → pago/recebido)

### Conciliação
- ✅ Importar extratos semanalmente
- ✅ Revisar matches com similaridade < 80%
- ✅ Criar lançamentos manuais para itens sem match
- ✅ Manter descrições padronizadas

### Notificações
- ✅ Configurar `limite_alerta` em 20-30% do saldo médio
- ✅ Ajustar `--dias` conforme prazo de pagamento
- ✅ Usar emails diferentes para alertas urgentes
- ✅ Revisar alertas diariamente

### Relatórios
- ✅ Gerar mensalmente para acompanhamento
- ✅ Comparar sempre com período anterior
- ✅ Analisar variações > 10% (horizontal)
- ✅ Focar em itens > 5% do total (vertical)

---

## 🔧 Troubleshooting

### Email não está sendo enviado

**Erro:** "Configure as variáveis de ambiente SMTP_USER e SMTP_PASSWORD"

**Solução:**
1. Verifique se o arquivo `.env` existe
2. Confirme que contém `SMTP_USER` e `SMTP_PASSWORD`
3. Reinicie o terminal após editar `.env`

**Erro:** "smtplib.SMTPAuthenticationError"

**Solução:**
1. Verifique se a senha de app está correta
2. Certifique-se de que a verificação em 2 etapas está ativada no Gmail
3. Gere uma nova senha de app

### Conciliação não encontra matches

**Problema:** Matching retorna 0% de similaridade

**Solução:**
1. Verifique se as datas estão no período ±3 dias
2. Confirme se os valores são próximos (±1%)
3. Revise descrições (devem ter palavras em comum)
4. Crie lançamento manual se necessário

### Relatórios não mostram dados

**Problema:** Relatório está vazio

**Solução:**
1. Confirme que há lançamentos no período selecionado
2. Verifique se as contas estão com status correto
3. Revise filtros de data
4. Execute query manualmente no MySQL para validar dados

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `docs/`
2. Verifique o `README.md`
3. Revise logs do sistema
4. Entre em contato com o suporte técnico

---

**MeetCall System v2.0** - Desenvolvido com ❤️  
*Gestão Empresarial Inteligente*
