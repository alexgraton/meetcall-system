# Sistema de Notificações - MeetCall System

## 📧 Configuração de Email (SMTP)

O sistema de notificações envia alertas por email sobre:
- Contas vencendo em X dias
- Contas bancárias com saldo baixo

### Passo 1: Configurar variáveis de ambiente

Edite o arquivo `.env` (copie de `.env.example` se necessário):

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM=noreply@meetcall.com
```

### Passo 2: Gerar senha de app (Gmail)

Se usar Gmail, você precisa gerar uma **senha de app** (não use sua senha normal):

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "App" > "Outro (nome personalizado)"
3. Digite "MeetCall System"
4. Clique em "Gerar"
5. Copie a senha gerada (16 caracteres)
6. Cole em `SMTP_PASSWORD` no arquivo `.env`

### Passo 3: Testar envio de email

Execute o script de teste:

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 7 --email seu-email@gmail.com
```

Ou teste saldo baixo:

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo saldo --email seu-email@gmail.com
```

Ou envie ambos:

```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo todos --dias 7 --email seu-email@gmail.com
```

## 🔔 Tipos de Alertas

### 1. Alertas de Vencimentos

Envia email quando há contas a pagar ou receber vencendo em X dias.

**Parâmetros:**
- `--tipo vencimentos`
- `--dias N` (padrão: 7 dias)
- `--email destinatario@exemplo.com`

**Exemplo:**
```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo vencimentos --dias 3 --email financeiro@empresa.com
```

### 2. Alertas de Saldo Baixo

Envia email quando contas bancárias estão abaixo do limite de alerta.

**Parâmetros:**
- `--tipo saldo`
- `--email destinatario@exemplo.com`

**Exemplo:**
```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo saldo --email admin@empresa.com
```

### 3. Alertas Completos

Envia ambos os tipos de alerta em sequência.

**Parâmetros:**
- `--tipo todos`
- `--dias N` (para vencimentos)
- `--email destinatario@exemplo.com`

**Exemplo:**
```bash
.venv\Scripts\python.exe enviar_alertas.py --tipo todos --dias 5 --email gestao@empresa.com
```

## 📅 Automação (Opcional)

### Agendamento no Windows (Task Scheduler)

Para enviar alertas automaticamente todos os dias às 8:00:

1. Abra o **Agendador de Tarefas** (Task Scheduler)
2. Clique em "Criar Tarefa Básica"
3. Nome: "MeetCall - Alertas Financeiros"
4. Gatilho: Diariamente às 8:00
5. Ação: Iniciar programa
   - Programa: `C:\PROJETOS\meetcall-system\.venv\Scripts\python.exe`
   - Argumentos: `enviar_alertas.py --tipo todos --dias 7 --email admin@empresa.com`
   - Iniciar em: `C:\PROJETOS\meetcall-system`

### Agendamento no Linux (Cron)

Adicione ao crontab:

```bash
crontab -e
```

Adicione a linha:

```bash
0 8 * * * cd /caminho/para/meetcall-system && .venv/bin/python enviar_alertas.py --tipo todos --dias 7 --email admin@empresa.com
```

## 🎯 Lógica dos Alertas

### Contas Vencendo

O sistema busca:
- Contas a pagar com status `pendente` ou `vencida`
- Contas a receber com status `pendente` ou `vencida`
- Data de vencimento entre hoje e hoje + N dias

### Saldo Baixo

O sistema busca:
- Contas bancárias ativas (`is_active = 1`)
- Com `limite_alerta` configurado (> 0)
- Com `saldo_atual < limite_alerta`

**Dica:** Configure o `limite_alerta` nas contas bancárias para receber alertas quando o saldo ficar crítico.

## 🔧 Solução de Problemas

### Erro: "Configure as variáveis de ambiente SMTP_USER e SMTP_PASSWORD"

Verifique se o arquivo `.env` existe e contém:
```bash
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
```

### Erro: "smtplib.SMTPAuthenticationError"

- Verifique se a senha de app está correta
- Certifique-se de que a verificação em 2 etapas está ativada no Gmail
- Gere uma nova senha de app

### Erro: "Nenhuma conta vencendo no período"

Isso é normal se não houver contas próximas do vencimento. O script não envia email se não houver alertas.

## 📊 Exemplo de Email Enviado

O email HTML inclui:

**Alertas de Vencimentos:**
- Tabela de contas a pagar com fornecedor, descrição, vencimento e valor
- Tabela de contas a receber com cliente, descrição, vencimento e valor
- Totais calculados

**Alertas de Saldo Baixo:**
- Tabela de contas bancárias com banco, agência, conta, saldo atual, limite e percentual
- Indicação visual (cores) para destacar criticidade

## 💡 Próximos Passos

1. ✅ Configure o SMTP no `.env`
2. ✅ Teste o envio manual
3. ✅ Configure o `limite_alerta` nas contas bancárias
4. ✅ Agende a tarefa para execução automática
5. ✅ Ajuste os dias de antecedência conforme necessidade

---

**Nota:** Este sistema usa o módulo `smtplib` nativo do Python, sem dependências externas além das já instaladas no projeto.
