"""
Script para popular tabela de Contas a Receber com dados de teste
"""
from datetime import date, timedelta
from decimal import Decimal
from app import app
from models.conta_receber import ContaReceberModel

# Dados de teste
contas_teste = [
    {
        'descricao': 'Mensalidade - Janeiro/2025',
        'cliente_id': 1,  # Tech Solutions Ltda
        'valor_total': Decimal('8500.00'),
        'data_emissao': date.today() - timedelta(days=5),
        'data_vencimento': date.today() + timedelta(days=10),
        'numero_parcelas': 1,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'NF-001/2025'
    },
    {
        'descricao': '12x Projeto de Consultoria TI',
        'cliente_id': 2,  # Construtora ABC
        'valor_total': Decimal('36000.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=30),
        'numero_parcelas': 12,
        'intervalo_parcelas': 30,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'CONTRATO-002/2025'
    },
    {
        'descricao': 'Servicos Prestados - Dezembro/2024 (VENCIDA)',
        'cliente_id': 4,  # MegaStore Comércio
        'valor_total': Decimal('2200.00'),
        'data_emissao': date(2024, 12, 1),
        'data_vencimento': date(2024, 12, 15),
        'numero_parcelas': 1,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'NF-099/2024'
    },
    {
        'descricao': '6x Licenciamento de Software',
        'cliente_id': 1,  # Tech Solutions Ltda
        'valor_total': Decimal('12000.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=15),
        'numero_parcelas': 6,
        'intervalo_parcelas': 30,
        'percentual_juros': Decimal('0.50'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'CONTRATO-003/2025'
    },
    {
        'descricao': 'Suporte Tecnico - Janeiro/2025',
        'cliente_id': 2,  # Construtora ABC
        'valor_total': Decimal('1500.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=20),
        'numero_parcelas': 1,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'is_recorrente': True,
        'recorrencia_tipo': 'mensal'
    },
    {
        'descricao': 'Treinamento Corporativo',
        'cliente_id': 4,  # MegaStore Comércio
        'valor_total': Decimal('3500.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=7),
        'numero_parcelas': 1,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'NF-002/2025'
    },
    {
        'descricao': '3x Manutencao de Sistemas',
        'cliente_id': 2,  # Construtora ABC
        'valor_total': Decimal('9000.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=30),
        'numero_parcelas': 3,
        'intervalo_parcelas': 30,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00')
    },
    {
        'descricao': 'Desenvolvimento de Website',
        'cliente_id': 1,  # Tech Solutions Ltda
        'valor_total': Decimal('15000.00'),
        'data_emissao': date.today(),
        'data_vencimento': date.today() + timedelta(days=45),
        'numero_parcelas': 1,
        'percentual_juros': Decimal('0.33'),
        'percentual_multa': Decimal('2.00'),
        'numero_documento': 'PROPOSTA-001/2025'
    }
]

def main():
    print("=" * 70)
    print("POPULANDO CONTAS A RECEBER")
    print("=" * 70)
    
    sucesso = 0
    erros = 0
    total_parcelas = 0
    
    with app.app_context():
        for i, conta_dados in enumerate(contas_teste, 1):
            try:
                conta_id = ContaReceberModel.create(conta_dados)
                num_parcelas = conta_dados.get('numero_parcelas', 1)
                total_parcelas += num_parcelas
                
                if num_parcelas > 1:
                    print(f"✅ {i}. {num_parcelas}x {conta_dados['descricao']} (R$ {conta_dados['valor_total']}) - ✓ Criadas {num_parcelas} parcelas")
                else:
                    status = " - VENCIDA" if 'VENCIDA' in conta_dados['descricao'] else ""
                    recorrente = " [RECORRENTE]" if conta_dados.get('is_recorrente') else ""
                    print(f"✅ {i}. {conta_dados['descricao']} (R$ {conta_dados['valor_total']}){status}{recorrente}")
                
                sucesso += 1
                
            except Exception as e:
                print(f"❌ {i}. Erro ao criar: {conta_dados['descricao']} - {e}")
                erros += 1
    
    print("\n" + "=" * 70)
    print(f"Sucesso: {sucesso} contas ({total_parcelas} parcelas total)")
    print(f"Erros: {erros}")
    print("=" * 70)
    
    # Calcular totalizadores
    with app.app_context():
        totais = ContaReceberModel.get_totalizadores()
        print("\nTotalizadores:")
        print(f"  A Receber: R$ {totais['total_pendente']}")
        print(f"  Vencidas: R$ {totais['total_vencido']}")
        print(f"  Recebidas: R$ {totais['total_recebido']}")
        print(f"  TOTAL: R$ {totais['total_geral']}")
    
    print("\n✅ Script finalizado!")

if __name__ == "__main__":
    main()
