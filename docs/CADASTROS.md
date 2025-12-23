# 📋 Manual de Cadastros - MeetCall System
## Call Center de Cobrança

## 🎯 Sobre a Meet Call

A **Meet Call** é um call center especializado em **cobrança de dívidas** para empresas como:
- 🏦 Bancos e Financeiras
- 🏫 Escolas e Universidades  
- 📞 Empresas de Telefonia
- 🏢 Outros segmentos

### Modelo de Negócio

**Receita:** Comissão sobre valores recuperados  
**Despesas:** Operação do call center (pessoas, telefonia, tecnologia, etc)

**Exemplo:**
- Recuperou R$ 100.000 em dívidas
- Comissão de 15%
- **Receita:** R$ 15.000

---

## 📊 Categorias de Despesas

### O que são?

São **categorias** para organizar as despesas operacionais do call center de forma hierárquica.

### Estrutura Hierárquica

**Categoria Principal** (Grupo)  
└── Subcategoria 1  
└── Subcategoria 2  
└── Subcategoria 3  

**Exemplo:**

**Tecnologia** (Categoria Principal)  
├── Software CRM  
├── Telefonia IP  
├── Infraestrutura TI  
└── Licenças de Software  

---

## 📝 Campos Explicados

### 1. **Nome da Categoria** (obrigatório)
Nome da categoria de despesa

**Exemplos de Categorias Principais:**
- Recursos Humanos
- Telefonia
- Tecnologia
- Marketing
- Administrativo
- Infraestrutura

**Exemplos de Subcategorias:**
- Salários (dentro de Recursos Humanos)
- Ligações (dentro de Telefonia)
- CRM (dentro de Tecnologia)
- Redes Sociais (dentro de Marketing)

### 2. **Grupo (Categoria Pai)**
Selecione uma categoria principal para criar uma subcategoria

**Quando usar:**
- **Deixe em branco**: Para criar uma categoria principal
- **Selecione um grupo**: Para criar uma subcategoria

**Exemplo prático:**
```
Categoria: "Software CRM"
Grupo: "Tecnologia"
Resultado: CRM fica dentro de Tecnologia
```

### 3. **Descrição**
Detalhes sobre a categoria

**Exemplos:**
- "Despesas com salários, benefícios e encargos da equipe"
- "Custos de telefonia fixa e móvel para operação"
- "Licenças e assinaturas de software"

### 4. **Tipo**
Indica se é Despesa ou Receita

- **Despesa**: Padrão (gastos operacionais)
- **Receita**: Comissões e outros recebíveis

---

## 🏢 Exemplos Práticos para Call Center

### Estrutura Sugerida

#### 1. **Recursos Humanos**
├── Salários Operadores  
├── Salários Supervisores  
├── Salários Administrativo  
├── Benefícios (VT, VR, VA)  
├── Encargos Trabalhistas  
└── Treinamentos  

#### 2. **Telefonia**
├── Telefonia Fixa  
├── Telefonia Móvel  
├── Telefonia IP (VOIP)  
└── Links de Dados  

#### 3. **Tecnologia**
├── Software CRM  
├── Discador Automático  
├── Sistema de Gestão  
├── Infraestrutura TI  
├── Licenças Microsoft  
└── Manutenção de TI  

#### 4. **Marketing**
├── Captação de Clientes  
├── Redes Sociais  
├── Material Publicitário  
└── Eventos e Feiras  

#### 5. **Administrativo**
├── Aluguel  
├── Água e Luz  
├── Internet  
├── Material de Escritório  
├── Limpeza  
└── Segurança  

#### 6. **Infraestrutura**
├── Mobiliário  
├── Equipamentos (computadores, headsets)  
├── Manutenção Predial  
└── Climatização  

---

## 🎯 Como Cadastrar

### Passo 1: Categoria Principal

1. Acesse: **Cadastros → Categorias de Despesas**
2. Clique em **"Nova Categoria"**
3. Preencha:
   - **Nome**: Tecnologia
   - **Grupo**: (deixe em branco)
   - **Descrição**: Despesas com tecnologia e sistemas
   - **Tipo**: Despesa
4. Salve

### Passo 2: Subcategorias

1. Clique em **"Nova Categoria"**
2. Preencha:
   - **Nome**: Software CRM
   - **Grupo**: Tecnologia (selecione)
   - **Descrição**: Licença do CRM para gestão de cobranças
   - **Tipo**: Despesa
3. Salve

Resultado:
```
Tecnologia
└── Software CRM
```

### Repetir para outras subcategorias:
- Discador Automático
- Sistema de Gestão
- Infraestrutura TI
- etc.

---

## 💰 Lançamento de Despesas

Após cadastrar as categorias, você pode lançar despesas reais:

1. Acesse: **Financeiro → Contas a Pagar**
2. Clique em **"Nova Conta a Pagar"**
3. Preencha:
   - **Fornecedor**: Empresa X
   - **Descrição**: Licença CRM Janeiro/2025
   - **Categoria**: Software CRM (subcategoria de Tecnologia)
   - **Valor**: R$ 1.500,00
   - **Vencimento**: 10/01/2025
