"""
Script automatizado para adicionar auditar_agora() em todas as operações CRUD
"""

# Lista de padrões e suas substituições
PATTERNS = {
    # Fornecedores
    'fornecedores.py': [
        {
            'find': "        FornecedorModel.update(fornecedor_id, dados)\n        flash('Fornecedor atualizado com sucesso!', 'success')",
            'replace': "        FornecedorModel.update(fornecedor_id, dados)\n        \n        # Auditoria\n        auditar_agora('fornecedores', fornecedor_id, 'update', dados)\n        \n        flash('Fornecedor atualizado com sucesso!', 'success')"
        },
        {
            'find': "        FornecedorModel.delete(fornecedor_id)\n        flash('Fornecedor excluído com sucesso!', 'success')",
            'replace': "        FornecedorModel.delete(fornecedor_id)\n        \n        # Auditoria\n        auditar_agora('fornecedores', fornecedor_id, 'delete')\n        \n        flash('Fornecedor excluído com sucesso!', 'success')"
        }
    ],
    
    # Clientes
    'clientes.py': [
        {
            'find': "        cliente_id = ClienteModel.create(dados)\n        flash('Cliente criado com sucesso!', 'success')",
            'replace': "        cliente_id = ClienteModel.create(dados)\n        \n        # Auditoria\n        auditar_agora('clientes', cliente_id, 'insert', dados)\n        \n        flash('Cliente criado com sucesso!', 'success')"
        },
        {
            'find': "        ClienteModel.update(cliente_id, dados)\n        flash('Cliente atualizado com sucesso!', 'success')",
            'replace': "        ClienteModel.update(cliente_id, dados)\n        \n        # Auditoria\n        auditar_agora('clientes', cliente_id, 'update', dados)\n        \n        flash('Cliente atualizado com sucesso!', 'success')"
        },
        {
            'find': "        ClienteModel.delete(cliente_id)\n        flash('Cliente excluído com sucesso!', 'success')",
            'replace': "        ClienteModel.delete(cliente_id)\n        \n        # Auditoria\n        auditar_agora('clientes', cliente_id, 'delete')\n        \n        flash('Cliente excluído com sucesso!', 'success')"
        }
    ],
    
    # Filiais  
    'filiais.py': [
        {
            'find': "            filial_id = FilialModel.create(dados)\n            flash('Filial criada com sucesso!', 'success')",
            'replace': "            filial_id = FilialModel.create(dados)\n            \n            # Auditoria\n            auditar_agora('filiais', filial_id, 'insert', dados)\n            \n            flash('Filial criada com sucesso!', 'success')"
        },
        {
            'find': "            FilialModel.update(filial_id, dados)\n            flash('Filial atualizada com sucesso!', 'success')",
            'replace': "            FilialModel.update(filial_id, dados)\n            \n            # Auditoria\n            auditar_agora('filiais', filial_id, 'update', dados)\n            \n            flash('Filial atualizada com sucesso!', 'success')"
        },
        {
            'find': "        FilialModel.delete(filial_id)\n        flash('Filial excluída com sucesso!', 'success')",
            'replace': "        FilialModel.delete(filial_id)\n        \n        # Auditoria\n        auditar_agora('filiais', filial_id, 'delete')\n        \n        flash('Filial excluída com sucesso!', 'success')"
        }
    ],
    
    # Centro de Custos
    'centro_custos.py': [
        {
            'find': "        centro_custo_id = CentroCustoModel.create(dados)\n        flash('Centro de custo criado com sucesso!', 'success')",
            'replace': "        centro_custo_id = CentroCustoModel.create(dados)\n        \n        # Auditoria\n        auditar_agora('centro_custos', centro_custo_id, 'insert', dados)\n        \n        flash('Centro de custo criado com sucesso!', 'success')"
        },
        {
            'find': "        CentroCustoModel.update(centro_custo_id, dados)\n        flash('Centro de custo atualizado com sucesso!', 'success')",
            'replace': "        CentroCustoModel.update(centro_custo_id, dados)\n        \n        # Auditoria\n        auditar_agora('centro_custos', centro_custo_id, 'update', dados)\n        \n        flash('Centro de custo atualizado com sucesso!', 'success')"
        },
        {
            'find': "        CentroCustoModel.delete(centro_custo_id)\n        flash('Centro de custo excluído com sucesso!', 'success')",
            'replace': "        CentroCustoModel.delete(centro_custo_id)\n        \n        # Auditoria\n        auditar_agora('centro_custos', centro_custo_id, 'delete')\n        \n        flash('Centro de custo excluído com sucesso!', 'success')"
        }
    ],
    
    # Plano de Contas
    'plano_contas.py': [
        {
            'find': "        conta_id = PlanoContaModel.create(dados)\n        flash('Conta criada com sucesso!', 'success')",
            'replace': "        conta_id = PlanoContaModel.create(dados)\n        \n        # Auditoria\n        auditar_agora('plano_contas', conta_id, 'insert', dados)\n        \n        flash('Conta criada com sucesso!', 'success')"
        },
        {
            'find': "        PlanoContaModel.update(conta_id, dados)\n        flash('Conta atualizada com sucesso!', 'success')",
            'replace': "        PlanoContaModel.update(conta_id, dados)\n        \n        # Auditoria\n        auditar_agora('plano_contas', conta_id, 'update', dados)\n        \n        flash('Conta atualizada com sucesso!', 'success')"
        },
        {
            'find': "        PlanoContaModel.delete(conta_id)\n        flash('Conta excluída com sucesso!', 'success')",
            'replace': "        PlanoContaModel.delete(conta_id)\n        \n        # Auditoria\n        auditar_agora('plano_contas', conta_id, 'delete')\n        \n        flash('Conta excluída com sucesso!', 'success')"
        }
    ],
}

import os

def aplicar_patterns(arquivo, patterns):
    filepath = os.path.join('routes', arquivo)
    
    if not os.path.exists(filepath):
        print(f"⚠️  Arquivo não encontrado: {arquivo}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    modificacoes = 0
    
    for pattern in patterns:
        if pattern['find'] in content:
            content = content.replace(pattern['find'], pattern['replace'])
            modificacoes += 1
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {arquivo}: {modificacoes} modificações aplicadas")
        return True
    else:
        print(f"ℹ️  {arquivo}: Nenhuma modificação necessária")
        return False

def main():
    print("\n" + "=" * 70)
    print("🔧 APLICANDO AUDITORIA AUTOMATICAMENTE EM TODAS AS ROTAS")
    print("=" * 70 + "\n")
    
    total_modificados = 0
    
    for arquivo, patterns in PATTERNS.items():
        if aplicar_patterns(arquivo, patterns):
            total_modificados += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Concluído! {total_modificados} arquivos modificados")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
