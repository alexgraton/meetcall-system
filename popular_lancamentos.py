#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular a tabela de lançamentos manuais com dados de exemplo
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from database import DatabaseManager

def criar_lancamento(conn, dados):
    """Cria um lançamento manual"""
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO lancamentos_manuais (
            tipo, descricao, valor, data_lancamento, data_competencia,
            filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id,
            fornecedor_id, cliente_id, forma_pagamento, numero_documento, observacoes
        ) VALUES (
            %(tipo)s, %(descricao)s, %(valor)s, %(data_lancamento)s, %(data_competencia)s,
            %(filial_id)s, %(tipo_servico_id)s, %(centro_custo_id)s, %(conta_contabil_id)s,
            %(fornecedor_id)s, %(cliente_id)s, %(forma_pagamento)s, %(numero_documento)s, %(observacoes)s
        )
    """
    
    cursor.execute(sql, dados)
    conn.commit()
    return cursor.lastrowid

def popular_lancamentos():
    """Popula lançamentos manuais de exemplo"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        # Buscar IDs necessários
        cursor = conn.cursor(dictionary=True)
        
        # Filiais
        cursor.execute("SELECT id, nome FROM filiais ORDER BY id LIMIT 2")
        filiais = cursor.fetchall()
        if not filiais:
            print("❌ Erro: Nenhuma filial encontrada. Execute popular_filiais.py primeiro.")
            return
        
        # Fornecedores
        cursor.execute("SELECT id, nome FROM fornecedores ORDER BY id LIMIT 3")
        fornecedores = cursor.fetchall()
        
        # Clientes
        cursor.execute("SELECT id, nome FROM clientes ORDER BY id LIMIT 3")
        clientes = cursor.fetchall()
        
        # Tipos de Serviços
        cursor.execute("SELECT id, nome FROM tipos_servicos ORDER BY id LIMIT 3")
        tipos_servicos = cursor.fetchall()
        
        # Centros de Custo
        cursor.execute("SELECT id, codigo, descricao FROM centro_custos ORDER BY id LIMIT 4")
        centros_custos = cursor.fetchall()
        
        # Plano de Contas (contas analíticas)
        cursor.execute("SELECT id, codigo, descricao FROM plano_contas WHERE tipo = 'analitica' ORDER BY id LIMIT 6")
        plano_contas = cursor.fetchall()
        
        hoje = datetime.now().date()
        
        # Lista de lançamentos para criar
        lancamentos = [
            # DESPESAS
            {
                'tipo': 'despesa',
                'descricao': 'Material de escritório',
                'valor': Decimal('350.50'),
                'data_lancamento': hoje - timedelta(days=5),
                'data_competencia': hoje - timedelta(days=5),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': centros_custos[0]['id'] if centros_custos else None,
                'conta_contabil_id': plano_contas[0]['id'] if plano_contas else None,
                'fornecedor_id': fornecedores[0]['id'] if fornecedores else None,
                'cliente_id': None,
                'forma_pagamento': 'dinheiro',
                'numero_documento': None,
                'observacoes': 'Compra de canetas, papel e clips'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Café e água para escritório',
                'valor': Decimal('180.00'),
                'data_lancamento': hoje - timedelta(days=3),
                'data_competencia': hoje - timedelta(days=3),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': centros_custos[0]['id'] if centros_custos else None,
                'conta_contabil_id': plano_contas[0]['id'] if plano_contas else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'pix',
                'numero_documento': None,
                'observacoes': 'Compra mensal'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Combustível veículo',
                'valor': Decimal('450.00'),
                'data_lancamento': hoje - timedelta(days=8),
                'data_competencia': hoje - timedelta(days=8),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': centros_custos[1]['id'] if len(centros_custos) > 1 else None,
                'conta_contabil_id': plano_contas[1]['id'] if len(plano_contas) > 1 else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'credito',
                'numero_documento': 'NF-8923',
                'observacoes': 'Abastecimento do veículo da empresa'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Manutenção ar condicionado',
                'valor': Decimal('680.00'),
                'data_lancamento': hoje - timedelta(days=12),
                'data_competencia': hoje - timedelta(days=12),
                'filial_id': filiais[1]['id'] if len(filiais) > 1 else filiais[0]['id'],
                'tipo_servico_id': tipos_servicos[0]['id'] if tipos_servicos else None,
                'centro_custo_id': centros_custos[2]['id'] if len(centros_custos) > 2 else None,
                'conta_contabil_id': plano_contas[2]['id'] if len(plano_contas) > 2 else None,
                'fornecedor_id': fornecedores[1]['id'] if len(fornecedores) > 1 else None,
                'cliente_id': None,
                'forma_pagamento': 'transferencia',
                'numero_documento': 'OS-4512',
                'observacoes': 'Manutenção preventiva'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Vale refeição funcionários',
                'valor': Decimal('1200.00'),
                'data_lancamento': hoje - timedelta(days=15),
                'data_competencia': hoje - timedelta(days=15),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': centros_custos[3]['id'] if len(centros_custos) > 3 else None,
                'conta_contabil_id': plano_contas[3]['id'] if len(plano_contas) > 3 else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'transferencia',
                'numero_documento': None,
                'observacoes': 'Recarga mensal vale refeição'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Taxa bancária',
                'valor': Decimal('45.90'),
                'data_lancamento': hoje - timedelta(days=1),
                'data_competencia': hoje - timedelta(days=1),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': centros_custos[0]['id'] if centros_custos else None,
                'conta_contabil_id': plano_contas[0]['id'] if plano_contas else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'debito',
                'numero_documento': None,
                'observacoes': 'Tarifa mensal de manutenção de conta'
            },
            {
                'tipo': 'despesa',
                'descricao': 'Limpeza escritório',
                'valor': Decimal('320.00'),
                'data_lancamento': hoje - timedelta(days=7),
                'data_competencia': hoje - timedelta(days=7),
                'filial_id': filiais[1]['id'] if len(filiais) > 1 else filiais[0]['id'],
                'tipo_servico_id': tipos_servicos[1]['id'] if len(tipos_servicos) > 1 else None,
                'centro_custo_id': centros_custos[0]['id'] if centros_custos else None,
                'conta_contabil_id': plano_contas[0]['id'] if plano_contas else None,
                'fornecedor_id': fornecedores[2]['id'] if len(fornecedores) > 2 else None,
                'cliente_id': None,
                'forma_pagamento': 'pix',
                'numero_documento': None,
                'observacoes': 'Serviço de limpeza quinzenal'
            },
            
            # RECEITAS
            {
                'tipo': 'receita',
                'descricao': 'Venda avulsa de serviço',
                'valor': Decimal('850.00'),
                'data_lancamento': hoje - timedelta(days=4),
                'data_competencia': hoje - timedelta(days=4),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': tipos_servicos[0]['id'] if tipos_servicos else None,
                'centro_custo_id': None,
                'conta_contabil_id': plano_contas[4]['id'] if len(plano_contas) > 4 else None,
                'fornecedor_id': None,
                'cliente_id': clientes[0]['id'] if clientes else None,
                'forma_pagamento': 'pix',
                'numero_documento': 'REC-1001',
                'observacoes': 'Atendimento pontual'
            },
            {
                'tipo': 'receita',
                'descricao': 'Reembolso despesa',
                'valor': Decimal('125.50'),
                'data_lancamento': hoje - timedelta(days=2),
                'data_competencia': hoje - timedelta(days=2),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': None,
                'conta_contabil_id': plano_contas[4]['id'] if len(plano_contas) > 4 else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'transferencia',
                'numero_documento': None,
                'observacoes': 'Reembolso de despesa com táxi'
            },
            {
                'tipo': 'receita',
                'descricao': 'Consultoria avulsa',
                'valor': Decimal('1500.00'),
                'data_lancamento': hoje - timedelta(days=10),
                'data_competencia': hoje - timedelta(days=10),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': tipos_servicos[1]['id'] if len(tipos_servicos) > 1 else None,
                'centro_custo_id': None,
                'conta_contabil_id': plano_contas[5]['id'] if len(plano_contas) > 5 else None,
                'fornecedor_id': None,
                'cliente_id': clientes[1]['id'] if len(clientes) > 1 else None,
                'forma_pagamento': 'transferencia',
                'numero_documento': 'REC-1002',
                'observacoes': 'Consultoria pontual sobre processos'
            },
            {
                'tipo': 'receita',
                'descricao': 'Treinamento in company',
                'valor': Decimal('2400.00'),
                'data_lancamento': hoje - timedelta(days=6),
                'data_competencia': hoje - timedelta(days=6),
                'filial_id': filiais[1]['id'] if len(filiais) > 1 else filiais[0]['id'],
                'tipo_servico_id': tipos_servicos[2]['id'] if len(tipos_servicos) > 2 else None,
                'centro_custo_id': None,
                'conta_contabil_id': plano_contas[5]['id'] if len(plano_contas) > 5 else None,
                'fornecedor_id': None,
                'cliente_id': clientes[2]['id'] if len(clientes) > 2 else None,
                'forma_pagamento': 'boleto',
                'numero_documento': 'REC-1003',
                'observacoes': 'Treinamento de equipe - 8 horas'
            },
            {
                'tipo': 'receita',
                'descricao': 'Venda de equipamento usado',
                'valor': Decimal('580.00'),
                'data_lancamento': hoje - timedelta(days=14),
                'data_competencia': hoje - timedelta(days=14),
                'filial_id': filiais[0]['id'],
                'tipo_servico_id': None,
                'centro_custo_id': None,
                'conta_contabil_id': plano_contas[4]['id'] if len(plano_contas) > 4 else None,
                'fornecedor_id': None,
                'cliente_id': None,
                'forma_pagamento': 'dinheiro',
                'numero_documento': None,
                'observacoes': 'Venda de notebook usado'
            }
        ]
        
        print("\n🔄 Criando lançamentos manuais...")
        print("=" * 80)
        
        total_despesas = Decimal('0')
        total_receitas = Decimal('0')
        criados = 0
        
        for lanc in lancamentos:
            try:
                lancamento_id = criar_lancamento(conn, lanc)
                
                icone = "📉" if lanc['tipo'] == 'despesa' else "📈"
                tipo_str = lanc['tipo'].upper()
                
                if lanc['tipo'] == 'despesa':
                    total_despesas += lanc['valor']
                else:
                    total_receitas += lanc['valor']
                
                print(f"{icone} {tipo_str}: {lanc['descricao'][:40]:<40} R$ {lanc['valor']:>10,.2f}")
                criados += 1
                
            except Exception as e:
                print(f"❌ Erro ao criar lançamento '{lanc['descricao']}': {e}")
        
        saldo = total_receitas - total_despesas
        saldo_icone = "💰" if saldo >= 0 else "⚠️"
        
        print("=" * 80)
        print(f"\n✅ {criados} lançamentos criados com sucesso!")
        print(f"\n📊 Resumo:")
        print(f"   📉 Total Despesas: R$ {total_despesas:,.2f}")
        print(f"   📈 Total Receitas: R$ {total_receitas:,.2f}")
        print(f"   {saldo_icone} Saldo:          R$ {saldo:,.2f}")
        print()

if __name__ == "__main__":
    popular_lancamentos()
