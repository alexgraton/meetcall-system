"""
Model para Dashboard Financeiro
Calcula KPIs, indicadores e métricas estratégicas
"""

from decimal import Decimal
from datetime import datetime, timedelta
from database import DatabaseManager

class DashboardModel:
    """Modelo para dashboard financeiro com KPIs e indicadores"""
    
    @staticmethod
    def get_kpis_gerais():
        """
        Retorna KPIs gerais do sistema
        
        Returns:
            dict: Métricas gerais (receitas, despesas, saldo, etc)
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            hoje = datetime.now().date()
            mes_atual_inicio = hoje.replace(day=1)
            
            # Último dia do mês
            if hoje.month == 12:
                mes_atual_fim = hoje.replace(day=31)
            else:
                proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
                mes_atual_fim = proximo_mes - timedelta(days=1)
            
            # Contas a Receber - Mês Atual (vencimento no mês)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_contas,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor_total,
                    COALESCE(SUM(CASE WHEN status = 'recebida' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as recebido,
                    COALESCE(SUM(CASE WHEN status = 'pendente' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as pendente,
                    COALESCE(SUM(CASE WHEN status = 'vencida' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as vencido
                FROM contas_receber
                WHERE data_vencimento >= %s AND data_vencimento <= %s
            """, (mes_atual_inicio, mes_atual_fim))
            contas_receber_mes = cursor.fetchone()
            
            # Contas a Pagar - Mês Atual (vencimento no mês)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_contas,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor_total,
                    COALESCE(SUM(CASE WHEN status = 'paga' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as pago,
                    COALESCE(SUM(CASE WHEN status = 'pendente' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as pendente,
                    COALESCE(SUM(CASE WHEN status = 'vencida' THEN (valor_total - valor_desconto + valor_juros + valor_multa) ELSE 0 END), 0) as vencido
                FROM contas_pagar
                WHERE data_vencimento >= %s AND data_vencimento <= %s
            """, (mes_atual_inicio, mes_atual_fim))
            contas_pagar_mes = cursor.fetchone()
            
            # Lançamentos Manuais - Mês Atual
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) as receitas,
                    COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) as despesas
                FROM lancamentos_manuais
                WHERE data_lancamento >= %s AND data_lancamento <= %s
                  AND status = 'ativo'
            """, (mes_atual_inicio, mes_atual_fim))
            lancamentos = cursor.fetchone()
            
            # Saldo em Contas Bancárias
            cursor.execute("""
                SELECT COALESCE(SUM(saldo_atual), 0) as saldo_total
                FROM contas_bancarias
                WHERE ativo = 1
            """)
            saldo_bancos = cursor.fetchone()
            
            # Contas a Receber Vencendo Próximos 7 dias
            proximos_7_dias = hoje + timedelta(days=7)
            cursor.execute("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor
                FROM contas_receber
                WHERE status IN ('pendente', 'vencida')
                  AND data_vencimento BETWEEN %s AND %s
            """, (hoje, proximos_7_dias))
            receber_7dias = cursor.fetchone()
            
            # Contas a Pagar Vencendo Próximos 7 dias
            cursor.execute("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor
                FROM contas_pagar
                WHERE status IN ('pendente', 'vencida')
                  AND data_vencimento BETWEEN %s AND %s
            """, (hoje, proximos_7_dias))
            pagar_7dias = cursor.fetchone()
            
            # Calcular totais (considerando apenas valores realizados)
            total_receitas = Decimal(str(contas_receber_mes['recebido'])) + Decimal(str(lancamentos['receitas']))
            total_despesas = Decimal(str(contas_pagar_mes['pago'])) + Decimal(str(lancamentos['despesas']))
            
            return {
                'contas_receber': {
                    'total': Decimal(str(contas_receber_mes['valor_total'])),
                    'recebido': Decimal(str(contas_receber_mes['recebido'])),
                    'pendente': Decimal(str(contas_receber_mes['pendente'])),
                    'vencido': Decimal(str(contas_receber_mes['vencido'])),
                    'quantidade': contas_receber_mes['total_contas'],
                    'vencendo_7dias': {
                        'quantidade': receber_7dias['quantidade'],
                        'valor': Decimal(str(receber_7dias['valor']))
                    }
                },
                'contas_pagar': {
                    'total': Decimal(str(contas_pagar_mes['valor_total'])),
                    'pago': Decimal(str(contas_pagar_mes['pago'])),
                    'pendente': Decimal(str(contas_pagar_mes['pendente'])),
                    'vencido': Decimal(str(contas_pagar_mes['vencido'])),
                    'quantidade': contas_pagar_mes['total_contas'],
                    'vencendo_7dias': {
                        'quantidade': pagar_7dias['quantidade'],
                        'valor': Decimal(str(pagar_7dias['valor']))
                    }
                },
                'lancamentos': {
                    'receitas': Decimal(str(lancamentos['receitas'])),
                    'despesas': Decimal(str(lancamentos['despesas']))
                },
                'resumo': {
                    'total_receitas': total_receitas,
                    'total_despesas': total_despesas,
                    'saldo_periodo': total_receitas - total_despesas,
                    'saldo_bancos': Decimal(str(saldo_bancos['saldo_total']))
                }
            }
    
    @staticmethod
    def get_inadimplencia():
        """
        Calcula taxa de inadimplência
        
        Returns:
            dict: Dados de inadimplência
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            hoje = datetime.now().date()
            
            # Contas a Receber Vencidas
            cursor.execute("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor_total
                FROM contas_receber
                WHERE status = 'vencida' AND data_vencimento < %s
            """, (hoje,))
            vencidas = cursor.fetchone()
            
            # Total de Contas a Receber
            cursor.execute("""
                SELECT 
                    COUNT(*) as quantidade,
                    COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as valor_total
                FROM contas_receber
                WHERE status IN ('pendente', 'vencida')
            """)
            total = cursor.fetchone()
            
            valor_vencido = Decimal(str(vencidas['valor_total']))
            valor_total = Decimal(str(total['valor_total']))
            
            taxa_inadimplencia = (valor_vencido / valor_total * 100) if valor_total > 0 else Decimal('0')
            
            return {
                'quantidade_vencidas': vencidas['quantidade'],
                'valor_vencido': valor_vencido,
                'valor_total': valor_total,
                'taxa_inadimplencia': taxa_inadimplencia
            }
    
    @staticmethod
    def get_evolucao_mensal(meses=6):
        """
        Retorna evolução de receitas e despesas nos últimos meses
        
        Args:
            meses (int): Quantidade de meses a retornar
        
        Returns:
            list: Dados mensais de receitas e despesas
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            evolucao = []
            hoje = datetime.now().date()
            
            for i in range(meses - 1, -1, -1):
                # Calcular primeiro e último dia do mês
                mes_ref = hoje - timedelta(days=30 * i)
                primeiro_dia = mes_ref.replace(day=1)
                
                # Último dia do mês
                if mes_ref.month == 12:
                    ultimo_dia = mes_ref.replace(day=31)
                else:
                    proximo_mes = mes_ref.replace(month=mes_ref.month + 1, day=1)
                    ultimo_dia = proximo_mes - timedelta(days=1)
                
                # Receitas do mês
                cursor.execute("""
                    SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
                    FROM contas_receber
                    WHERE status = 'recebida' 
                      AND data_recebimento >= %s 
                      AND data_recebimento <= %s
                """, (primeiro_dia, ultimo_dia))
                receitas_receber = cursor.fetchone()['total']
                
                cursor.execute("""
                    SELECT COALESCE(SUM(valor), 0) as total
                    FROM lancamentos_manuais
                    WHERE tipo = 'receita'
                      AND status = 'ativo'
                      AND data_lancamento >= %s 
                      AND data_lancamento <= %s
                """, (primeiro_dia, ultimo_dia))
                receitas_lancamentos = cursor.fetchone()['total']
                
                # Despesas do mês
                cursor.execute("""
                    SELECT COALESCE(SUM(valor_total - valor_desconto + valor_juros + valor_multa), 0) as total
                    FROM contas_pagar
                    WHERE status = 'paga' 
                      AND data_pagamento >= %s 
                      AND data_pagamento <= %s
                """, (primeiro_dia, ultimo_dia))
                despesas_pagar = cursor.fetchone()['total']
                
                cursor.execute("""
                    SELECT COALESCE(SUM(valor), 0) as total
                    FROM lancamentos_manuais
                    WHERE tipo = 'despesa'
                      AND status = 'ativo'
                      AND data_lancamento >= %s 
                      AND data_lancamento <= %s
                """, (primeiro_dia, ultimo_dia))
                despesas_lancamentos = cursor.fetchone()['total']
                
                total_receitas = Decimal(str(receitas_receber)) + Decimal(str(receitas_lancamentos))
                total_despesas = Decimal(str(despesas_pagar)) + Decimal(str(despesas_lancamentos))
                
                evolucao.append({
                    'mes': primeiro_dia.strftime('%b/%y'),
                    'receitas': total_receitas,
                    'despesas': total_despesas,
                    'saldo': total_receitas - total_despesas
                })
            
            return evolucao
    
    @staticmethod
    def get_top_clientes(limite=5):
        """
        Retorna top clientes por valor recebido
        
        Args:
            limite (int): Quantidade de clientes a retornar
        
        Returns:
            list: Top clientes
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    c.id,
                    c.nome,
                    c.razao_social,
                    COUNT(cr.id) as quantidade_contas,
                    COALESCE(SUM(cr.valor_total - cr.valor_desconto + cr.valor_juros + cr.valor_multa), 0) as valor_total
                FROM clientes c
                INNER JOIN contas_receber cr ON c.id = cr.cliente_id
                WHERE cr.status = 'recebida'
                GROUP BY c.id, c.nome, c.razao_social
                ORDER BY valor_total DESC
                LIMIT %s
            """, (limite,))
            
            clientes = cursor.fetchall()
            
            for cliente in clientes:
                cliente['valor_total'] = Decimal(str(cliente['valor_total']))
            
            return clientes
    
    @staticmethod
    def get_top_fornecedores(limite=5):
        """
        Retorna top fornecedores por valor pago
        
        Args:
            limite (int): Quantidade de fornecedores a retornar
        
        Returns:
            list: Top fornecedores
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    f.id,
                    f.nome,
                    COUNT(cp.id) as quantidade_contas,
                    COALESCE(SUM(cp.valor_total - cp.valor_desconto + cp.valor_juros + cp.valor_multa), 0) as valor_total
                FROM fornecedores f
                INNER JOIN contas_pagar cp ON f.id = cp.fornecedor_id
                WHERE cp.status = 'paga'
                GROUP BY f.id, f.nome
                ORDER BY valor_total DESC
                LIMIT %s
            """, (limite,))
            
            fornecedores = cursor.fetchall()
            
            for fornecedor in fornecedores:
                fornecedor['valor_total'] = Decimal(str(fornecedor['valor_total']))
            
            return fornecedores
    
    @staticmethod
    def get_distribuicao_despesas():
        """
        Retorna distribuição de despesas por centro de custo
        
        Returns:
            list: Despesas por centro de custo
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            hoje = datetime.now().date()
            mes_atual_inicio = hoje.replace(day=1)
            
            cursor.execute("""
                SELECT 
                    cc.codigo,
                    cc.descricao,
                    COALESCE(SUM(cp.valor_total - cp.valor_desconto + cp.valor_juros + cp.valor_multa), 0) as valor
                FROM centro_custos cc
                LEFT JOIN contas_pagar cp ON cc.id = cp.centro_custo_id 
                    AND cp.status = 'paga'
                    AND cp.data_pagamento >= %s
                    AND cp.data_pagamento <= %s
                WHERE cc.is_active = 1
                GROUP BY cc.id, cc.codigo, cc.descricao
                HAVING valor > 0
                ORDER BY valor DESC
                LIMIT 10
            """, (mes_atual_inicio, hoje))
            
            distribuicao = cursor.fetchall()
            
            for item in distribuicao:
                item['valor'] = Decimal(str(item['valor']))
            
            return distribuicao
