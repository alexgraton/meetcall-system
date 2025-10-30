"""Script para verificar se há sobreposição entre clientes e fornecedores"""
from models.fornecedor import FornecedorModel
from models.cliente import ClienteModel

fornecedores = FornecedorModel.get_all()
clientes = ClienteModel.get_all()

print("=" * 60)
print("FORNECEDORES")
print("=" * 60)
for f in fornecedores:
    print(f"ID: {f['id']:3} | Nome: {f.get('nome', 'N/A'):30} | Razão: {f.get('razao_social', 'N/A')}")

print("\n" + "=" * 60)
print("CLIENTES")
print("=" * 60)
for c in clientes:
    print(f"ID: {c['id']:3} | Nome: {c.get('nome', 'N/A'):30} | Razão: {c.get('razao_social', 'N/A')}")

print("\n" + "=" * 60)
print("ANÁLISE")
print("=" * 60)

# Verificar CNPJs/CPFs duplicados
fornecedor_docs = {f.get('cnpj'): f.get('nome', f.get('razao_social')) for f in fornecedores if f.get('cnpj')}
cliente_docs = {c.get('cnpj'): c.get('nome', c.get('razao_social')) for c in clientes if c.get('cnpj')}

duplicados = set(fornecedor_docs.keys()).intersection(set(cliente_docs.keys()))

if duplicados:
    print(f"\n⚠️  CNPJ/CPF duplicados entre fornecedores e clientes:")
    for doc in duplicados:
        print(f"  {doc}: Fornecedor '{fornecedor_docs[doc]}' / Cliente '{cliente_docs[doc]}'")
else:
    print("\n✅ Não há CNPJ/CPF duplicados entre fornecedores e clientes")

# Verificar nomes com None em razao_social
print("\n" + "=" * 60)
print("FORNECEDORES COM RAZÃO SOCIAL VAZIA (podem ser pessoas físicas):")
for f in fornecedores:
    if not f.get('razao_social'):
        print(f"  ID {f['id']}: {f.get('nome')} - Tipo: {f.get('tipo_pessoa', 'N/A')}")
