"""
Script para popular Tipos de Serviços com dados de exemplo
Execute este script para criar categorias e subcategorias de exemplo
"""
from models.tipo_servico import TipoServicoModel

def popular_tipos_servicos():
    """Cria tipos de serviços de exemplo"""
    
    print("🔧 Populando Tipos de Serviços...")
    
    # Categorias principais
    categorias = [
        {
            'nome': 'Consultoria',
            'descricao': 'Serviços de consultoria empresarial',
            'aliquota': 15.0,
            'margem_esperada': 40.0,
            'subcategorias': [
                {'nome': 'Consultoria Tributária', 'aliquota': 15.0, 'margem_esperada': 45.0},
                {'nome': 'Consultoria Contábil', 'aliquota': 15.0, 'margem_esperada': 40.0},
                {'nome': 'Consultoria Financeira', 'aliquota': 15.0, 'margem_esperada': 50.0},
            ]
        },
        {
            'nome': 'Tecnologia',
            'descricao': 'Serviços de tecnologia da informação',
            'aliquota': 10.5,
            'margem_esperada': 35.0,
            'subcategorias': [
                {'nome': 'Desenvolvimento de Software', 'aliquota': 10.5, 'margem_esperada': 40.0},
                {'nome': 'Suporte Técnico', 'aliquota': 10.5, 'margem_esperada': 30.0},
                {'nome': 'Infraestrutura de TI', 'aliquota': 10.5, 'margem_esperada': 35.0},
            ]
        },
        {
            'nome': 'Marketing',
            'descricao': 'Serviços de marketing e publicidade',
            'aliquota': 14.0,
            'margem_esperada': 38.0,
            'subcategorias': [
                {'nome': 'Marketing Digital', 'aliquota': 14.0, 'margem_esperada': 42.0},
                {'nome': 'Gestão de Redes Sociais', 'aliquota': 14.0, 'margem_esperada': 40.0},
                {'nome': 'Criação de Conteúdo', 'aliquota': 14.0, 'margem_esperada': 35.0},
            ]
        },
        {
            'nome': 'Treinamento',
            'descricao': 'Cursos e treinamentos corporativos',
            'aliquota': 12.0,
            'margem_esperada': 45.0,
            'subcategorias': [
                {'nome': 'Treinamento Presencial', 'aliquota': 12.0, 'margem_esperada': 48.0},
                {'nome': 'Treinamento Online', 'aliquota': 12.0, 'margem_esperada': 50.0},
                {'nome': 'Workshop', 'aliquota': 12.0, 'margem_esperada': 42.0},
            ]
        },
        {
            'nome': 'Assessoria',
            'descricao': 'Serviços de assessoria especializada',
            'aliquota': 13.0,
            'margem_esperada': 36.0,
            'subcategorias': [
                {'nome': 'Assessoria Jurídica', 'aliquota': 13.0, 'margem_esperada': 40.0},
                {'nome': 'Assessoria de Imprensa', 'aliquota': 13.0, 'margem_esperada': 35.0},
                {'nome': 'Assessoria Administrativa', 'aliquota': 13.0, 'margem_esperada': 33.0},
            ]
        }
    ]
    
    try:
        for cat in categorias:
            # Criar categoria principal
            cat_id = TipoServicoModel.create(
                nome=cat['nome'],
                descricao=cat.get('descricao'),
                tipo='despesa',  # Tipo padrão
                aliquota=cat['aliquota'],
                margem_esperada=cat['margem_esperada']
            )
            print(f"✅ Categoria criada: {cat['nome']}")
            
            # Criar subcategorias
            for sub in cat.get('subcategorias', []):
                TipoServicoModel.create(
                    nome=sub['nome'],
                    tipo='despesa',
                    parent_id=cat_id,
                    aliquota=sub['aliquota'],
                    margem_esperada=sub['margem_esperada']
                )
                print(f"   ↳ Subcategoria criada: {sub['nome']}")
        
        print("\n🎉 Tipos de Serviços populados com sucesso!")
        print(f"📊 Total: {len(categorias)} categorias com subcategorias")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular dados: {str(e)}")

if __name__ == '__main__':
    popular_tipos_servicos()
