"""
Modelo para gerenciamento de Contas a Pagar
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, date, timedelta
from database import DatabaseManager

class ContaPagarModel:
    """Operações CRUD para Contas a Pagar"""

    @staticmethod
    def create(dados: Dict) -> Dict:
        """Cria uma nova conta a pagar"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO contas_pagar
                    (fornecedor_id, tipo_servico_id, centro_custo_id, conta_contabil_id, filial_id,
                     descricao, numero_documento, observacoes,
                     valor_total, numero_parcelas, parcela_atual,
                     recorrente, tipo_recorrencia,
                     data_emissao, data_vencimento,
                     percentual_juros, percentual_multa,
                     status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    dados['fornecedor_id'],
                    dados.get('tipo_servico_id'),
                    dados.get('centro_custo_id'),
                    dados.get('conta_contabil_id'),
                    dados.get('filial_id'),
                    dados['descricao'],
                    dados.get('numero_documento'),
                    dados.get('observacoes'),
                    dados['valor_total'],
                    dados.get('numero_parcelas', 1),
                    dados.get('parcela_atual', 1),
                    dados.get('recorrente', False),
                    dados.get('tipo_recorrencia'),
                    dados['data_emissao'],
                    dados['data_vencimento'],
                    dados.get('percentual_juros', 0),
                    dados.get('percentual_multa', 0),
                    'pendente',
                    dados.get('created_by')
                ))
                conn.commit()
                conta_id = cursor.lastrowid
                
                # Se tiver mais de uma parcela, criar as outras
                if dados.get('numero_parcelas', 1) > 1:
                    ContaPagarModel._criar_parcelas(conn, conta_id, dados)
                
                return {'success': True, 'message': 'Conta criada com sucesso', 'id': conta_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def _criar_parcelas(conn, primeira_parcela_id: int, dados: Dict):
        """Cria as parcelas restantes de uma conta parcelada"""
        cursor = conn.cursor()
        numero_parcelas = dados.get('numero_parcelas', 1)
        valor_parcela = Decimal(str(dados['valor_total'])) / numero_parcelas
        
        # Pegar a data de vencimento da primeira parcela
        data_base = datetime.strptime(dados['data_vencimento'], '%Y-%m-%d').date() if isinstance(dados['data_vencimento'], str) else dados['data_vencimento']
        
        for i in range(2, numero_parcelas + 1):
            # Calcular vencimento (30 dias após a anterior)
            data_vencimento = data_base + timedelta(days=30 * (i - 1))
            
            query = """
                INSERT INTO contas_pagar
                (fornecedor_id, tipo_servico_id, centro_custo_id, conta_contabil_id, filial_id,
                 descricao, numero_documento, observacoes,
                 valor_total, numero_parcelas, parcela_atual,
                 recorrente, tipo_recorrencia,
                 data_emissao, data_vencimento,
                 percentual_juros, percentual_multa,
                 status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                dados['fornecedor_id'],
                dados.get('tipo_servico_id'),
                dados.get('centro_custo_id'),
                dados.get('conta_contabil_id'),
                dados.get('filial_id'),
                f"{dados['descricao']} - Parcela {i}/{numero_parcelas}",
                dados.get('numero_documento'),
                dados.get('observacoes'),
                valor_parcela,
                numero_parcelas,
                i,
                dados.get('recorrente', False),
                dados.get('tipo_recorrencia'),
                dados['data_emissao'],
                data_vencimento,
                dados.get('percentual_juros', 0),
                dados.get('percentual_multa', 0),
                'pendente',
                dados.get('created_by')
            ))
        
        conn.commit()

    @staticmethod
    def get_all(fornecedor_id: Optional[int] = None, 
                filial_id: Optional[int] = None,
                status: Optional[str] = None,
                data_inicio: Optional[date] = None,
                data_fim: Optional[date] = None) -> List[Dict]:
        """Lista todas as contas a pagar com filtros opcionais"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT cp.*, 
                       f.razao_social as fornecedor_nome,
                       f.nome as fornecedor_fantasia,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       fil.nome as filial_nome
                FROM contas_pagar cp
                INNER JOIN fornecedores f ON cp.fornecedor_id = f.id
                LEFT JOIN tipos_servicos ts ON cp.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON cp.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON cp.conta_contabil_id = pc.id
                LEFT JOIN filiais fil ON cp.filial_id = fil.id
                WHERE 1=1
            """
            params = []
            
            if fornecedor_id:
                query += " AND cp.fornecedor_id = %s"
                params.append(fornecedor_id)
            
            if filial_id:
                query += " AND cp.filial_id = %s"
                params.append(filial_id)
            
            if status:
                query += " AND cp.status = %s"
                params.append(status)
            
            if data_inicio:
                query += " AND cp.data_vencimento >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND cp.data_vencimento <= %s"
                params.append(data_fim)
            
            query += " ORDER BY cp.data_vencimento ASC, cp.id DESC"
            
            cursor.execute(query, tuple(params))
            contas = cursor.fetchall()
            
            # Atualizar status de contas vencidas
            ContaPagarModel._atualizar_status_vencidas(conn)
            
            return contas

    @staticmethod
    def _atualizar_status_vencidas(conn):
        """Atualiza status de contas vencidas automaticamente"""
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contas_pagar 
            SET status = 'vencido'
            WHERE status = 'pendente' 
            AND data_vencimento < CURDATE()
        """)
        conn.commit()

    @staticmethod
    def get_by_id(conta_id: int) -> Optional[Dict]:
        """Busca uma conta por ID"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT cp.*, 
                       f.razao_social as fornecedor_nome,
                       f.nome as fornecedor_fantasia,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       fil.nome as filial_nome
                FROM contas_pagar cp
                INNER JOIN fornecedores f ON cp.fornecedor_id = f.id
                LEFT JOIN tipos_servicos ts ON cp.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON cp.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON cp.conta_contabil_id = pc.id
                LEFT JOIN filiais fil ON cp.filial_id = fil.id
                WHERE cp.id = %s
            """
            cursor.execute(query, (conta_id,))
            return cursor.fetchone()

    @staticmethod
    def baixar(conta_id: int, dados_baixa: Dict) -> Dict:
        """Realiza a baixa (pagamento) de uma conta"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Buscar conta
                cursor.execute("SELECT * FROM contas_pagar WHERE id = %s", (conta_id,))
                conta = cursor.fetchone()
                
                if not conta:
                    return {'success': False, 'message': 'Conta não encontrada'}
                
                if conta['status'] == 'pago':
                    return {'success': False, 'message': 'Conta já está paga'}
                
                # Validar conta bancária
                if not dados_baixa.get('conta_bancaria_id'):
                    return {'success': False, 'message': 'Conta bancária é obrigatória'}
                
                # Calcular juros e multa se houver atraso
                data_pagamento = datetime.strptime(dados_baixa['data_pagamento'], '%Y-%m-%d').date() if isinstance(dados_baixa['data_pagamento'], str) else dados_baixa['data_pagamento']
                data_vencimento = conta['data_vencimento']
                
                valor_juros = Decimal(str(dados_baixa.get('valor_juros', 0)))
                valor_multa = Decimal(str(dados_baixa.get('valor_multa', 0)))
                
                # Se não informado manualmente, calcular automaticamente
                if valor_juros == 0 and valor_multa == 0 and data_pagamento > data_vencimento:
                    dias_atraso = (data_pagamento - data_vencimento).days
                    
                    # Multa (uma vez)
                    if conta['percentual_multa'] > 0:
                        valor_multa = (Decimal(str(conta['valor_total'])) * Decimal(str(conta['percentual_multa']))) / 100
                    
                    # Juros (por dia)
                    if conta['percentual_juros'] > 0:
                        valor_juros = (Decimal(str(conta['valor_total'])) * Decimal(str(conta['percentual_juros'])) * dias_atraso) / 100
                
                # Aplicar desconto se houver
                valor_desconto = Decimal(str(dados_baixa.get('valor_desconto', 0)))
                
                # Valor total pago (pode ser informado manualmente ou calculado)
                if dados_baixa.get('valor_pago'):
                    valor_total_pago = Decimal(str(dados_baixa['valor_pago']))
                else:
                    valor_total_pago = Decimal(str(conta['valor_total'])) + valor_juros + valor_multa - valor_desconto
                
                # Atualizar conta
                query = """
                    UPDATE contas_pagar
                    SET status = 'pago',
                        conta_bancaria_id = %s,
                        data_pagamento = %s,
                        valor_pago = %s,
                        valor_juros = %s,
                        valor_multa = %s,
                        valor_desconto = %s
                    WHERE id = %s
                """
                
                cursor.execute(query, (
                    dados_baixa['conta_bancaria_id'],
                    data_pagamento,
                    valor_total_pago,
                    valor_juros,
                    valor_multa,
                    valor_desconto,
                    conta_id
                ))
                conn.commit()
                
                return {
                    'success': True, 
                    'message': 'Pagamento registrado com sucesso',
                    'valor_pago': float(valor_total_pago),
                    'valor_juros': float(valor_juros),
                    'valor_multa': float(valor_multa),
                    'valor_desconto': float(valor_desconto)
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def cancelar(conta_id: int) -> Dict:
        """Cancela uma conta a pagar"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contas_pagar SET status = 'cancelado' WHERE id = %s",
                    (conta_id,)
                )
                conn.commit()
                return {'success': True, 'message': 'Conta cancelada com sucesso'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_totalizadores(filtros: Dict = None) -> Dict:
        """Retorna totalizadores de contas a pagar"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query_base = "SELECT SUM(valor_total) as total FROM contas_pagar WHERE 1=1"
            params = []
            
            if filtros:
                if filtros.get('fornecedor_id'):
                    query_base += " AND fornecedor_id = %s"
                    params.append(filtros['fornecedor_id'])
                
                if filtros.get('filial_id'):
                    query_base += " AND filial_id = %s"
                    params.append(filtros['filial_id'])
            
            # Total pendente
            query_pendente = query_base + " AND status = 'pendente'"
            cursor.execute(query_pendente, tuple(params))
            total_pendente = cursor.fetchone()['total'] or 0
            
            # Total vencido
            query_vencido = query_base + " AND status = 'vencido'"
            cursor.execute(query_vencido, tuple(params))
            total_vencido = cursor.fetchone()['total'] or 0
            
            # Total pago
            query_pago = query_base + " AND status = 'pago'"
            cursor.execute(query_pago, tuple(params))
            total_pago = cursor.fetchone()['total'] or 0
            
            return {
                'total_pendente': float(total_pendente),
                'total_vencido': float(total_vencido),
                'total_pago': float(total_pago),
                'total_geral': float(total_pendente + total_vencido + total_pago)
            }
