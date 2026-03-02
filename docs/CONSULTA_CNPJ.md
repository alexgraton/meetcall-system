# Consulta Automática de CNPJ

## 📋 Descrição

Funcionalidade que permite consultar automaticamente os dados de uma empresa em APIs públicas ao digitar um CNPJ em formulários de cadastro. O sistema implementa um mecanismo de fallback entre 3 APIs diferentes para garantir alta disponibilidade.

## 🎯 Funcionalidades

- ✅ Consulta automática ao completar 14 dígitos do CNPJ
- ✅ Sistema de fallback entre 3 APIs públicas
- ✅ Preenchimento automático de campos do formulário
- ✅ Validação de CNPJ antes da consulta
- ✅ Mensagens de feedback ao usuário
- ✅ Permite edição manual dos campos preenchidos
- ✅ Tratamento robusto de erros

## 🔌 APIs Utilizadas

O sistema tenta as APIs na seguinte ordem de prioridade:

### 1. BrasilAPI (Primeira opção)
- **URL**: `https://brasilapi.com.br/api/cnpj/v1/{cnpj}`
- **Vantagens**: Rápida, gratuita, sem necessidade de cadastro
- **Timeout**: 10 segundos

### 2. ReceitaWS (Fallback)
- **URL**: `https://www.receitaws.com.br/v1/cnpj/{cnpj}`
- **Vantagens**: Dados oficiais da Receita Federal
- **Timeout**: 10 segundos
- **Observação**: Retorna `status: 'ERROR'` quando CNPJ não é encontrado

### 3. CNPJ.WS (Último fallback)
- **URL**: `https://publica.cnpj.ws/cnpj/{cnpj}`
- **Vantagens**: API pública completa
- **Timeout**: 10 segundos

## 📦 Arquivos Criados/Modificados

### Novos Arquivos

1. **`services/cnpj_consulta.py`**
   - Serviço principal de consulta de CNPJ
   - Implementa as 3 funções de consulta (uma para cada API)
   - Função principal `buscar_cnpj()` com lógica de fallback
   - Normalização de dados entre APIs diferentes
   - Sistema robusto de logs

2. **`test_cnpj_consulta.py`**
   - Script de testes para validar a funcionalidade
   - 4 casos de teste diferentes
   - Execução independente

3. **`docs/CONSULTA_CNPJ.md`**
   - Este arquivo de documentação

### Arquivos Modificados

1. **`routes/clientes.py`**
   - Adicionado import do serviço `cnpj_consulta`
   - Nova rota `GET /clientes/buscar-cnpj/<cnpj>`
   - Tratamento de erros com status HTTP apropriados

2. **`templates/clientes/form.html`**
   - Adicionada função JavaScript `consultarCNPJ()`
   - Adicionada função `preencherFormularioCNPJ()`
   - Adicionada função auxiliar `formatarTelefone()`
   - Integração automática ao validar CNPJ
   - Feedback visual durante consulta

## 🚀 Como Usar

### Para Usuários

1. **Acesse o formulário de cadastro de clientes**
   - Menu: Cadastros > Clientes > Novo Cliente

2. **Selecione "Pessoa Jurídica (CNPJ)"**

3. **Digite o CNPJ**
   - Pode digitar com ou sem formatação
   - Exemplos: `33.000.167/0001-01` ou `33000167000101`

4. **Aguarde o preenchimento automático**
   - Assim que o CNPJ for validado (14 dígitos)
   - O sistema consultará automaticamente
   - Verá uma mensagem "Consultando CNPJ..."
   - Os campos serão preenchidos automaticamente

5. **Revise e edite se necessário**
   - Todos os campos podem ser editados manualmente
   - Apenas campos vazios serão preenchidos automaticamente

### Para Desenvolvedores

#### Endpoint da API

```http
GET /clientes/buscar-cnpj/<cnpj>
```

**Parâmetros:**
- `cnpj`: CNPJ com ou sem formatação (14 dígitos)

**Respostas:**

**Sucesso (200):**
```json
{
  "success": true,
  "message": "CNPJ consultado com sucesso",
  "api_utilizada": "BrasilAPI",
  "data": {
    "razao_social": "PETRÓLEO BRASILEIRO S.A. - PETROBRAS",
    "nome": "PETROBRAS",
    "cnpj": "33000167000101",
    "cep": "20231-030",
    "rua": "Avenida Henrique Valadares",
    "numero": "28",
    "complemento": "",
    "bairro": "Centro",
    "cidade": "Rio de Janeiro",
    "estado": "RJ",
    "telefone": "2121212121",
    "email": "exemplo@petrobras.com.br",
    "situacao": "ATIVA",
    "atividade_principal": "Extração de petróleo e gás natural"
  }
}
```

**CNPJ Inválido (400):**
```json
{
  "success": false,
  "message": "CNPJ inválido. Deve conter 14 dígitos.",
  "error_code": "invalid_cnpj"
}
```

