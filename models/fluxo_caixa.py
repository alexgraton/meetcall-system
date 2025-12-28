"""
Model para Fluxo de Caixa
Consolida dados de contas a pagar, contas a receber e lançamentos manuais
para visualização de entradas, saídas e projeções
"""

from decimal import Decimal
from datetime import datetime, timedelta
from database import DatabaseManager

class FluxoCaixaModel:
    """Modelo para análise de fluxo de caixa"""
    
    @staticmethod
    def get_movimentacoes(data_inicio, data_fim, filial_id=None, conta_bancaria_id=None):
        """
        Retorna todas as movimentações financeiras consolidadas
        
        Args:
            data_inicio (date): Data inicial do período
            data_fim (date): Data final do período
            filial_id (int): Filtrar por filial (opcional)
            conta_bancaria_id (int): Filtrar por conta bancária (opcional)
        
        Returns:
            dict: {
                'entradas': [],  # Lista de entradas
                'saidas': [],    # Lista de saídas
                'resumo': {}     # Resumo totalizador
            }
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            entradas = []
            saidas = []
            
            # 1. CONTAS A RECEBER (pagas)
            sql_receber = """
                SELECT 
                    cr.id,
                    cr.descricao,
                    cr.valor_total as valor,
                    cr.data_recebimento as data,
                    'conta_receber' as tipo,
                    'realizado' as status,
                    c.nome as cliente,
                    f.nome as filial
                FROM contas_receber cr
                LEFT JOIN clientes c ON cr.cliente_id = c.id
                LEFT JOIN filiais f ON cr.filial_id = f.id
                WHERE cr.status = 'recebido'
                  AND cr.data_recebimento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_receber += " AND cr.filial_id = %s"
                params.append(filial_id)
            
            if conta_bancaria_id:
                sql_receber += " AND cr.conta_bancaria_id = %s"
                params.append(conta_bancaria_id)
            
            cursor.execute(sql_receber, params)
            entradas.extend(cursor.fetchall())
            
            # 2. CONTAS A RECEBER (a receber - projetado)
            sql_receber_projetado = """
                SELECT 
                    cr.id,
                    cr.descricao,
                    cr.valor_total as valor,
                    cr.data_vencimento as data,
                    'conta_receber' as tipo,
                    'projetado' as status,
                    c.nome as cliente,
                    f.nome as filial
                FROM contas_receber cr
                LEFT JOIN clientes c ON cr.cliente_id = c.id
                LEFT JOIN filiais f ON cr.filial_id = f.id
                WHERE cr.status IN ('pendente', 'vencido')
                  AND cr.data_vencimento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_receber_projetado += " AND cr.filial_id = %s"
                params.append(filial_id)
            
            if conta_bancaria_id:
                sql_receber_projetado += " AND cr.conta_bancaria_id = %s"
                params.append(conta_bancaria_id)
            
            cursor.execute(sql_receber_projetado, params)
            entradas.extend(cursor.fetchall())
            
            # 3. LANÇAMENTOS MANUAIS - RECEITAS
            sql_lancamentos_receita = """
                SELECT 
                    lm.id,
                    lm.descricao,
                    lm.valor,
                    lm.data_lancamento as data,
                    'lancamento_manual' as tipo,
                    'realizado' as status,
                    c.nome as cliente,
                    f.nome as filial
                FROM lancamentos_manuais lm
                LEFT JOIN clientes c ON lm.cliente_id = c.id
                LEFT JOIN filiais f ON lm.filial_id = f.id
                WHERE lm.tipo = 'receita'
                  AND lm.status = 'ativo'
                  AND lm.data_lancamento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_lancamentos_receita += " AND lm.filial_id = %s"
                params.append(filial_id)
            
            cursor.execute(sql_lancamentos_receita, params)
            entradas.extend(cursor.fetchall())
            
            # 4. CONTAS A PAGAR (pagas)
            sql_pagar = """
                SELECT 
                    cp.id,
                    cp.descricao,
                    cp.valor_total as valor,
                    cp.data_pagamento as data,
                    'conta_pagar' as tipo,
                    'realizado' as status,
                    fo.nome as fornecedor,
                    f.nome as filial
                FROM contas_pagar cp
                LEFT JOIN fornecedores fo ON cp.fornecedor_id = fo.id
                LEFT JOIN filiais f ON cp.filial_id = f.id
                WHERE cp.status = 'pago'
                  AND cp.data_pagamento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_pagar += " AND cp.filial_id = %s"
                params.append(filial_id)
            
            if conta_bancaria_id:
                sql_pagar += " AND cp.conta_bancaria_id = %s"
                params.append(conta_bancaria_id)
            
            cursor.execute(sql_pagar, params)
            saidas.extend(cursor.fetchall())
            
            # 5. CONTAS A PAGAR (a pagar - projetado)
            sql_pagar_projetado = """
                SELECT 
                    cp.id,
                    cp.descricao,
                    cp.valor_total as valor,
                    cp.data_vencimento as data,
                    'conta_pagar' as tipo,
                    'projetado' as status,
                    fo.nome as fornecedor,
                    f.nome as filial
                FROM contas_pagar cp
                LEFT JOIN fornecedores fo ON cp.fornecedor_id = fo.id
                LEFT JOIN filiais f ON cp.filial_id = f.id
                WHERE cp.status IN ('pendente', 'vencido')
                  AND cp.data_vencimento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_pagar_projetado += " AND cp.filial_id = %s"
                params.append(filial_id)
            
            if conta_bancaria_id:
                sql_pagar_projetado += " AND cp.conta_bancaria_id = %s"
                params.append(conta_bancaria_id)
            
            cursor.execute(sql_pagar_projetado, params)
            saidas.extend(cursor.fetchall())
            
            # 6. LANÇAMENTOS MANUAIS - DESPESAS
            sql_lancamentos_despesa = """
                SELECT 
                    lm.id,
                    lm.descricao,
                    lm.valor,
                    lm.data_lancamento as data,
                    'lancamento_manual' as tipo,
                    'realizado' as status,
                    fo.nome as fornecedor,
                    f.nome as filial
                FROM lancamentos_manuais lm
                LEFT JOIN fornecedores fo ON lm.fornecedor_id = fo.id
                LEFT JOIN filiais f ON lm.filial_id = f.id
                WHERE lm.tipo = 'despesa'
                  AND lm.status = 'ativo'
                  AND lm.data_lancamento BETWEEN %s AND %s
            """
            params = [data_inicio, data_fim]
            
            if filial_id:
                sql_lancamentos_despesa += " AND lm.filial_id = %s"
                params.append(filial_id)
            
            cursor.execute(sql_lancamentos_despesa, params)
            saidas.extend(cursor.fetchall())
            
            # Calcular totalizadores
            total_entradas_realizadas = sum(
                Decimal(str(e['valor'])) for e in entradas if e['status'] == 'realizado'
            )
            total_entradas_projetadas = sum(
                Decimal(str(e['valor'])) for e in entradas if e['status'] == 'projetado'
            )
            total_saidas_realizadas = sum(
                Decimal(str(s['valor'])) for s in saidas if s['status'] == 'realizado'
            )
            total_saidas_projetadas = sum(
                Decimal(str(s['valor'])) for s in saidas if s['status'] == 'projetado'
            )
            
            resumo = {
                'total_entradas_realizadas': total_entradas_realizadas,
                'total_entradas_projetadas': total_entradas_projetadas,
                'total_entradas': total_entradas_realizadas + total_entradas_projetadas,
                'total_saidas_realizadas': total_saidas_realizadas,
                'total_saidas_projetadas': total_saidas_projetadas,
                'total_saidas': total_saidas_realizadas + total_saidas_projetadas,
                'saldo_realizado': total_entradas_realizadas - total_saidas_realizadas,
                'saldo_projetado': (total_entradas_realizadas + total_entradas_projetadas) - 
                                   (total_saidas_realizadas + total_saidas_projetadas)
            }
            
            return {
                'entradas': sorted(entradas, key=lambda x: x['data']),
                'saidas': sorted(saidas, key=lambda x: x['data']),
                'resumo': resumo
            }
    
    @staticmethod
    def get_saldo_inicial(data_referencia, filial_id=None, conta_bancaria_id=None):
        """
        Calcula o saldo inicial somando movimentações ANTES da data de referência
        Parte do princípio que contas iniciaram com saldo zero
        
        Args:
            data_referencia (date): Data de referência para o saldo inicial
            filial_id (int): Filtrar por filial (opcional)
            conta_bancaria_id (int): Filtrar por conta bancária (opcional)
        
        Returns:
            Decimal: Saldo inicial na data de referência
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Calcular movimentações ANTES da data de referência
            # Contas recebidas antes da data
            sql_recebimentos = """
                SELECT COALESCE(SUM(valor_total - COALESCE(valor_desconto, 0) + COALESCE(valor_juros, 0) + COALESCE(valor_multa, 0)), 0) as total
                FROM contas_receber
                WHERE status = 'recebido' AND data_recebimento < %s
            """
            params_mov = [data_referencia]
            
            if filial_id:
                sql_recebimentos += " AND filial_id = %s"
                params_mov.append(filial_id)
            
            if conta_bancaria_id:
                sql_recebimentos += " AND conta_bancaria_id = %s"
                params_mov.append(conta_bancaria_id)
            
            cursor.execute(sql_recebimentos, params_mov)
            recebimentos_anteriores = Decimal(str(cursor.fetchone()['total']))
            
            # Contas pagas antes da data
            params_mov = [data_referencia]
            if filial_id:
                params_mov.append(filial_id)
            if conta_bancaria_id:
                params_mov.append(conta_bancaria_id)
                
            sql_pagamentos = """
                SELECT COALESCE(SUM(valor_total - COALESCE(valor_desconto, 0) + COALESCE(valor_juros, 0) + COALESCE(valor_multa, 0)), 0) as total
                FROM contas_pagar
                WHERE status = 'pago' AND data_pagamento < %s
            """
            
            if filial_id:
                sql_pagamentos += " AND filial_id = %s"
            
            if conta_bancaria_id:
                sql_pagamentos += " AND conta_bancaria_id = %s"
            
            cursor.execute(sql_pagamentos, params_mov)
            pagamentos_anteriores = Decimal(str(cursor.fetchone()['total']))
            
            # Lançamentos manuais antes da data
            params_mov = [data_referencia]
            if filial_id:
                params_mov.append(filial_id)
                
            sql_lancamentos = """
                SELECT COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE -valor END), 0) as total
                FROM lancamentos_manuais
                WHERE data_lancamento < %s
            """
            
            if filial_id:
                sql_lancamentos += " AND filial_id = %s"
            
            cursor.execute(sql_lancamentos, params_mov)
            lancamentos_anteriores = Decimal(str(cursor.fetchone()['total']))
            
            cursor.close()
            
            # Saldo inicial = Recebimentos anteriores - Pagamentos anteriores + Lançamentos anteriores
            saldo_inicial = recebimentos_anteriores - pagamentos_anteriores + lancamentos_anteriores
            
            return saldo_inicial
    
    @staticmethod
    def get_projecao_diaria(data_inicio, data_fim, filial_id=None, conta_bancaria_id=None):
        """
        Retorna projeção diária de saldo
        
        Args:
            data_inicio (date): Data inicial
            data_fim (date): Data final
            filial_id (int): Filtrar por filial (opcional)
            conta_bancaria_id (int): Filtrar por conta bancária (opcional)
        
        Returns:
            list: Lista de dicionários com data e saldo projetado
        """
        movimentacoes = FluxoCaixaModel.get_movimentacoes(data_inicio, data_fim, filial_id, conta_bancaria_id)
        saldo_atual = FluxoCaixaModel.get_saldo_inicial(data_inicio, filial_id, conta_bancaria_id)
        
        # Agrupar movimentações por data
        mov_por_data = {}
        
        for entrada in movimentacoes['entradas']:
            data = entrada['data']
            if data not in mov_por_data:
                mov_por_data[data] = {'entradas': Decimal('0'), 'saidas': Decimal('0')}
            mov_por_data[data]['entradas'] += Decimal(str(entrada['valor']))
        
        for saida in movimentacoes['saidas']:
            data = saida['data']
            if data not in mov_por_data:
                mov_por_data[data] = {'entradas': Decimal('0'), 'saidas': Decimal('0')}
            mov_por_data[data]['saidas'] += Decimal(str(saida['valor']))
        
        # Gerar projeção diária
        projecao = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            if data_atual in mov_por_data:
                saldo_atual += mov_por_data[data_atual]['entradas']
                saldo_atual -= mov_por_data[data_atual]['saidas']
            
            projecao.append({
                'data': data_atual,
                'saldo': saldo_atual,
                'entradas': mov_por_data.get(data_atual, {}).get('entradas', Decimal('0')),
                'saidas': mov_por_data.get(data_atual, {}).get('saidas', Decimal('0'))
            })
            
            data_atual += timedelta(days=1)
        
        return projecao
