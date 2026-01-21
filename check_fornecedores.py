"""Script para verificar fornecedores cadastrados"""
from models.fornecedor import FornecedorModel

fornecedores = FornecedorModel.get_all()
print(f"Total de fornecedores: {len(fornecedores)}\n")

for f in fornecedores:
    print(f"ID: {f['id']}")
    print(f"  Nome: {f.get('nome', 'N/A')}")
    print(f"  Razão Social: {f.get('razao_social', 'N/A')}")
    print(f"  CNPJ: {f.get('cnpj', 'N/A')}")
    print(f"  Ativo: {f.get('is_active', 'N/A')}")
    print("-" * 50)
