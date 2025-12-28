"""
Modelo para gerenciar Rateio de Contas a Receber entre Produtos de Cliente
"""
from typing import List, Dict, Optional
from database import DatabaseManager

class RateioModel:
    """Operações CRUD para rateio de receitas"""

    @staticmethod
    def create_rateio(conta_receber_id: int, rateios: List[Dict], created_by: int = None) -> Dict:
        """
        Cria rateio de uma conta a receber entre produtos do cliente
        
        Args:
            conta_receber_id: ID da conta a receber
            rateios: Lista de dicts com {cliente_produto_id, tipo_rateio, percentual, valor_fixo}
            created_by: ID do usuário que criou
            
        Returns:
            Dict com success e message
        """
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Buscar conta a receber
                cursor.execute("SELECT * FROM contas_receber WHERE id = %s", (conta_receber_id,))
                conta = cursor.fetchone()
                
                if not conta:
                    return {'success': False, 'message': 'Conta a receber não encontrada'}
                
                if conta.get('is_rateada'):
                    return {'success': False, 'message': 'Esta conta já foi rateada'}
                
                valor_total = float(conta['valor_total'])
                
                # Validar rateio
                validacao = RateioModel._validar_rateio(rateios, valor_total)
                if not validacao['success']:
                    return validacao
                
                # Limpar rateios anteriores (se houver)
                cursor.execute("DELETE FROM contas_receber_rateio WHERE conta_receber_id = %s", (conta_receber_id,))
                
                # Inserir rateios
                for r in rateios:
                    tipo = r.get('tipo_rateio', 'percentual')
                    percentual = r.get('percentual') if tipo == 'percentual' else None
                    valor_fixo = r.get('valor_fixo') if tipo == 'valor' else None
                    
                    # Calcular valor rateado
                    if tipo == 'percentual':
                        valor_rateado = valor_total * (float(percentual) / 100)
                    else:
                        valor_rateado = float(valor_fixo)
                    
                    cursor.execute("""
                        INSERT INTO contas_receber_rateio 
                        (conta_receber_id, cliente_produto_id, tipo_rateio, percentual, valor_fixo, valor_rateado, observacoes, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        conta_receber_id,
                        r['cliente_produto_id'],
                        tipo,
                        percentual,
                        valor_fixo,
                        valor_rateado,
                        r.get('observacoes'),
                        created_by
                    ))
                
                # Marcar conta como rateada
                cursor.execute("UPDATE contas_receber SET is_rateada = TRUE WHERE id = %s", (conta_receber_id,))
                
                conn.commit()
                return {'success': True, 'message': 'Rateio criado com sucesso'}
                
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar rateio: {str(e)}'}

    @staticmethod
    def _validar_rateio(rateios: List[Dict], valor_total: float) -> Dict:
        """Valida se o rateio está correto"""
        if not rateios:
            return {'success': False, 'message': 'Nenhum produto informado para rateio'}
        
        # Verificar tipo do primeiro (todos devem ser iguais)
        tipo = rateios[0].get('tipo_rateio', 'percentual')
        
        if tipo == 'percentual':
            soma_percentuais = sum(float(r.get('percentual', 0)) for r in rateios)
            if abs(soma_percentuais - 100) > 0.01:  # Tolerância de 0.01%
                return {'success': False, 'message': f'Soma dos percentuais deve ser 100%. Atual: {soma_percentuais}%'}
        else:  # valor
            soma_valores = sum(float(r.get('valor_fixo', 0)) for r in rateios)
            if abs(soma_valores - valor_total) > 0.01:  # Tolerância de 1 centavo
                return {'success': False, 'message': f'Soma dos valores deve ser R$ {valor_total:.2f}. Atual: R$ {soma_valores:.2f}'}
        
        return {'success': True}

    @staticmethod
    def get_rateio_by_conta(conta_receber_id: int) -> List[Dict]:
        """Busca o rateio de uma conta a receber"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    r.*,
                    cp.nome as produto_nome,
                    cp.codigo as produto_codigo
                FROM contas_receber_rateio r
                JOIN cliente_produtos cp ON cp.id = r.cliente_produto_id
                WHERE r.conta_receber_id = %s
                ORDER BY r.id
            """, (conta_receber_id,))
            return cursor.fetchall()

    @staticmethod
    def delete_rateio(conta_receber_id: int) -> Dict:
        """Remove o rateio de uma conta a receber"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM contas_receber_rateio WHERE conta_receber_id = %s", (conta_receber_id,))
                cursor.execute("UPDATE contas_receber SET is_rateada = FALSE WHERE id = %s", (conta_receber_id,))
                
                conn.commit()
                return {'success': True, 'message': 'Rateio removido com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao remover rateio: {str(e)}'}

    @staticmethod
    def get_receitas_por_produto(cliente_id: int = None, produto_id: int = None, data_inicio = None, data_fim = None) -> List[Dict]:
        """
        Retorna receitas agrupadas por produto (diretas + rateadas)
        """
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            where_clauses = []
            params = []
            
            if cliente_id:
                where_clauses.append("c.id = %s")
                params.append(cliente_id)
            if produto_id:
                where_clauses.append("cp.id = %s")
                params.append(produto_id)
            if data_inicio:
                where_clauses.append("cr.data_emissao >= %s")
                params.append(data_inicio)
            if data_fim:
                where_clauses.append("cr.data_emissao <= %s")
                params.append(data_fim)
            
            where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            # Receitas diretas (com produto definido)
            query_diretas = f"""
                SELECT 
                    c.id as cliente_id,
                    c.nome as cliente_nome,
                    cp.id as produto_id,
                    cp.nome as produto_nome,
                    cp.codigo as produto_codigo,
                    SUM(cr.valor_total) as receita_total,
                    'direta' as tipo_receita
                FROM contas_receber cr
                JOIN clientes c ON c.id = cr.cliente_id
                JOIN cliente_produtos cp ON cp.id = cr.cliente_produto_id
                {where_sql}
                AND cr.is_rateada = FALSE 
                AND cr.cliente_produto_id IS NOT NULL
                AND cr.status = 'recebido'
                GROUP BY c.id, cp.id
            """
            
            # Receitas rateadas
            query_rateadas = f"""
                SELECT 
                    c.id as cliente_id,
                    c.nome as cliente_nome,
                    cp.id as produto_id,
                    cp.nome as produto_nome,
                    cp.codigo as produto_codigo,
                    SUM(crr.valor_rateado) as receita_total,
                    'rateada' as tipo_receita
                FROM contas_receber_rateio crr
                JOIN contas_receber cr ON cr.id = crr.conta_receber_id
                JOIN clientes c ON c.id = cr.cliente_id
                JOIN cliente_produtos cp ON cp.id = crr.cliente_produto_id
                {where_sql}
                AND cr.status = 'recebido'
                GROUP BY c.id, cp.id
            """
            
            query_final = f"{query_diretas} UNION ALL {query_rateadas}"
            
            cursor.execute(query_final, params + params)  # params duplicados para as duas queries
            return cursor.fetchall()
