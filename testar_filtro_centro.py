from app import app
from models.centro_custo import CentroCustoModel
from models.filial import FilialModel

with app.app_context():
    print("=== Testando Filtro de Centro de Custos ===\n")
    
    # Listar filiais
    filiais = FilialModel.get_all()
    print("Filiais disponíveis:")
    for f in filiais:
        print(f"  ID: {f['id']} - {f['nome']}")
    
    print("\n=== Centros SEM filtro (todos) ===")
    centros_todos = CentroCustoModel.get_all()
    for c in centros_todos:
        filial_info = c.get('filial_nome', 'GERAL')
        print(f"  {c['codigo']} - {c['descricao']} (Filial: {filial_info})")
    print(f"Total: {len(centros_todos)} centros")
    
    if filiais:
        filial_teste = filiais[0]['id']
        print(f"\n=== Centros COM filtro (Filial ID: {filial_teste}) ===")
        centros_filtrados = CentroCustoModel.get_all(filial_id=filial_teste)
        for c in centros_filtrados:
            filial_info = c.get('filial_nome', 'GERAL')
            print(f"  {c['codigo']} - {c['descricao']} (Filial: {filial_info})")
        print(f"Total: {len(centros_filtrados)} centros")
