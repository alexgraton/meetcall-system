#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular a tabela de contas bancárias com dados de exemplo
"""

from decimal import Decimal
from database import DatabaseManager

def criar_conta(conn, dados):
    """Cria uma conta bancária"""
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO contas_bancarias (
            banco, agencia, numero_conta, tipo_conta, descricao,
            saldo_inicial, saldo_atual, moeda, filial_id, ativo
        ) VALUES (
            %(banco)s, %(agencia)s, %(numero_conta)s, %(tipo_conta)s, %(descricao)s,
            %(saldo_inicial)s, %(saldo_atual)s, %(moeda)s, %(filial_id)s, %(ativo)s
        )
    """
    
    cursor.execute(sql, dados)
    conn.commit()
    return cursor.lastrowid

def popular_contas_bancarias():
    """Popula contas bancárias de exemplo"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar filiais
        cursor.execute("SELECT id, nome FROM filiais ORDER BY id LIMIT 2")
        filiais = cursor.fetchall()
        
        if not filiais:
            print("❌ Erro: Nenhuma filial encontrada. Execute popular_filiais.py primeiro.")
            return
        
        print("\n🔄 Criando contas bancárias...")
        print("=" * 80)
        
        contas = [
            {
                'banco': 'Banco do Brasil',
                'agencia': '1234-5',
                'numero_conta': '12345-6',
                'tipo_conta': 'corrente',
                'descricao': 'Conta principal da matriz',
                'saldo_inicial': Decimal('50000.00'),
                'saldo_atual': Decimal('50000.00'),
                'moeda': 'BRL',
                'filial_id': filiais[0]['id'],
                'ativo': 1
            },
            {
                'banco': 'Itaú Unibanco',
                'agencia': '5678',
                'numero_conta': '98765-4',
                'tipo_conta': 'corrente',
                'descricao': 'Conta operacional',
                'saldo_inicial': Decimal('25000.00'),
                'saldo_atual': Decimal('25000.00'),
                'moeda': 'BRL',
                'filial_id': filiais[0]['id'],
                'ativo': 1
            },
            {
                'banco': 'Bradesco',
                'agencia': '2468-1',
                'numero_conta': '24680-1',
                'tipo_conta': 'poupanca',
                'descricao': 'Reserva de emergência',
                'saldo_inicial': Decimal('100000.00'),
                'saldo_atual': Decimal('100000.00'),
                'moeda': 'BRL',
                'filial_id': filiais[0]['id'],
                'ativo': 1
            },
            {
                'banco': 'Caixa Econômica Federal',
                'agencia': '1357',
                'numero_conta': '00098765-4',
                'tipo_conta': 'corrente',
                'descricao': 'Conta para pagamentos de folha',
                'saldo_inicial': Decimal('35000.00'),
                'saldo_atual': Decimal('35000.00'),
                'moeda': 'BRL',
                'filial_id': filiais[0]['id'],
                'ativo': 1
            }
        ]
        
        # Se houver segunda filial, adicionar conta
        if len(filiais) > 1:
            contas.append({
                'banco': 'Santander',
                'agencia': '9876',
                'numero_conta': '87654-3',
                'tipo_conta': 'corrente',
                'descricao': 'Conta da filial',
                'saldo_inicial': Decimal('15000.00'),
                'saldo_atual': Decimal('15000.00'),
                'moeda': 'BRL',
                'filial_id': filiais[1]['id'],
                'ativo': 1
            })
        
        # Adicionar conta de caixa físico
        contas.append({
            'banco': 'Caixa Interno',
            'agencia': '-',
            'numero_conta': 'CAIXA-001',
            'tipo_conta': 'caixa',
            'descricao': 'Caixa físico do escritório',
            'saldo_inicial': Decimal('2000.00'),
            'saldo_atual': Decimal('2000.00'),
            'moeda': 'BRL',
            'filial_id': filiais[0]['id'],
            'ativo': 1
        })
        
        total_saldo = Decimal('0')
        criadas = 0
        
        for conta in contas:
            try:
                conta_id = criar_conta(conn, conta)
                
                icone = "🏦" if conta['tipo_conta'] == 'corrente' else ("💰" if conta['tipo_conta'] == 'poupanca' else "💵")
                tipo_str = conta['tipo_conta'].upper()
                
                total_saldo += conta['saldo_inicial']
                
                print(f"{icone} {conta['banco']:<30} {tipo_str:<10} R$ {conta['saldo_inicial']:>12,.2f}")
                criadas += 1
                
            except Exception as e:
                print(f"❌ Erro ao criar conta '{conta['banco']}': {e}")
        
        print("=" * 80)
        print(f"\n✅ {criadas} contas bancárias criadas com sucesso!")
        print(f"💰 Saldo total disponível: R$ {total_saldo:,.2f}\n")

if __name__ == "__main__":
    popular_contas_bancarias()
