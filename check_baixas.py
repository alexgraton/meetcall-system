from models.conta_pagar import ContaPagarModel

baixas = ContaPagarModel.get_baixas()
print(f'Total de pagamentos realizados: {len(baixas)}')

if baixas:
    print('\n=== PAGAMENTOS DISPONÍVEIS PARA ESTORNO ===\n')
    for b in baixas[:5]:
        print(f"ID: {b['id']:3d} | Fornecedor: {b['fornecedor_nome']} | Valor: R$ {b['valor_pago']:,.2f} | Data: {b['data_pagamento']}")
else:
    print('\n⚠️  Nenhum pagamento encontrado. Você precisa baixar uma conta primeiro!')
