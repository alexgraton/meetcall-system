#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular Contas a Pagar com dados de exemplo
"""

from app import app
from models.conta_pagar import ContaPagarModel
from models.fornecedor import FornecedorModel
from models.plano_conta import PlanoContaModel
from models.centro_custo import CentroCustoModel
from models.filial import FilialModel
from datetime import datetime, timedelta

def popular():
    """Popula contas a pagar com exemplos variados"""
    
    print("Iniciando população de Contas a Pagar...\n")
    
    # Buscar dados necessários
    fornecedores = FornecedorModel.get_all()
    contas_despesa = PlanoContaModel.get_analiticas(tipo='despesa')
    centros_custo = CentroCustoModel.get_all()
    filiais = FilialModel.get_all()
    
    if not fornecedores:
        print("❌ Nenhum fornecedor encontrado. Execute popular_fornecedores.py primeiro.")
        return
    
    if not contas_despesa:
        print("❌ Nenhuma conta de despesa analítica encontrada. Execute popular_plano_contas.py primeiro.")
        return
    
    print(f"✓ {len(fornecedores)} fornecedores disponíveis")
    print(f"✓ {len(contas_despesa)} contas de despesa analíticas")
    print(f"✓ {len(centros_custo)} centros de custo\n")
    
    # Contas a criar
    contas = [
        # 1. Conta simples (à vista, pendente)
        {
            'fornecedor_id': fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Aluguel' in c['descricao']), contas_despesa[0]['id']),
            'centro_custo_id': centros_custo[0]['id'] if centros_custo else None,
            'filial_id': filiais[0]['id'] if filiais else None,
            'descricao': 'Aluguel - Janeiro/2025',
            'numero_documento': 'BOL-2025-001',
            'valor_total': 5000.00,
            'numero_parcelas': 1,
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=15)).date(),
            'percentual_juros': 0.033,  # 1% ao mês = 0.033% ao dia
            'percentual_multa': 2.0,
            'observacoes': 'Aluguel do escritório central'
        },
        
        # 2. Conta parcelada (3x)
        {
            'fornecedor_id': fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Software' in c.get('descricao', '') or 'Licenças' in c.get('descricao', '')), contas_despesa[1]['id']),
            'centro_custo_id': centros_custo[1]['id'] if len(centros_custo) > 1 else centros_custo[0]['id'],
            'descricao': 'Licenças de Software - Microsoft 365',
            'numero_documento': 'NF-2025-789',
            'valor_total': 3000.00,
            'numero_parcelas': 3,
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=30)).date(),
            'percentual_juros': 0.033,
            'percentual_multa': 2.0
        },
        
        # 3. Conta vencida (para testar cálculo de juros)
        {
            'fornecedor_id': fornecedores[1]['id'] if len(fornecedores) > 1 else fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Energia' in c.get('descricao', '')), contas_despesa[2]['id']),
            'centro_custo_id': centros_custo[0]['id'] if centros_custo else None,
            'descricao': 'Energia Elétrica - Dezembro/2024',
            'numero_documento': 'COPEL-2024-12',
            'valor_total': 1500.00,
            'numero_parcelas': 1,
            'data_emissao': (datetime.now() - timedelta(days=45)).date(),
            'data_vencimento': (datetime.now() - timedelta(days=10)).date(),  # Vencida há 10 dias
            'percentual_juros': 0.033,
            'percentual_multa': 2.0,
            'observacoes': 'Conta vencida - calcular juros e multa'
        },
        
        # 4. Conta com valor alto (parcelada em 6x)
        {
            'fornecedor_id': fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Equipamentos' in c.get('descricao', '')), contas_despesa[3]['id']),
            'centro_custo_id': centros_custo[2]['id'] if len(centros_custo) > 2 else centros_custo[0]['id'],
            'descricao': 'Aquisição de Equipamentos de TI',
            'numero_documento': 'NF-2025-1001',
            'valor_total': 18000.00,
            'numero_parcelas': 6,
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=30)).date(),
            'percentual_juros': 0.05,  # Juros mais alto
            'percentual_multa': 3.0
        },
        
        # 5. Conta de telefonia/internet
        {
            'fornecedor_id': fornecedores[1]['id'] if len(fornecedores) > 1 else fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Telefone' in c.get('descricao', '') or 'Internet' in c.get('descricao', '')), contas_despesa[4]['id']),
            'centro_custo_id': centros_custo[0]['id'] if centros_custo else None,
            'descricao': 'Telefone e Internet - Janeiro/2025',
            'numero_documento': 'TIM-2025-01',
            'valor_total': 850.00,
            'numero_parcelas': 1,
            'recorrente': True,
            'tipo_recorrencia': 'mensal',
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=10)).date(),
            'percentual_juros': 0.033,
            'percentual_multa': 2.0,
            'observacoes': 'Conta recorrente - renovar mensalmente'
        },
        
        # 6. Conta com vencimento próximo
        {
            'fornecedor_id': fornecedores[2]['id'] if len(fornecedores) > 2 else fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Material' in c.get('descricao', '')), contas_despesa[5]['id']),
            'centro_custo_id': centros_custo[1]['id'] if len(centros_custo) > 1 else centros_custo[0]['id'],
            'descricao': 'Material de Escritório',
            'numero_documento': 'NF-2025-256',
            'valor_total': 450.00,
            'numero_parcelas': 1,
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=3)).date(),  # Vence em 3 dias
            'percentual_juros': 0.033,
            'percentual_multa': 2.0
        },
        
        # 7. Conta de serviços (sem juros/multa)
        {
            'fornecedor_id': fornecedores[0]['id'],
            'conta_contabil_id': next((c['id'] for c in contas_despesa if 'Limpeza' in c.get('descricao', '')), contas_despesa[6]['id']),
            'centro_custo_id': centros_custo[0]['id'] if centros_custo else None,
            'descricao': 'Serviços de Limpeza - Janeiro/2025',
            'numero_documento': 'OS-2025-15',
            'valor_total': 1200.00,
            'numero_parcelas': 1,
            'recorrente': True,
            'tipo_recorrencia': 'mensal',
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=20)).date(),
            'percentual_juros': 0,  # Sem juros
            'percentual_multa': 0,  # Sem multa
            'observacoes': 'Contrato mensal de limpeza'
        },
        
        # 8. Conta parcelada longa (12x)
        {
            'fornecedor_id': fornecedores[1]['id'] if len(fornecedores) > 1 else fornecedores[0]['id'],
            'conta_contabil_id': contas_despesa[7]['id'] if len(contas_despesa) > 7 else contas_despesa[0]['id'],
            'centro_custo_id': centros_custo[0]['id'] if centros_custo else None,
            'filial_id': filiais[1]['id'] if len(filiais) > 1 else (filiais[0]['id'] if filiais else None),
            'descricao': 'Mobiliário para Nova Filial',
            'numero_documento': 'NF-2025-5500',
            'valor_total': 24000.00,
            'numero_parcelas': 12,
            'data_emissao': datetime.now().date(),
            'data_vencimento': (datetime.now() + timedelta(days=30)).date(),
            'percentual_juros': 0.033,
            'percentual_multa': 2.0,
            'observacoes': 'Parcelamento em 12x - Mobiliário completo'
        }
    ]
    
    sucesso = 0
    erros = 0
    total_parcelas = 0
    
    for conta in contas:
        resultado = ContaPagarModel.create(conta)
        
        if resultado['success']:
            sucesso += 1
            parcelas = conta.get('numero_parcelas', 1)
            total_parcelas += parcelas
            
            status_icon = "💵" if parcelas == 1 else f"📊 {parcelas}x"
            vencimento_str = conta['data_vencimento'].strftime('%d/%m/%Y')
            
            print(f"{status_icon} {conta['descricao']}")
            print(f"    Fornecedor: {conta['fornecedor_id']} | Valor: R$ {conta['valor_total']:.2f} | Venc: {vencimento_str}")
            
            if parcelas > 1:
                print(f"    ✓ Criadas {parcelas} parcelas automaticamente")
        else:
            erros += 1
            print(f"✗ ERRO: {conta['descricao']} - {resultado['message']}")
    
    print(f"\n{'='*70}")
    print(f"População concluída!")
    print(f"Sucesso: {sucesso} contas ({total_parcelas} parcelas total)")
    print(f"Erros: {erros}")
    print(f"{'='*70}")
    
    # Mostrar totalizadores
    totalizadores = ContaPagarModel.get_totalizadores()
    print(f"\n📊 TOTALIZADORES:")
    print(f"   Pendentes: R$ {totalizadores['total_pendente']:.2f}")
    print(f"   Vencidas:  R$ {totalizadores['total_vencido']:.2f}")
    print(f"   Pagas:     R$ {totalizadores['total_pago']:.2f}")
    print(f"   TOTAL:     R$ {totalizadores['total_geral']:.2f}")

if __name__ == '__main__':
    with app.app_context():
        popular()
