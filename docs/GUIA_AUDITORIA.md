# ============================================================================
# GUIA DE USO: Sistema de Auditoria
# ============================================================================

## 📋 VISÃO GERAL

O sistema de auditoria registra automaticamente todas as ações dos usuários:
- **Login/Logout**: Captura tentativas de login (sucesso/falha) e logout
- **Inserções**: Registra novos cadastros
- **Atualizações**: Registra modificações
- **Exclusões**: Registra deleções
- **Visualizações**: Registra acesso a registros (opcional)

Todos os logs incluem:
- Usuário que executou a ação
- Data e hora exata
- Endereço IP
- Dados antes e depois (quando aplicável)

---

## 🚀 COMO USAR

### 1. **Login/Logout** (Já Implementado)

O login e logout já estão registrando automaticamente em `app.py`.

```python
# Login bem-sucedido
registrar_login(user['id'], user['email'], sucesso=True)

# Login falho
registrar_login(None, email, sucesso=False)

# Logout
registrar_logout(user_id, email)
```

---

### 2. **Usar Decorators para Auditoria Automática**

#### Exemplo: Auditar Inserção

```python
from utils.auditoria import auditar_acao

@contas_pagar_bp.route('/novo', methods=['POST'])
@login_required
@auditar_acao('contas_pagar', 'insert')  # <-- Adicionar decorator
def criar_conta():
    # ... seu código normal ...
    conta_id = ContaPagarModel.criar(dados)
    return conta_id  # O decorator captura automaticamente
```

#### Exemplo: Auditar Atualização

```python
@contas_pagar_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
@auditar_acao('contas_pagar', 'update')  # <-- Adicionar decorator
def editar_conta(id):
    # ... seu código normal ...
    ContaPagarModel.atualizar(id, dados)
    return redirect(url_for('contas_pagar.detalhes', id=id))
```

#### Exemplo: Auditar Exclusão

```python
from utils.auditoria import auditar_exclusao

@fornecedores_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@auditar_exclusao('fornecedores')  # <-- Decorator específico para exclusão
def excluir_fornecedor(id):
    # ... seu código normal ...
    FornecedorModel.excluir(id)
    return redirect(url_for('fornecedores.lista'))
```

#### Exemplo: Auditar Visualização (Opcional)

```python
from utils.auditoria import auditar_visualizacao

@contas_receber_bp.route('/detalhes/<int:id>')
@login_required
@auditar_visualizacao('contas_receber')  # <-- Registra visualização
def detalhes_conta(id):
    conta = ContaReceberModel.buscar_por_id(id)
    return render_template('contas_receber/detalhes.html', conta=conta)
```

---

### 3. **Registro Manual (Mais Controle)**

Para casos que precisam de mais controle:

```python
from utils.auditoria import registrar_acao_customizada

@app.route('/processar-lote', methods=['POST'])
@login_required
def processar_lote():
    ids_processados = []
    
    for item in itens:
        # Processar item
        resultado = processar(item)
        ids_processados.append(resultado.id)
    
    # Registrar ação customizada
    registrar_acao_customizada(
        tabela='lote_processamento',
        registro_id=lote_id,
        acao='insert',
        dados={
            'total_itens': len(ids_processados),
            'ids': ids_processados,
            'tipo': 'processamento_lote'
        }
    )
    
    return jsonify({'success': True})
```

---

### 4. **Capturar Dados Antes da Modificação**

Para comparar valores antes/depois:

```python
from models.auditoria import AuditoriaModel

@app.route('/atualizar-preco/<int:id>', methods=['POST'])
@login_required
def atualizar_preco(id):
    # Buscar dados ANTES da alteração
    produto_antes = ProdutoModel.buscar(id)
    
    # Atualizar
    novo_preco = request.form.get('preco')
    ProdutoModel.atualizar_preco(id, novo_preco)
    
    # Buscar dados DEPOIS da alteração
    produto_depois = ProdutoModel.buscar(id)
    
    # Registrar com dados antes/depois
    AuditoriaModel.registrar_acao(
        tabela='produtos',
        registro_id=id,
        acao='update',
        usuario_id=session.get('user_id'),
        dados_anteriores={'preco': produto_antes['preco']},
        dados_novos={'preco': produto_depois['preco']},
        ip_address=request.remote_addr
    )
    
    return redirect(url_for('produtos.detalhes', id=id))
```

