"""
Script para popular a tabela de centros de custo com dados de exemplo.
Execute: python popular_centro_custos.py
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.centro_custo import CentroCustoModel
from models.filial import FilialModel

def popular_centro_custos():
    """Popula a tabela de centros de custo com dados de exemplo"""
    
    # Buscar filiais existentes
    filiais = FilialModel.get_all()
    if not filiais:
        print("AVISO: Nenhuma filial encontrada. Execute popular_filiais.py primeiro.")
        return
    
    # Pegar primeira filial como exemplo
    filial_sp = next((f for f in filiais if 'SP' in f.get('uf', '')), filiais[0])
    
    centros_exemplo = [
        # Centros Gerais (sem filial específica)
        {
            'descricao': 'Administrativo',
            'filial_id': None,
            'parent_id': None
        },
        {
            'descricao': 'Recursos Humanos',
            'filial_id': None,
            'parent_id': None
        },
        {
            'descricao': 'Tecnologia da Informação',
            'filial_id': None,
            'parent_id': None
        },
        {
            'descricao': 'Marketing',
            'filial_id': None,
            'parent_id': None
        },
        {
            'descricao': 'Financeiro',
            'filial_id': None,
            'parent_id': None
        },
        # Centros por Filial
        {
            'descricao': 'Vendas',
            'filial_id': filial_sp['id'],
            'parent_id': None
        },
        {
            'descricao': 'Operações',
            'filial_id': filial_sp['id'],
            'parent_id': None
        },
        {
            'descricao': 'Atendimento ao Cliente',
            'filial_id': filial_sp['id'],
            'parent_id': None
        }
    ]
    
    print("Populando tabela de centros de custo...")
    print("-" * 80)
    
    centros_criados = []
    
    for centro_data in centros_exemplo:
        try:
            result = CentroCustoModel.create(centro_data)
            if result['success']:
                tipo = "Geral" if not centro_data['filial_id'] else f"Filial {filial_sp['nome']}"
                print(f"✓ Centro de custo cadastrado: {result['codigo']} - {centro_data['descricao']} ({tipo})")
                centros_criados.append({'id': result['id'], 'codigo': result['codigo'], 'descricao': centro_data['descricao']})
            else:
                print(f"✗ Erro ao cadastrar {centro_data['descricao']}: {result['message']}")
        except Exception as e:
            print(f"✗ Exceção ao cadastrar {centro_data['descricao']}: {str(e)}")
    
    # Criar alguns centros filhos (hierarquia)
    if centros_criados:
        # Encontrar centro "Marketing"
        marketing = next((c for c in centros_criados if c['descricao'] == 'Marketing'), None)
        if marketing:
            print("\nCriando centros de custo filhos (hierarquia)...")
            print("-" * 80)
            
            filhos = [
                {
                    'descricao': 'Marketing Digital',
                    'filial_id': None,
                    'parent_id': marketing['id']
                },
                {
                    'descricao': 'Marketing Tradicional',
                    'filial_id': None,
                    'parent_id': marketing['id']
                }
            ]
            
            for filho_data in filhos:
                try:
                    result = CentroCustoModel.create(filho_data)
                    if result['success']:
                        print(f"✓ Subcentro criado: {result['codigo']} - {filho_data['descricao']} (filho de {marketing['codigo']})")
                    else:
                        print(f"✗ Erro ao criar subcentro: {result['message']}")
                except Exception as e:
                    print(f"✗ Exceção ao criar subcentro: {str(e)}")
    
    print("\n" + "-" * 80)
    print("Processo de população concluído!")
    
    # Listar todos os centros cadastrados
    print("\nCentros de Custo cadastrados no sistema:")
    print("-" * 80)
    centros = CentroCustoModel.get_all()
    for centro in centros:
        filial_info = f" - Filial: {centro['filial_nome']}" if centro.get('filial_nome') else " - Geral"
        parent_info = f" (filho de: {centro['parent_descricao']})" if centro.get('parent_descricao') else ""
        print(f"{centro['codigo']} | {centro['descricao']}{filial_info}{parent_info}")
    
    print("-" * 80)
    print(f"Total: {len(centros)} centros de custo")

if __name__ == '__main__':
    popular_centro_custos()
