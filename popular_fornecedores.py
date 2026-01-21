"""
Script para popular Fornecedores com dados de exemplo
"""
from models.fornecedor import FornecedorModel

def popular_fornecedores():
    print("🔧 Populando Fornecedores...")
    
    fornecedores = [
        {
            'nome': 'Tech Solutions Ltda',
            'razao_social': 'Tech Solutions Tecnologia da Informação Ltda',
            'cnpj': '12.345.678/0001-90',
            'tipo_pessoa': 'juridica',
            'email': 'contato@techsolutions.com.br',
            'telefone': '(11) 3456-7890',
            'cep': '01310-100',
            'endereco': 'Av. Paulista',
            'numero': '1578',
            'bairro': 'Bela Vista',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'contatos': [
                {'nome': 'João Silva', 'cargo': 'Gerente Comercial', 'telefone': '(11) 98765-4321', 'email': 'joao@techsolutions.com.br'},
                {'nome': 'Maria Santos', 'cargo': 'Coordenadora de TI', 'telefone': '(11) 98765-4322', 'email': 'maria@techsolutions.com.br'}
            ]
        },
        {
            'nome': 'Distribuidora ABC',
            'razao_social': 'ABC Distribuidora de Materiais Ltda',
            'cnpj': '98.765.432/0001-10',
            'tipo_pessoa': 'juridica',
            'email': 'vendas@distribuidoraabc.com.br',
            'telefone': '(21) 2345-6789',
            'cep': '20040-020',
            'endereco': 'Av. Rio Branco',
            'numero': '156',
            'bairro': 'Centro',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
            'contatos': [
                {'nome': 'Pedro Costa', 'cargo': 'Representante de Vendas', 'telefone': '(21) 99876-5432', 'email': 'pedro@distribuidoraabc.com.br'}
            ]
        },
        {
            'nome': 'Consultoria XYZ',
            'razao_social': 'XYZ Consultoria Empresarial S.A.',
            'cnpj': '11.222.333/0001-44',
            'tipo_pessoa': 'juridica',
            'email': 'info@consultoriaxyz.com',
            'telefone': '(31) 3210-9876',
            'cep': '30130-100',
            'endereco': 'Rua da Bahia',
            'numero': '1234',
            'bairro': 'Centro',
            'cidade': 'Belo Horizonte',
            'estado': 'MG',
            'contatos': [
                {'nome': 'Ana Paula', 'cargo': 'Diretora', 'telefone': '(31) 99123-4567', 'email': 'ana@consultoriaxyz.com'},
                {'nome': 'Carlos Mendes', 'cargo': 'Consultor Sênior', 'telefone': '(31) 99123-4568', 'email': 'carlos@consultoriaxyz.com'}
            ]
        },
        {
            'nome': 'José da Silva',
            'razao_social': None,
            'cnpj': '123.456.789-00',
            'tipo_pessoa': 'fisica',
            'email': 'jose.silva@email.com',
            'telefone': '(41) 98765-4321',
            'cep': '80010-000',
            'endereco': 'Rua XV de Novembro',
            'numero': '500',
            'bairro': 'Centro',
            'cidade': 'Curitiba',
            'estado': 'PR',
            'contatos': []
        },
        {
            'nome': 'Gráfica Impressão Total',
            'razao_social': 'Impressão Total Serviços Gráficos Ltda',
            'cnpj': '55.666.777/0001-88',
            'tipo_pessoa': 'juridica',
            'email': 'orcamento@impressaototal.com.br',
            'telefone': '(48) 3333-4444',
            'cep': '88010-400',
            'endereco': 'Rua Felipe Schmidt',
            'numero': '789',
            'bairro': 'Centro',
            'cidade': 'Florianópolis',
            'estado': 'SC',
            'contatos': [
                {'nome': 'Roberto Oliveira', 'cargo': 'Orçamentista', 'telefone': '(48) 99999-8888', 'email': 'roberto@impressaototal.com.br'}
            ]
        }
    ]
    
    try:
        for f in fornecedores:
            fornecedor_id = FornecedorModel.create(f)
            print(f"✅ Fornecedor criado: {f['nome']} (ID: {fornecedor_id})")
            if f.get('contatos'):
                print(f"   ↳ {len(f['contatos'])} contato(s) adicionado(s)")
        
        print(f"\n🎉 Fornecedores populados com sucesso!")
        print(f"📊 Total: {len(fornecedores)} fornecedores cadastrados")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular dados: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    popular_fornecedores()
