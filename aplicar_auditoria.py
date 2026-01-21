"""
Script para aplicar auditoria automaticamente em todas as rotas do sistema
"""
import os
import re

# Mapeamento de arquivos e suas tabelas
ROTAS_TABELAS = {
    'fornecedores.py': {
        'tabela': 'fornecedores',
        'funcoes': {
            'def novo()': ('insert', 'fornecedor_id'),
            'def editar(fornecedor_id)': ('update', 'fornecedor_id'),
            'def deletar(fornecedor_id)': ('delete', 'fornecedor_id'),
        }
    },
    'clientes.py': {
        'tabela': 'clientes',
        'funcoes': {
            'def novo()': ('insert', 'cliente_id'),
            'def editar(cliente_id)': ('update', 'cliente_id'),
            'def deletar(cliente_id)': ('delete', 'cliente_id'),
        }
    },
    'filiais.py': {
        'tabela': 'filiais',
        'funcoes': {
            'def nova()': ('insert', 'filial_id'),
            'def editar(filial_id)': ('update', 'filial_id'),
            'def deletar(filial_id)': ('delete', 'filial_id'),
        }
    },
    'contas_bancarias.py': {
        'tabela': 'contas_bancarias',
        'funcoes': {
            'def nova()': ('insert', 'conta_id'),
            'def editar(conta_id)': ('update', 'conta_id'),
            'def excluir(conta_id)': ('delete', 'conta_id'),
            'def ajustar_saldo(conta_id)': ('update', 'conta_id'),
        }
    },
    'centro_custos.py': {
        'tabela': 'centro_custos',
        'funcoes': {
            'def novo()': ('insert', 'centro_custo_id'),
            'def editar(centro_custo_id)': ('update', 'centro_custo_id'),
            'def deletar(centro_custo_id)': ('delete', 'centro_custo_id'),
        }
    },
    'plano_contas.py': {
        'tabela': 'plano_contas',
        'funcoes': {
            'def novo()': ('insert', 'conta_id'),
            'def editar(conta_id)': ('update', 'conta_id'),
            'def deletar(conta_id)': ('delete', 'conta_id'),
        }
    },
    'tipos_servicos.py': {
        'tabela': 'tipos_servicos',
        'funcoes': {
            'def novo()': ('insert', 'tipo_id'),
            'def novo_subtipo(categoria_id)': ('insert', 'tipo_id'),
            'def editar(tipo_id)': ('update', 'tipo_id'),
            'def deletar(tipo_id)': ('delete', 'tipo_id'),
        }
    },
    'lancamentos.py': {
        'tabela': 'lancamentos_manuais',
        'funcoes': {
            'def novo()': ('insert', 'lancamento_id'),
            'def editar(lancamento_id)': ('update', 'lancamento_id'),
            'def excluir(lancamento_id)': ('delete', 'lancamento_id'),
        }
    },
    'contas_pagar.py': {
        'tabela': 'contas_pagar',
        'funcoes': {
            'def criar_conta()': ('insert', 'conta_id'),
            'def baixar_conta(conta_id)': ('update', 'conta_id'),
            'def cancelar_conta(conta_id)': ('update', 'conta_id'),
        }
    },
    'contas_receber.py': {
        'tabela': 'contas_receber',
        'funcoes': {
            'def criar_conta()': ('insert', 'conta_id'),
            'def receber_conta(conta_id)': ('update', 'conta_id'),
            'def cancelar_conta(conta_id)': ('update', 'conta_id'),
        }
    },
    'conciliacao.py': {
        'tabela': 'conciliacao_bancaria',
        'funcoes': {
            'def conciliar()': ('insert', None),
            'def desconciliar()': ('delete', None),
        }
    },
    'margem.py': {
        'tabela': 'margem_operacional',
        'funcoes': {
            'def criar_competencia()': ('insert', 'competencia_id'),
            'def fechar_competencia(competencia_id)': ('update', 'competencia_id'),
            'def reabrir_competencia(competencia_id)': ('update', 'competencia_id'),
        }
    },
}

def adicionar_import(conteudo):
    """Adiciona import da auditoria se não existir"""
    if 'from utils.auditoria import auditar_agora' in conteudo:
        return conteudo
    
    # Encontrar a última linha de import
    linhas = conteudo.split('\n')
    ultima_import = 0
    
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('from ') or linha.strip().startswith('import '):
            ultima_import = i
    
    # Inserir o import
    linhas.insert(ultima_import + 1, 'from utils.auditoria import auditar_agora')
    return '\n'.join(linhas)

def gerar_codigo_auditoria(tabela, acao, var_id):
    """Gera o código de auditoria"""
    if var_id:
        return f"""
        # Auditoria
        auditar_agora('{tabela}', {var_id}, '{acao}', request.form.to_dict() if request.method == 'POST' else None)
        """
    else:
        return f"""
        # Auditoria
        auditar_agora('{tabela}', 0, '{acao}', request.get_json() if request.is_json else request.form.to_dict())
        """

def processar_arquivo(arquivo_path, config):
    """Processa um arquivo de rota"""
    print(f"\n📝 Processando: {os.path.basename(arquivo_path)}")
    
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Adicionar import
    conteudo_novo = adicionar_import(conteudo)
    
    # Verificar se já tem auditoria
    if conteudo_novo != conteudo:
        print(f"  ✓ Import adicionado")
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
    else:
        print(f"  ℹ Import já existe")

def main():
    print("=" * 60)
    print("🔧 APLICADOR AUTOMÁTICO DE AUDITORIA")
    print("=" * 60)
    
    routes_dir = 'routes'
    arquivos_processados = 0
    
    for arquivo, config in ROTAS_TABELAS.items():
        arquivo_path = os.path.join(routes_dir, arquivo)
        
        if os.path.exists(arquivo_path):
            processar_arquivo(arquivo_path, config)
            arquivos_processados += 1
        else:
            print(f"\n⚠️  Arquivo não encontrado: {arquivo}")
    
    print("\n" + "=" * 60)
    print(f"✅ Concluído! {arquivos_processados} arquivos processados")
    print("=" * 60)
    print("\n📌 PRÓXIMO PASSO:")
    print("   Adicione manualmente as chamadas auditar_agora() após cada operação")
    print("   Exemplo: auditar_agora('fornecedores', fornecedor_id, 'insert')")
    print("\n")

if __name__ == '__main__':
    main()