---

## 🔍 CONSULTAR LOGS DE AUDITORIA

### Interface Web (Admins)

Acesse: **http://localhost:5000/auditoria**

Funcionalidades:
- Filtrar por tabela, ação, data, usuário
- Ver histórico completo de um registro
- Visualizar atividades de um usuário específico
- Estatísticas gerais

### Programaticamente

```python
from models.auditoria import AuditoriaModel

# Listar logs com filtros
logs = AuditoriaModel.listar_logs(
    filtros={
        'tabela': 'contas_pagar',
        'acao': 'update',
        'data_inicio': '2026-01-01',
        'usuario_id': 5
    },
    limit=50
)

# Histórico de um registro específico
historico = AuditoriaModel.obter_historico_registro('fornecedores', 123)

# Atividade de um usuário
atividades = AuditoriaModel.obter_atividade_usuario(user_id=5, limit=100)

# Estatísticas
stats = AuditoriaModel.obter_estatisticas()
```

---

## 📊 EXEMPLOS PRÁTICOS

### Exemplo 1: Auditar CRUD Completo de Fornecedores

```python
# routes/fornecedores.py
from utils.auditoria import auditar_acao, auditar_exclusao, auditar_visualizacao

# CREATE
@fornecedores_bp.route('/novo', methods=['POST'])
@login_required
@auditar_acao('fornecedores', 'insert')
def criar():
    # ... código ...
    return fornecedor_id

# READ
@fornecedores_bp.route('/detalhes/<int:id>')
@login_required
@auditar_visualizacao('fornecedores')
def detalhes(id):
    # ... código ...
    return render_template(...)

# UPDATE
@fornecedores_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
@auditar_acao('fornecedores', 'update')
def editar(id):
    # ... código ...
    return redirect(...)

# DELETE
@fornecedores_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
@auditar_exclusao('fornecedores')
def excluir(id):
    # ... código ...
    return redirect(...)
```

### Exemplo 2: Ver Quem Modificou uma Conta a Pagar

```python
from models.auditoria import AuditoriaModel

# Buscar histórico
historico = AuditoriaModel.obter_historico_registro('contas_pagar', 456)

for log in historico:
    print(f"{log['usuario_nome']} {log['acao']} em {log['data_hora']}")
    if log['dados_anteriores']:
        print(f"  Antes: {log['dados_anteriores']}")
    if log['dados_novos']:
        print(f"  Depois: {log['dados_novos']}")
```

---

## ⚙️ CONFIGURAÇÃO

### 1. Executar Migration

```bash
python migrations/008_auditoria_acoes.py
```

### 2. A tabela `auditoria` já existe, apenas precisa adicionar os novos tipos de ação.

---

## 🔒 SEGURANÇA

- **Campos sensíveis são removidos automaticamente**: passwords, tokens, etc.
- **Apenas admins podem visualizar logs completos**
- **Usuários podem ver apenas suas próprias atividades**
- **IPs são registrados para rastreabilidade**

---

## 📝 BOAS PRÁTICAS

1. **Use decorators sempre que possível** - São mais simples e menos propensos a erros
2. **Registre visualizações apenas em páginas críticas** - Evite poluir logs
3. **Para operações em lote, use registro manual** - Mais controle
4. **Revise logs regularmente** - Identifique padrões suspeitos
5. **Não remova logs** - São importantes para compliance e auditoria

---

## 🎯 PRÓXIMOS PASSOS

Para aplicar auditoria em todas as rotas existentes:

1. Abra cada arquivo em `routes/`
2. Importe os decorators necessários
3. Adicione `@auditar_acao()` nas funções de CRUD
4. Teste cada funcionalidade
5. Verifique os logs em `/auditoria`

**Quer que eu aplique automaticamente em alguma rota específica? É só pedir!**
