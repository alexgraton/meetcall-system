"""
Modelo para conciliação bancária
"""
from database import DatabaseManager
from datetime import datetime, timedelta
from decimal import Decimal
from difflib import SequenceMatcher


class Conciliacao:
    """Modelo para conciliação bancária"""
    
    @staticmethod
    def criar_conciliacao(conta_bancaria_id, nome_arquivo, transacoes, user_id=None):
        """
        Cria um novo registro de conciliação e importa transações
        
        Args:
            conta_bancaria_id: ID da conta bancária
            nome_arquivo: Nome do arquivo importado
            transacoes: Lista de transações do extrato
            user_id: ID do usuário que fez a importação
            
        Returns:
            ID da conciliação criada
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Calcular período
            datas = [t['data_transacao'] for t in transacoes]
            periodo_inicio = min(datas)
            periodo_fim = max(datas)
            
            # Criar registro de conciliação
            cursor.execute("""
                INSERT INTO conciliacoes_bancarias 
                (conta_bancaria_id, nome_arquivo, data_importacao, periodo_inicio, periodo_fim, 
                 total_transacoes, total_pendentes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (conta_bancaria_id, nome_arquivo, datetime.now(), periodo_inicio, periodo_fim,
                  len(transacoes), len(transacoes), 'processando'))
            
            conciliacao_id = cursor.lastrowid
            
            # Inserir transações do extrato
            for trans in transacoes:
                cursor.execute("""
                    INSERT INTO transacoes_extrato
                    (conciliacao_id, data_transacao, descricao, documento, valor, tipo, 
                     saldo_apos, status_conciliacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (conciliacao_id, trans['data_transacao'], trans['descricao'], 
                      trans.get('documento', ''), trans['valor'], trans['tipo'],
                      trans.get('saldo_apos'), 'pendente'))
            
            # Atualizar status
            cursor.execute("""
                UPDATE conciliacoes_bancarias 
                SET status = 'concluida'
                WHERE id = %s
            """, (conciliacao_id,))
            
            conn.commit()
            cursor.close()
            
            return conciliacao_id
    
    @staticmethod
    def buscar_matches_automaticos(conciliacao_id, tolerancia_dias=3, tolerancia_valor=0.01):
        """
        Busca matches automáticos entre transações do extrato e do sistema
        
        Args:
            conciliacao_id: ID da conciliação
            tolerancia_dias: Diferença máxima de dias entre as datas
            tolerancia_valor: Diferença máxima percentual no valor (0.01 = 1%)
            
        Returns:
            Lista de matches encontrados
        """
        db = DatabaseManager()
        matches = []
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar transações pendentes do extrato
            cursor.execute("""
                SELECT * FROM transacoes_extrato
                WHERE conciliacao_id = %s AND status_conciliacao = 'pendente'
                ORDER BY data_transacao
            """, (conciliacao_id,))
            
            transacoes_extrato = cursor.fetchall()
            
            for trans in transacoes_extrato:
                data_min = trans['data_transacao'] - timedelta(days=tolerancia_dias)
                data_max = trans['data_transacao'] + timedelta(days=tolerancia_dias)
                valor_min = float(trans['valor']) * (1 - tolerancia_valor)
                valor_max = float(trans['valor']) * (1 + tolerancia_valor)
                
                candidatos = []
                
                # Buscar em contas a pagar (débitos)
                if trans['tipo'] == 'debito':
                    cursor.execute("""
                        SELECT 
                            id, 
                            'contas_pagar' as tipo_transacao,
                            fornecedor_id as entidade_id,
                            descricao,
                            numero_documento as documento,
                            data_pagamento as data_transacao,
                            (valor_total - valor_desconto + valor_juros + valor_multa) as valor,
                            conciliado
                        FROM contas_pagar
                        WHERE status = 'paga'
                        AND conciliado = 0
                        AND data_pagamento BETWEEN %s AND %s
                        AND (valor_total - valor_desconto + valor_juros + valor_multa) BETWEEN %s AND %s
                    """, (data_min, data_max, valor_min, valor_max))
                    
                    candidatos.extend(cursor.fetchall())
                
                # Buscar em contas a receber (créditos)
                elif trans['tipo'] == 'credito':
                    cursor.execute("""
                        SELECT 
                            id,
                            'contas_receber' as tipo_transacao,
                            cliente_id as entidade_id,
                            descricao,
                            numero_documento as documento,
                            data_recebimento as data_transacao,
                            (valor_total - valor_desconto + valor_juros + valor_multa) as valor,
                            conciliado
                        FROM contas_receber
                        WHERE status = 'recebida'
                        AND conciliado = 0
                        AND data_recebimento BETWEEN %s AND %s
                        AND (valor_total - valor_desconto + valor_juros + valor_multa) BETWEEN %s AND %s
                    """, (data_min, data_max, valor_min, valor_max))
                    
                    candidatos.extend(cursor.fetchall())
                
                # Buscar em lançamentos manuais
                cursor.execute("""
                    SELECT 
                        id,
                        'lancamento_manual' as tipo_transacao,
                        NULL as entidade_id,
                        descricao,
                        '' as documento,
                        data_lancamento as data_transacao,
                        valor,
                        conciliado
                    FROM lancamentos_manuais
                    WHERE conciliado = 0
                    AND data_lancamento BETWEEN %s AND %s
                    AND valor BETWEEN %s AND %s
                    AND tipo = %s
                """, (data_min, data_max, valor_min, valor_max, 
                      'despesa' if trans['tipo'] == 'debito' else 'receita'))
                
                candidatos.extend(cursor.fetchall())
                
                # Calcular similaridade para cada candidato
                for cand in candidatos:
                    # Similaridade por descrição
                    sim_descricao = SequenceMatcher(None, 
                                                    trans['descricao'].lower(), 
                                                    cand['descricao'].lower()).ratio() * 100
                    
                    # Similaridade por documento (se tiver)
                    sim_documento = 0
                    if trans.get('documento') and cand.get('documento'):
                        sim_documento = SequenceMatcher(None,
                                                       str(trans['documento']).lower(),
                                                       str(cand['documento']).lower()).ratio() * 100
                    
                    # Similaridade por valor (quanto mais próximo, maior a similaridade)
                    diff_valor = abs(float(trans['valor']) - float(cand['valor']))
                    sim_valor = max(0, 100 - (diff_valor / float(trans['valor']) * 100))
                    
                    # Similaridade por data
                    diff_dias = abs((trans['data_transacao'] - cand['data_transacao']).days)
                    sim_data = max(0, 100 - (diff_dias * 20))
                    
                    # Calcular similaridade total (média ponderada)
                    similaridade_total = (
                        sim_descricao * 0.4 +
                        sim_valor * 0.3 +
                        sim_data * 0.2 +
                        sim_documento * 0.1
                    )
                    
                    # Adicionar ao match se similaridade >= 60%
                    if similaridade_total >= 60:
                        matches.append({
                            'transacao_extrato_id': trans['id'],
                            'transacao_extrato': trans,
                            'transacao_sistema_id': cand['id'],
                            'transacao_sistema_tipo': cand['tipo_transacao'],
                            'transacao_sistema': cand,
                            'similaridade': round(similaridade_total, 2),
                            'sim_descricao': round(sim_descricao, 2),
                            'sim_valor': round(sim_valor, 2),
                            'sim_data': round(sim_data, 2),
                            'sim_documento': round(sim_documento, 2)
                        })
            
            cursor.close()
        
        # Ordenar por similaridade (maior primeiro)
        matches.sort(key=lambda x: x['similaridade'], reverse=True)
        
        return matches
    
    @staticmethod
    def conciliar_transacao(transacao_extrato_id, tipo_transacao, transacao_id, user_id):
        """
        Concilia uma transação do extrato com uma transação do sistema
        
        Args:
            transacao_extrato_id: ID da transação do extrato
            tipo_transacao: 'contas_pagar', 'contas_receber' ou 'lancamento_manual'
            transacao_id: ID da transação do sistema
            user_id: ID do usuário que fez a conciliação
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Atualizar transação do extrato
            cursor.execute("""
                UPDATE transacoes_extrato
                SET status_conciliacao = 'conciliada',
                    transacao_relacionada_tipo = %s,
                    transacao_relacionada_id = %s,
                    conciliado_em = %s,
                    conciliado_por = %s
                WHERE id = %s
            """, (tipo_transacao, transacao_id, datetime.now(), user_id, transacao_extrato_id))
            
            # Atualizar transação do sistema
            tabela = tipo_transacao if tipo_transacao != 'lancamento_manual' else 'lancamentos_manuais'
            cursor.execute(f"""
                UPDATE {tabela}
                SET conciliado = 1,
                    conciliacao_data = %s,
                    transacao_extrato_id = %s
                WHERE id = %s
            """, (datetime.now(), transacao_extrato_id, transacao_id))
            
            # Atualizar contadores da conciliação
            cursor.execute("""
                UPDATE conciliacoes_bancarias c
                SET total_conciliadas = (
                    SELECT COUNT(*) FROM transacoes_extrato 
                    WHERE conciliacao_id = c.id AND status_conciliacao = 'conciliada'
                ),
                total_pendentes = (
                    SELECT COUNT(*) FROM transacoes_extrato 
                    WHERE conciliacao_id = c.id AND status_conciliacao = 'pendente'
                )
                WHERE id = (
                    SELECT conciliacao_id FROM transacoes_extrato WHERE id = %s
                )
            """, (transacao_extrato_id,))
            
            conn.commit()
            cursor.close()
    
    @staticmethod
    def desconciliar_transacao(transacao_extrato_id):
        """Remove conciliação de uma transação"""
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar informações da conciliação
            cursor.execute("""
                SELECT transacao_relacionada_tipo, transacao_relacionada_id
                FROM transacoes_extrato
                WHERE id = %s
            """, (transacao_extrato_id,))
            
            info = cursor.fetchone()
            
            if info and info['transacao_relacionada_id']:
                # Remover flag de conciliado da transação do sistema
                tabela = info['transacao_relacionada_tipo']
                if tabela == 'lancamento_manual':
                    tabela = 'lancamentos_manuais'
                
                cursor.execute(f"""
                    UPDATE {tabela}
                    SET conciliado = 0,
                        conciliacao_data = NULL,
                        transacao_extrato_id = NULL
                    WHERE id = %s
                """, (info['transacao_relacionada_id'],))
            
            # Atualizar transação do extrato
            cursor.execute("""
                UPDATE transacoes_extrato
                SET status_conciliacao = 'pendente',
                    transacao_relacionada_tipo = NULL,
                    transacao_relacionada_id = NULL,
                    similaridade = NULL,
                    conciliado_em = NULL,
                    conciliado_por = NULL
                WHERE id = %s
            """, (transacao_extrato_id,))
            
            # Atualizar contadores
            cursor.execute("""
                UPDATE conciliacoes_bancarias c
                SET total_conciliadas = (
                    SELECT COUNT(*) FROM transacoes_extrato 
                    WHERE conciliacao_id = c.id AND status_conciliacao = 'conciliada'
                ),
                total_pendentes = (
                    SELECT COUNT(*) FROM transacoes_extrato 
                    WHERE conciliacao_id = c.id AND status_conciliacao = 'pendente'
                )
                WHERE id = (
                    SELECT conciliacao_id FROM transacoes_extrato WHERE id = %s
                )
            """, (transacao_extrato_id,))
            
            conn.commit()
            cursor.close()
    
    @staticmethod
    def listar_conciliacoes(conta_bancaria_id=None, limit=50):
        """Lista conciliações realizadas"""
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    c.*,
                    cb.banco,
                    cb.agencia,
                    cb.conta,
                    cb.nome as conta_nome
                FROM conciliacoes_bancarias c
                INNER JOIN contas_bancarias cb ON c.conta_bancaria_id = cb.id
            """
            params = []
            
            if conta_bancaria_id:
                query += " WHERE c.conta_bancaria_id = %s"
                params.append(conta_bancaria_id)
            
            query += " ORDER BY c.data_importacao DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            conciliacoes = cursor.fetchall()
            cursor.close()
            
            return conciliacoes
    
    @staticmethod
    def get_detalhes_conciliacao(conciliacao_id):
        """Retorna detalhes de uma conciliação específica"""
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar conciliação
            cursor.execute("""
                SELECT 
                    c.*,
                    cb.banco,
                    cb.agencia,
                    cb.conta,
                    cb.nome as conta_nome
                FROM conciliacoes_bancarias c
                INNER JOIN contas_bancarias cb ON c.conta_bancaria_id = cb.id
                WHERE c.id = %s
            """, (conciliacao_id,))
            
            conciliacao = cursor.fetchone()
            
            if not conciliacao:
                return None
            
            # Buscar transações
            cursor.execute("""
                SELECT * FROM transacoes_extrato
                WHERE conciliacao_id = %s
                ORDER BY data_transacao DESC, id DESC
            """, (conciliacao_id,))
            
            conciliacao['transacoes'] = cursor.fetchall()
            cursor.close()
            
            return conciliacao