4. Salve

---

## 📊 Visualizando nos Relatórios

### DRE (Demonstração do Resultado)

O DRE agrupa automaticamente por categorias:

```
RECEITAS
├── Comissões Banco X: R$ 50.000
└── Comissões Escola Y: R$ 30.000
Total: R$ 80.000

DESPESAS
├── Recursos Humanos: R$ 40.000
│   ├── Salários: R$ 35.000
│   └── Benefícios: R$ 5.000
├── Tecnologia: R$ 8.000
│   ├── CRM: R$ 1.500
│   ├── Discador: R$ 3.000
│   └── Infraestrutura: R$ 3.500
└── Telefonia: R$ 12.000
Total: R$ 60.000

LUCRO LÍQUIDO: R$ 20.000
```

### Análise Vertical

Mostra a composição percentual:

```
Despesas por Categoria:
- Recursos Humanos: 50% (R$ 40.000)
- Telefonia: 15% (R$ 12.000)
- Tecnologia: 10% (R$ 8.000)
- Administrativo: 15% (R$ 12.000)
- Marketing: 7,5% (R$ 6.000)
- Infraestrutura: 2,5% (R$ 2.000)
```

---

## ✅ Boas Práticas

### 1. Categorização Clara
- Use nomes descritivos
- Mantenha hierarquia lógica
- Evite categorias muito genéricas

### 2. Consistência
- Sempre use as mesmas categorias
- Não crie duplicatas
- Padronize nomenclatura

### 3. Nível de Detalhamento
- **Principal**: Não muito granular (máximo 8-10)
- **Subcategorias**: Detalhe conforme necessidade

### 4. Revisão Periódica
- Revise categorias trimestralmente
- Ajuste conforme operação evolui
- Desative categorias não utilizadas

---

## ❓ FAQ

### 1. Quantas categorias devo criar?
**Recomendação:** 6-8 categorias principais com 3-5 subcategorias cada.

### 2. Posso ter subcategorias de subcategorias?
**Não.** O sistema suporta apenas 2 níveis (Principal → Subcategoria).

### 3. Posso mudar uma subcategoria de grupo depois?
**Sim.** Edite a subcategoria e altere o "Grupo".

### 4. E se eu cadastrar despesas na categoria errada?
Você pode editar o lançamento e trocar a categoria.

### 5. Preciso cadastrar receitas também?
**Sim**, mas geralmente são poucas categorias:
- Comissões de Cobrança
- Serviços de Consultoria (se aplicável)
- Outras Receitas

### 6. As categorias afetam os relatórios?
**Sim!** O DRE e outros relatórios agrupam por categoria automaticamente.

---

## 📞 Exemplo Real - Operação Mensal

### Despesas Típicas de um Call Center (100 posições)

| Categoria | Subcategoria | Valor Mensal |
|-----------|--------------|--------------|
| **Recursos Humanos** | | **R$ 180.000** |
| | Salários Operadores | R$ 120.000 |
| | Salários Supervisores | R$ 35.000 |
| | Benefícios | R$ 15.000 |
| | Encargos | R$ 10.000 |
| **Telefonia** | | **R$ 25.000** |
| | Telefonia IP | R$ 20.000 |
| | Links Dedicados | R$ 5.000 |
| **Tecnologia** | | **R$ 15.000** |
| | CRM | R$ 5.000 |
| | Discador | R$ 7.000 |
| | Infraestrutura | R$ 3.000 |
| **Administrativo** | | **R$ 20.000** |
| | Aluguel | R$ 12.000 |
| | Energia | R$ 5.000 |
| | Limpeza/Segurança | R$ 3.000 |
| **Marketing** | | **R$ 8.000** |
| **Infraestrutura** | | **R$ 5.000** |
| **TOTAL** | | **R$ 253.000** |

### Receitas Típicas

| Categoria | Cliente | Taxa | Valor Recuperado | Comissão |
|-----------|---------|------|------------------|----------|
| Comissões | Banco X | 15% | R$ 1.000.000 | R$ 150.000 |
| Comissões | Escola Y | 12% | R$ 500.000 | R$ 60.000 |
| Comissões | Telco Z | 18% | R$ 800.000 | R$ 144.000 |
| **TOTAL** | | | **R$ 2.300.000** | **R$ 354.000** |

### Resultado

- **Receita:** R$ 354.000
- **Despesa:** R$ 253.000
- **Lucro:** R$ 101.000
- **Margem:** 28,5%

---

## 📚 Documentação Relacionada

- **Guia de Uso Geral**: `GUIA_DE_USO.md`
- **Sistema de Notificações**: `NOTIFICACOES.md`
- **Relatórios Financeiros**: Acesse no sistema (Financeiro → Relatórios)

---

**MeetCall System** - Gestão Inteligente para Call Centers 📞💼
