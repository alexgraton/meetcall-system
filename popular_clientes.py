"""
Script para popular a tabela de clientes com dados de exemplo.
Execute: python popular_clientes.py
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.cliente import ClienteModel

def popular_clientes():
    """Popula a tabela de clientes com dados de exemplo"""
    
    clientes_exemplo = [
        {
            'tipo_pessoa': 'juridica',
            'nome': 'Tech Solutions Ltda',
            'razao_social': 'Tech Solutions Tecnologia da Informação Ltda',
            'cnpj': '12.345.678/0001-90',
            'inscricao_estadual': '123.456.789.012',
            'logradouro': 'Av. Paulista',
            'numero': '1000',
            'complemento': 'Sala 1501',
            'bairro': 'Bela Vista',
            'cidade': 'São Paulo',
            'uf': 'SP',
            'cep': '01310-100',
            'telefone': '(11) 98765-4321',
            'email': 'contato@techsolutions.com.br',
            'contatos': [
                {
                    'nome': 'Carlos Santos',
                    'telefone': '(11) 98765-1111',
                    'email': 'carlos.santos@techsolutions.com.br',
                    'cargo': 'Gerente Comercial',
                    'observacoes': 'Responsável por novos projetos'
                },
                {
                    'nome': 'Maria Oliveira',
                    'telefone': '(11) 98765-2222',
                    'email': 'maria.oliveira@techsolutions.com.br',
                    'cargo': 'Coordenadora de TI',
                    'observacoes': 'Contato técnico principal'
                }
            ],
            'produtos': [
                {
                    'nome': 'Sistema de Gestão Empresarial',
                    'descricao': 'ERP completo para gestão empresarial',
                    'valor': 15000.00
                },
                {
                    'nome': 'Consultoria em TI',
                    'descricao': 'Horas de consultoria especializada',
                    'valor': 250.00
                }
            ]
        },
        {
            'tipo_pessoa': 'juridica',
            'nome': 'Construtora ABC',
            'razao_social': 'ABC Construções e Empreendimentos S.A.',
            'cnpj': '23.456.789/0001-01',
            'inscricao_estadual': '234.567.890.123',
            'logradouro': 'Rua das Obras',
            'numero': '500',
            'bairro': 'Centro',
            'cidade': 'Campinas',
            'uf': 'SP',
            'cep': '13010-000',
            'telefone': '(19) 3333-4444',
            'email': 'contato@construtorabc.com.br',
            'contatos': [
                {
                    'nome': 'João Silva',
                    'telefone': '(19) 99999-8888',
                    'email': 'joao.silva@construtorabc.com.br',
                    'cargo': 'Engenheiro Civil',
                    'observacoes': 'Aprovação de projetos'
                }
            ],
            'produtos': [
                {
                    'nome': 'Projeto Arquitetônico',
                    'descricao': 'Projetos arquitetônicos personalizados',
                    'valor': 8000.00
                },
                {
                    'nome': 'Construção Residencial',
                    'descricao': 'Construção de casas e apartamentos',
                    'valor': 350000.00
                }
            ]
        },
        {
            'tipo_pessoa': 'fisica',
            'nome': 'Ana Maria Costa',
            'cnpj': '123.456.789-00',
            'logradouro': 'Rua das Flores',
            'numero': '123',
            'bairro': 'Jardim Primavera',
            'cidade': 'São Paulo',
            'uf': 'SP',
            'cep': '04567-890',
            'telefone': '(11) 91234-5678',
            'email': 'ana.costa@email.com',
            'contatos': [],
            'produtos': [
                {
                    'nome': 'Consultoria Financeira Pessoal',
                    'descricao': 'Planejamento financeiro individual',
                    'valor': 500.00
                }
            ]
        },
        {
            'tipo_pessoa': 'juridica',
            'nome': 'MegaStore Comércio',
            'razao_social': 'MegaStore Comércio de Eletrônicos Ltda',
            'cnpj': '34.567.890/0001-12',
            'inscricao_estadual': '345.678.901.234',
            'logradouro': 'Av. do Comércio',
            'numero': '2000',
            'complemento': 'Loja 15',
            'bairro': 'Shopping Center',
            'cidade': 'Guarulhos',
            'uf': 'SP',
            'cep': '07110-000',
            'telefone': '(11) 2222-3333',
            'email': 'vendas@megastore.com.br',
            'contatos': [
                {
                    'nome': 'Pedro Almeida',
                    'telefone': '(11) 98888-7777',
                    'email': 'pedro.almeida@megastore.com.br',
                    'cargo': 'Gerente de Compras',
                    'observacoes': 'Autorização de orçamentos'
                },
                {
                    'nome': 'Juliana Ferreira',
                    'telefone': '(11) 98888-6666',
                    'email': 'juliana.ferreira@megastore.com.br',
                    'cargo': 'Supervisora de Vendas',
                    'observacoes': 'Relacionamento comercial'
                }
            ],
            'produtos': [
                {
                    'nome': 'Notebooks',
                    'descricao': 'Linha completa de notebooks',
                    'valor': 3500.00
                },
                {
                    'nome': 'Smartphones',
                    'descricao': 'Smartphones de última geração',
                    'valor': 2500.00
                },
                {
                    'nome': 'Tablets',
                    'descricao': 'Tablets para uso pessoal e corporativo',
                    'valor': 1500.00
                }
            ]
        },
        {
            'tipo_pessoa': 'fisica',
            'nome': 'Roberto Mendes',
            'cnpj': '987.654.321-00',
            'logradouro': 'Rua dos Professores',
            'numero': '456',
            'complemento': 'Apto 302',
            'bairro': 'Vila Universitária',
            'cidade': 'Sorocaba',
            'uf': 'SP',
            'cep': '18040-000',
            'telefone': '(15) 99876-5432',
            'email': 'roberto.mendes@email.com',
            'contatos': [
                {
                    'nome': 'Patricia Mendes',
                    'telefone': '(15) 99876-5433',
                    'email': 'patricia.mendes@email.com',
                    'cargo': 'Sócia',
                    'observacoes': 'Contato alternativo'
                }
            ],
            'produtos': [
                {
                    'nome': 'Treinamento Corporativo',
                    'descricao': 'Treinamentos personalizados para empresas',
                    'valor': 1200.00
                },
                {
                    'nome': 'Palestras Motivacionais',
                    'descricao': 'Palestras sobre liderança e desenvolvimento',
                    'valor': 800.00
                }
            ]
        }
    ]
    
    print("Populando tabela de clientes...")
    print("-" * 80)
    
    for cliente_data in clientes_exemplo:
        try:
            result = ClienteModel.create(cliente_data)
            if result['success']:
                print(f"✓ Cliente cadastrado: {cliente_data['nome']} (Código: {result['codigo']})")
                print(f"  - Contatos: {len(cliente_data['contatos'])}")
                print(f"  - Produtos: {len(cliente_data['produtos'])}")
            else:
                print(f"✗ Erro ao cadastrar {cliente_data['nome']}: {result['message']}")
        except Exception as e:
            print(f"✗ Exceção ao cadastrar {cliente_data['nome']}: {str(e)}")
        print()
    
    print("-" * 80)
    print("Processo de população concluído!")
    
    # Listar todos os clientes cadastrados
    print("\nClientes cadastrados no sistema:")
    print("-" * 80)
    clientes = ClienteModel.get_all()
    for cliente in clientes:
        print(f"Código: {cliente['codigo']} | {cliente['nome']} | {cliente['cnpj']} | Produtos: {cliente['produtos_count']}")
    
    print("-" * 80)
    print(f"Total: {len(clientes)} clientes")

if __name__ == '__main__':
    popular_clientes()
