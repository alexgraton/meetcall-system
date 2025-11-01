"""
Modelo para geração de relatórios financeiros
"""
from database import DatabaseManager
from datetime import datetime, timedelta
from decimal import Decimal


class Relatorios:
    """Modelo para relatórios financeiros (DRE, Balanço, DFC, etc)"""
    
    @staticmethod
    def get_dre(data_inicio, data_fim):
        """
        Gera o DRE (Demonstrativo do Resultado do Exercício)
        
        Args:
            data_inicio: Data inicial do período (formato YYYY-MM-DD)
            data_fim: Data final do período (formato YYYY-MM-DD)
            
        Returns:
            dict com estrutura do DRE
        """
        db = DatabaseManager()
        
        # Estrutura do DRE
        dre = {
            'periodo': {
                'inicio': data_inicio,
                'fim': data_fim
            },
            'receitas_operacionais': {
                'vendas_servicos': Decimal('0'),
                'outras_receitas': Decimal('0'),
                'total': Decimal('0')
            },
            'deducoes_receita': {
                'descontos': Decimal('0'),
                'total': Decimal('0')
            },
            'receita_liquida': Decimal('0'),
            'custos_operacionais': {
                'custos_servicos': Decimal('0'),
                'total': Decimal('0')
            },
            'lucro_bruto': Decimal('0'),
            'despesas_operacionais': {
                'administrativas': Decimal('0'),
                'comerciais': Decimal('0'),
                'financeiras': Decimal('0'),
                'outras': Decimal('0'),
                'total': Decimal('0')
            },
            'resultado_operacional': Decimal('0'),
            'outras_receitas_despesas': Decimal('0'),
            'resultado_antes_impostos': Decimal('0'),
            'impostos': Decimal('0'),
            'lucro_liquido': Decimal('0')
        }
        
        # 1. RECEITAS - Contas a Receber recebidas no período
        query_receitas = """
            SELECT 
                pc.tipo,
                pc.categoria,
                SUM(cr.valor_total - cr.valor_desconto + cr.valor_juros + cr.valor_multa) as valor
            FROM contas_receber cr
            INNER JOIN plano_contas pc ON cr.plano_contas_id = pc.id
            WHERE cr.status = 'recebida'
            AND cr.data_recebimento BETWEEN %s AND %s
            GROUP BY pc.tipo, pc.categoria
        """
        receitas = db.execute_query(query_receitas, (data_inicio, data_fim))
        
        for receita in receitas:
            valor = receita['valor'] if receita['valor'] else Decimal('0')
            categoria = receita['categoria'].lower() if receita['categoria'] else ''
            
            if 'venda' in categoria or 'servico' in categoria or 'serviço' in categoria:
                dre['receitas_operacionais']['vendas_servicos'] += valor
            else:
                dre['receitas_operacionais']['outras_receitas'] += valor
        
        # 2. DESCONTOS - Total de descontos concedidos
        query_descontos = """
            SELECT SUM(valor_desconto) as total_descontos
            FROM contas_receber
            WHERE status = 'recebida'
            AND data_recebimento BETWEEN %s AND %s
            AND valor_desconto > 0
        """
        result_descontos = db.execute_query(query_descontos, (data_inicio, data_fim))
        if result_descontos and result_descontos[0]['total_descontos']:
            dre['deducoes_receita']['descontos'] = result_descontos[0]['total_descontos']
        
        # 3. LANÇAMENTOS MANUAIS - Receitas
        query_lancamentos_receita = """
            SELECT SUM(valor) as total
            FROM lancamentos_manuais
            WHERE tipo = 'receita'
            AND data_lancamento BETWEEN %s AND %s
        """
        result_lanc_rec = db.execute_query(query_lancamentos_receita, (data_inicio, data_fim))
        if result_lanc_rec and result_lanc_rec[0]['total']:
            dre['receitas_operacionais']['outras_receitas'] += result_lanc_rec[0]['total']
        
        # 4. DESPESAS - Contas a Pagar pagas no período
        query_despesas = """
            SELECT 
                pc.tipo,
                pc.categoria,
                SUM(cp.valor_total - cp.valor_desconto + cp.valor_juros + cp.valor_multa) as valor
            FROM contas_pagar cp
            INNER JOIN plano_contas pc ON cp.plano_contas_id = pc.id
            WHERE cp.status = 'paga'
            AND cp.data_pagamento BETWEEN %s AND %s
            GROUP BY pc.tipo, pc.categoria
        """
        despesas = db.execute_query(query_despesas, (data_inicio, data_fim))
        
        for despesa in despesas:
            valor = despesa['valor'] if despesa['valor'] else Decimal('0')
            categoria = despesa['categoria'].lower() if despesa['categoria'] else ''
            
            if 'custo' in categoria or 'cogs' in categoria or 'cmv' in categoria:
                dre['custos_operacionais']['custos_servicos'] += valor
            elif 'financeira' in categoria or 'juros' in categoria or 'banco' in categoria:
                dre['despesas_operacionais']['financeiras'] += valor
            elif 'administrativa' in categoria or 'admin' in categoria:
                dre['despesas_operacionais']['administrativas'] += valor
            elif 'comercial' in categoria or 'vendas' in categoria or 'marketing' in categoria:
                dre['despesas_operacionais']['comerciais'] += valor
            else:
                dre['despesas_operacionais']['outras'] += valor
        
        # 5. LANÇAMENTOS MANUAIS - Despesas
        query_lancamentos_despesa = """
            SELECT SUM(valor) as total
            FROM lancamentos_manuais
            WHERE tipo = 'despesa'
            AND data_lancamento BETWEEN %s AND %s
        """
        result_lanc_desp = db.execute_query(query_lancamentos_despesa, (data_inicio, data_fim))
        if result_lanc_desp and result_lanc_desp[0]['total']:
            dre['despesas_operacionais']['outras'] += result_lanc_desp[0]['total']
        
        # CÁLCULOS
        dre['receitas_operacionais']['total'] = (
            dre['receitas_operacionais']['vendas_servicos'] + 
            dre['receitas_operacionais']['outras_receitas']
        )
        
        dre['deducoes_receita']['total'] = dre['deducoes_receita']['descontos']
        
        dre['receita_liquida'] = (
            dre['receitas_operacionais']['total'] - 
            dre['deducoes_receita']['total']
        )
        
        dre['custos_operacionais']['total'] = dre['custos_operacionais']['custos_servicos']
        
        dre['lucro_bruto'] = dre['receita_liquida'] - dre['custos_operacionais']['total']
        
        dre['despesas_operacionais']['total'] = (
            dre['despesas_operacionais']['administrativas'] +
            dre['despesas_operacionais']['comerciais'] +
            dre['despesas_operacionais']['financeiras'] +
            dre['despesas_operacionais']['outras']
        )
        
        dre['resultado_operacional'] = dre['lucro_bruto'] - dre['despesas_operacionais']['total']
        
        dre['resultado_antes_impostos'] = dre['resultado_operacional'] + dre['outras_receitas_despesas']
        
        dre['lucro_liquido'] = dre['resultado_antes_impostos'] - dre['impostos']
        
        return dre
    
    @staticmethod
    def get_balanco_patrimonial(data_referencia):
        """
        Gera o Balanço Patrimonial
        
        Args:
            data_referencia: Data de referência (formato YYYY-MM-DD)
            
        Returns:
            dict com estrutura do Balanço
        """
        db = DatabaseManager()
        
        balanco = {
            'data_referencia': data_referencia,
            'ativo': {
                'circulante': {
                    'caixa_bancos': Decimal('0'),
                    'contas_receber': Decimal('0'),
                    'total': Decimal('0')
                },
                'total': Decimal('0')
            },
            'passivo': {
                'circulante': {
                    'contas_pagar': Decimal('0'),
                    'total': Decimal('0')
                },
                'total': Decimal('0')
            },
            'patrimonio_liquido': {
                'capital_social': Decimal('0'),
                'lucros_acumulados': Decimal('0'),
                'total': Decimal('0')
            }
        }
        
        # 1. ATIVO CIRCULANTE - Caixa e Bancos
        query_bancos = """
            SELECT SUM(saldo_atual) as total
            FROM contas_bancarias
            WHERE is_active = 1
        """
        result_bancos = db.execute_query(query_bancos)
        if result_bancos and result_bancos[0]['total']:
            balanco['ativo']['circulante']['caixa_bancos'] = result_bancos[0]['total']
        
        # 2. ATIVO CIRCULANTE - Contas a Receber (pendentes e vencidas até data_referencia)
        query_receber = """
            SELECT SUM(valor_total - valor_desconto + valor_juros + valor_multa) as total
            FROM contas_receber
            WHERE status IN ('pendente', 'vencida')
            AND data_vencimento <= %s
        """
        result_receber = db.execute_query(query_receber, (data_referencia,))
        if result_receber and result_receber[0]['total']:
            balanco['ativo']['circulante']['contas_receber'] = result_receber[0]['total']
        
        # 3. PASSIVO CIRCULANTE - Contas a Pagar (pendentes e vencidas até data_referencia)
        query_pagar = """
            SELECT SUM(valor_total - valor_desconto + valor_juros + valor_multa) as total
            FROM contas_pagar
            WHERE status IN ('pendente', 'vencida')
            AND data_vencimento <= %s
        """
        result_pagar = db.execute_query(query_pagar, (data_referencia,))
        if result_pagar and result_pagar[0]['total']:
            balanco['passivo']['circulante']['contas_pagar'] = result_pagar[0]['total']
        
        # CÁLCULOS
        balanco['ativo']['circulante']['total'] = (
            balanco['ativo']['circulante']['caixa_bancos'] +
            balanco['ativo']['circulante']['contas_receber']
        )
        balanco['ativo']['total'] = balanco['ativo']['circulante']['total']
        
        balanco['passivo']['circulante']['total'] = balanco['passivo']['circulante']['contas_pagar']
        balanco['passivo']['total'] = balanco['passivo']['circulante']['total']
        
        # Patrimônio Líquido = Ativo - Passivo
        balanco['patrimonio_liquido']['lucros_acumulados'] = (
            balanco['ativo']['total'] - balanco['passivo']['total']
        )
        balanco['patrimonio_liquido']['total'] = balanco['patrimonio_liquido']['lucros_acumulados']
        
        return balanco
    
    @staticmethod
    def get_dfc(data_inicio, data_fim):
        """
        Gera o DFC (Demonstração do Fluxo de Caixa)
        
        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            dict com estrutura do DFC
        """
        db = DatabaseManager()
        
        dfc = {
            'periodo': {
                'inicio': data_inicio,
                'fim': data_fim
            },
            'operacional': {
                'recebimentos': Decimal('0'),
                'pagamentos': Decimal('0'),
                'total': Decimal('0')
            },
            'investimento': {
                'total': Decimal('0')
            },
            'financiamento': {
                'total': Decimal('0')
            },
            'saldo_inicial': Decimal('0'),
            'variacao': Decimal('0'),
            'saldo_final': Decimal('0')
        }
        
        # 1. Saldo inicial (bancos no início do período)
        # Para simplificar, vamos calcular retroativamente
        query_movimentos_anteriores = """
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) as saldo_anterior
            FROM lancamentos_manuais
            WHERE data_lancamento < %s
        """
        result_anterior = db.execute_query(query_movimentos_anteriores, (data_inicio,))
        
        query_recebimentos_anteriores = """
            SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
            FROM contas_receber
            WHERE status = 'recebida'
            AND data_recebimento < %s
        """
        result_rec_anterior = db.execute_query(query_recebimentos_anteriores, (data_inicio,))
        
        query_pagamentos_anteriores = """
            SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
            FROM contas_pagar
            WHERE status = 'paga'
            AND data_pagamento < %s
        """
        result_pag_anterior = db.execute_query(query_pagamentos_anteriores, (data_inicio,))
        
        saldo_movimentos = result_anterior[0]['saldo_anterior'] if result_anterior else Decimal('0')
        saldo_recebimentos = result_rec_anterior[0]['total'] if result_rec_anterior else Decimal('0')
        saldo_pagamentos = result_pag_anterior[0]['total'] if result_pag_anterior else Decimal('0')
        
        dfc['saldo_inicial'] = saldo_movimentos + saldo_recebimentos - saldo_pagamentos
        
        # 2. FLUXO OPERACIONAL - Recebimentos
        query_recebimentos = """
            SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
            FROM contas_receber
            WHERE status = 'recebida'
            AND data_recebimento BETWEEN %s AND %s
        """
        result_recebimentos = db.execute_query(query_recebimentos, (data_inicio, data_fim))
        if result_recebimentos:
            dfc['operacional']['recebimentos'] = result_recebimentos[0]['total']
        
        # 3. Lançamentos manuais - Receitas
        query_lanc_receitas = """
            SELECT COALESCE(SUM(valor), 0) as total
            FROM lancamentos_manuais
            WHERE tipo = 'receita'
            AND data_lancamento BETWEEN %s AND %s
        """
        result_lanc_rec = db.execute_query(query_lanc_receitas, (data_inicio, data_fim))
        if result_lanc_rec:
            dfc['operacional']['recebimentos'] += result_lanc_rec[0]['total']
        
        # 4. FLUXO OPERACIONAL - Pagamentos
        query_pagamentos = """
            SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
            FROM contas_pagar
            WHERE status = 'paga'
            AND data_pagamento BETWEEN %s AND %s
        """
        result_pagamentos = db.execute_query(query_pagamentos, (data_inicio, data_fim))
        if result_pagamentos:
            dfc['operacional']['pagamentos'] = result_pagamentos[0]['total']
        
        # 5. Lançamentos manuais - Despesas
        query_lanc_despesas = """
            SELECT COALESCE(SUM(valor), 0) as total
            FROM lancamentos_manuais
            WHERE tipo = 'despesa'
            AND data_lancamento BETWEEN %s AND %s
        """
        result_lanc_desp = db.execute_query(query_lanc_despesas, (data_inicio, data_fim))
        if result_lanc_desp:
            dfc['operacional']['pagamentos'] += result_lanc_desp[0]['total']
        
        # CÁLCULOS
        dfc['operacional']['total'] = dfc['operacional']['recebimentos'] - dfc['operacional']['pagamentos']
        
        dfc['variacao'] = (
            dfc['operacional']['total'] +
            dfc['investimento']['total'] +
            dfc['financiamento']['total']
        )
        
        dfc['saldo_final'] = dfc['saldo_inicial'] + dfc['variacao']
        
        return dfc
    
    @staticmethod
    def get_analise_horizontal(data_inicio_1, data_fim_1, data_inicio_2, data_fim_2):
        """
        Gera análise horizontal comparando dois períodos
        
        Args:
            data_inicio_1, data_fim_1: Primeiro período
            data_inicio_2, data_fim_2: Segundo período
            
        Returns:
            dict com comparação entre períodos
        """
        dre_1 = Relatorios.get_dre(data_inicio_1, data_fim_1)
        dre_2 = Relatorios.get_dre(data_inicio_2, data_fim_2)
        
        analise = {
            'periodo_1': {'inicio': data_inicio_1, 'fim': data_fim_1},
            'periodo_2': {'inicio': data_inicio_2, 'fim': data_fim_2},
            'comparacao': {}
        }
        
        # Comparar principais indicadores
        indicadores = [
            ('receita_liquida', 'Receita Líquida'),
            ('lucro_bruto', 'Lucro Bruto'),
            ('resultado_operacional', 'Resultado Operacional'),
            ('lucro_liquido', 'Lucro Líquido')
        ]
        
        for chave, nome in indicadores:
            valor_1 = dre_1.get(chave, Decimal('0'))
            valor_2 = dre_2.get(chave, Decimal('0'))
            
            variacao_absoluta = valor_2 - valor_1
            variacao_percentual = Decimal('0')
            
            if valor_1 != 0:
                variacao_percentual = (variacao_absoluta / valor_1) * Decimal('100')
            
            analise['comparacao'][chave] = {
                'nome': nome,
                'periodo_1': valor_1,
                'periodo_2': valor_2,
                'variacao_absoluta': variacao_absoluta,
                'variacao_percentual': variacao_percentual
            }
        
        return analise
    
    @staticmethod
    def get_analise_vertical(data_inicio, data_fim):
        """
        Gera análise vertical (percentual sobre receita total)
        
        Args:
            data_inicio, data_fim: Período da análise
            
        Returns:
            dict com percentuais sobre receita
        """
        dre = Relatorios.get_dre(data_inicio, data_fim)
        
        analise = {
            'periodo': {'inicio': data_inicio, 'fim': data_fim},
            'indicadores': {}
        }
        
        receita_total = dre['receitas_operacionais']['total']
        
        if receita_total == 0:
            return analise
        
        # Calcular percentuais
        indicadores = [
            ('receitas_operacionais', 'total', 'Receita Operacional'),
            ('deducoes_receita', 'total', 'Deduções'),
            ('receita_liquida', None, 'Receita Líquida'),
            ('custos_operacionais', 'total', 'Custos Operacionais'),
            ('lucro_bruto', None, 'Lucro Bruto'),
            ('despesas_operacionais', 'total', 'Despesas Operacionais'),
            ('resultado_operacional', None, 'Resultado Operacional'),
            ('lucro_liquido', None, 'Lucro Líquido')
        ]
        
        for item in indicadores:
            if len(item) == 3 and item[1] is not None:
                chave_principal, chave_secundaria, nome = item
                valor = dre[chave_principal][chave_secundaria]
            else:
                chave_principal, _, nome = item
                valor = dre[chave_principal]
            
            percentual = (valor / receita_total) * Decimal('100')
            
            analise['indicadores'][chave_principal] = {
                'nome': nome,
                'valor': valor,
                'percentual': percentual
            }
        
        return analise