**CNPJ Não Encontrado (404):**
```json
{
  "success": false,
  "message": "CNPJ não encontrado em nenhuma base de dados.",
  "error_code": "not_found"
}
```

**Limite de Requisições (429):**
```json
{
  "success": false,
  "message": "Limite de requisições atingido. Tente novamente em alguns minutos.",
  "error_code": "rate_limit"
}
```

**Erro do Servidor (500):**
```json
{
  "success": false,
  "message": "Não foi possível consultar o CNPJ. As APIs estão temporariamente indisponíveis.",
  "error_code": "service_unavailable"
}
```

## 🧪 Testes

Execute o script de testes:

```bash
python test_cnpj_consulta.py
```

O script testará:
1. CNPJ válido (Petrobras)
2. CNPJ inválido (formato incorreto)
3. CNPJ não encontrado
4. CNPJ com formatação

## 📊 Campos Preenchidos Automaticamente

| Campo | Descrição |
|-------|-----------|
| Razão Social | Nome empresarial registrado |
| Nome Fantasia | Nome comercial (usa razão social se vazio) |
| Email | Email da empresa |
| Telefone | Telefone formatado: (99) 99999-9999 |
| CEP | CEP formatado: 99999-999 |
| Endereço | Logradouro/Rua completo |
| Número | Número do endereço |
| Complemento | Complemento do endereço |
| Bairro | Bairro |
| Cidade | Município |
| Estado | UF (sigla) |

## 🎨 Feedback Visual

### Estados do Campo CNPJ

1. **Digitando**: Campo normal
2. **Validando**: Spinner de validação
3. **CNPJ Válido**: Borda verde + ícone ✓
4. **Consultando**: Spinner + mensagem "Consultando CNPJ..."
5. **Dados Preenchidos**: Campos com fundo verde claro (2s)
6. **Erro**: Borda amarela + mensagem de erro (5s)

### Mensagens

- ✅ "Dados preenchidos automaticamente (BrasilAPI)"
- 🔄 "Consultando CNPJ..."
- ❌ "CNPJ não encontrado"
- ⚠️ "Limite de consultas atingido. Tente novamente mais tarde."

## 🔧 Configuração

### Dependências

Adicione ao `requirements.txt`:

```txt
requests>=2.31.0
```

Instale:

```bash
pip install requests
```

### Logs

O sistema registra logs detalhados:

```python
import logging
logger = logging.getLogger(__name__)
```

Logs incluem:
- Qual API está sendo consultada
- Status HTTP de cada resposta
- Qual API retornou sucesso
- Erros detalhados

## 🔐 Segurança e Boas Práticas

1. **Validação antes da consulta**: CNPJ é validado antes de consultar APIs
2. **Timeout configurado**: 10 segundos para cada API
3. **Tratamento de erros robusto**: Todos os erros são capturados e tratados
4. **Dados normalizados**: Formato padrão independente da API
5. **Não sobrescreve dados**: Apenas preenche campos vazios
6. **Rate limiting**: Detecta e informa limite de requisições

## 📝 Limitações Conhecidas

1. **APIs públicas podem estar indisponíveis**
   - Solução: Sistema de fallback tenta 3 APIs diferentes

2. **Limite de requisições**
   - BrasilAPI: Sem limite documentado
   - ReceitaWS: ~3 requisições por minuto
   - CNPJ.WS: Limite por IP
   - Solução: Sistema informa ao usuário e sugere aguardar

3. **Dados podem estar desatualizados**
   - APIs podem ter informações defasadas
   - Solução: Permite edição manual de todos os campos

## 🐛 Resolução de Problemas

### Problema: "Erro ao consultar CNPJ"

**Possíveis causas:**
- Sem conexão com internet
- Todas as APIs indisponíveis
- Firewall bloqueando requisições

**Solução:**
1. Verifique a conexão com internet
2. Tente novamente em alguns minutos
3. Preencha os dados manualmente

### Problema: "Limite de consultas atingido"

**Solução:**
- Aguarde alguns minutos antes de tentar novamente
- O sistema tentará automaticamente outra API

### Problema: "CNPJ não encontrado"

**Possíveis causas:**
- CNPJ muito recente (ainda não nas bases públicas)
- CNPJ inativo ou cancelado
- Erro de digitação

**Solução:**
- Verifique se o CNPJ está correto
- Preencha os dados manualmente
- Consulte no site da Receita Federal

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs da aplicação
2. Execute o script de testes: `python test_cnpj_consulta.py`
3. Consulte a documentação das APIs utilizadas

## 🔄 Próximas Melhorias

- [ ] Cache de consultas (evitar consultas duplicadas)
- [ ] Histórico de consultas realizadas
- [ ] Suporte a mais APIs de fallback
- [ ] Consulta de CPF para pessoas físicas
- [ ] Dashboard de estatísticas de uso

## 📚 Referências

- [BrasilAPI](https://brasilapi.com.br/)
- [ReceitaWS](https://receitaws.com.br/)
- [CNPJ.WS](https://cnpj.ws/)
- [Receita Federal](http://www.receita.fazenda.gov.br/)
