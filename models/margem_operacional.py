"""
Model para gerenciamento de Margem Operacional
Controla competências, rateios de receitas e despesas
"""
from database import DatabaseManager
from datetime import datetime
from decimal import Decimal
from models.capacity import CapacityModel

class MargemOperacionalModel:
    def __init__(self):
        self.db = DatabaseManager()
        self.capacity_model = CapacityModel()
    
    # ========== COMPETÊNCIAS ==========
    
    def get_competencias(self, status=None):
        """Lista todas as competências"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    mc.*,
                    ua.name as usuario_abertura_nome,
                    uf.name as usuario_fechamento_nome
                FROM margem_competencias mc
                LEFT JOIN users ua ON mc.usuario_abertura = ua.id
                LEFT JOIN users uf ON mc.usuario_fechamento = uf.id
                WHERE 1=1
            """
            params = []
            
            if status:
                query += " AND mc.status = %s"
                params.append(status)
            
            query += " ORDER BY mc.competencia DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_competencia(self, competencia_id):
        """Busca uma competência específica"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    mc.*,
                    ua.name as usuario_abertura_nome,
                    uf.name as usuario_fechamento_nome
                FROM margem_competencias mc
                LEFT JOIN users ua ON mc.usuario_abertura = ua.id
                LEFT JOIN users uf ON mc.usuario_fechamento = uf.id
                WHERE mc.id = %s
            """, (competencia_id,))
            
            return cursor.fetchone()
    
    def criar_competencia(self, competencia, usuario_id):
        """Cria nova competência (formato MM/YYYY)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO margem_competencias (competencia, usuario_abertura)
                VALUES (%s, %s)
            """, (competencia, usuario_id))
            
            conn.commit()
            return cursor.lastrowid
    
    def fechar_competencia(self, competencia_id, usuario_id):
        """Fecha uma competência (bloqueia alterações)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE margem_competencias 
                SET status = 'fechada',
                    data_fechamento = NOW(),
                    usuario_fechamento = %s
                WHERE id = %s
            """, (usuario_id, competencia_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def reabrir_competencia(self, competencia_id):
        """Reabre uma competência fechada"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE margem_competencias 
                SET status = 'aberta',
                    data_fechamento = NULL,
                    usuario_fechamento = NULL
                WHERE id = %s
            """, (competencia_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # ========== RECEITAS ==========
    
    def get_receitas_competencia(self, competencia):
        """Busca todas as receitas de uma competência"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    cr.*,
                    c.nome as cliente_nome,
                    c.id as cliente_id
                FROM contas_receber cr
                INNER JOIN clientes c ON cr.cliente_id = c.id
                WHERE cr.referencia = %s
                ORDER BY c.nome, cr.data_vencimento
            """, (competencia,))
            
            receitas = cursor.fetchall()
            
            # Para cada receita, busca produtos do cliente
            for receita in receitas:
                cursor.execute("""
                    SELECT id, nome, descricao
                    FROM cliente_produtos
                    WHERE cliente_id = %s AND is_active = TRUE
                    ORDER BY nome
                """, (receita['cliente_id'],))
                receita['produtos'] = cursor.fetchall()
            
            return receitas
    
    def get_rateios_receita(self, conta_receber_id, competencia_id):
        """Busca rateios existentes de uma receita"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    mrr.*,
                    c.nome as cliente_nome,
                    cp.nome as produto_nome
                FROM margem_rateio_receitas mrr
                INNER JOIN clientes c ON mrr.cliente_id = c.id
                LEFT JOIN cliente_produtos cp ON mrr.produto_id = cp.id
                WHERE mrr.conta_receber_id = %s 
                  AND mrr.competencia_id = %s
                ORDER BY mrr.id
            """, (conta_receber_id, competencia_id))
            
            return cursor.fetchall()
    
    def salvar_rateio_receita(self, competencia_id, conta_receber_id, cliente_id, 
                              produto_id, percentual, valor_rateado, usuario_id):
        """Salva rateio de receita"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO margem_rateio_receitas
                (competencia_id, conta_receber_id, cliente_id, produto_id,
                 percentual, valor_rateado, usuario_rateio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (competencia_id, conta_receber_id, cliente_id, 
                  produto_id if produto_id else None, percentual, valor_rateado, usuario_id))
            
            conn.commit()
            return cursor.lastrowid
    
    def limpar_rateios_receita(self, conta_receber_id, competencia_id):
        """Remove todos os rateios de uma receita para refazer"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM margem_rateio_receitas
                WHERE conta_receber_id = %s AND competencia_id = %s
            """, (conta_receber_id, competencia_id))
            
            conn.commit()
            return cursor.rowcount
    
    # ========== DESPESAS ==========
    
    def get_despesas_competencia(self, competencia):
        """Busca todas as despesas de uma competência"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    cp.*,
                    f.razao_social as fornecedor_nome,
                    ts.nome as tipo_servico,
                    ts.id as tipo_servico_id
                FROM contas_pagar cp
                INNER JOIN fornecedores f ON cp.fornecedor_id = f.id
                LEFT JOIN tipos_servicos ts ON cp.tipo_servico_id = ts.id
                WHERE cp.referencia = %s
                ORDER BY f.razao_social, cp.data_vencimento
            """, (competencia,))
            
            return cursor.fetchall()
    
    def get_rateios_despesa(self, conta_pagar_id, competencia_id):
        """Busca rateios existentes de uma despesa"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    mrd.*,
                    c.nome as cliente_nome,
                    cp.nome as produto_nome
                FROM margem_rateio_despesas mrd
                INNER JOIN clientes c ON mrd.cliente_id = c.id
                LEFT JOIN cliente_produtos cp ON mrd.produto_id = cp.id
                WHERE mrd.conta_pagar_id = %s 
                  AND mrd.competencia_id = %s
                ORDER BY mrd.id
            """, (conta_pagar_id, competencia_id))
            
            return cursor.fetchall()
    
    def salvar_rateio_despesa(self, competencia_id, conta_pagar_id, cliente_id, 
                              produto_id, tipo_rateio, percentual, valor_rateado, 
                              usuario_id, observacoes=None):
        """Salva rateio de despesa"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO margem_rateio_despesas
                (competencia_id, conta_pagar_id, cliente_id, produto_id,
                 tipo_rateio, percentual, valor_rateado, usuario_rateio, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (competencia_id, conta_pagar_id, cliente_id, 
                  produto_id if produto_id else None, tipo_rateio, 
                  percentual, valor_rateado, usuario_id, observacoes))
            
            conn.commit()
            return cursor.lastrowid
    
    def limpar_rateios_despesa(self, conta_pagar_id, competencia_id):
        """Remove todos os rateios de uma despesa para refazer"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM margem_rateio_despesas
                WHERE conta_pagar_id = %s AND competencia_id = %s
            """, (conta_pagar_id, competencia_id))
            
            conn.commit()
            return cursor.rowcount
    
    def aplicar_rateio_automatico_capacity(self, competencia_id, conta_pagar_id, 
                                           valor_total, competencia, usuario_id):
        """Aplica rateio automático de despesa usando proporção de capacity"""
        # Limpa rateios anteriores
        self.limpar_rateios_despesa(conta_pagar_id, competencia_id)
        
        # Busca proporções de capacity
        rateios_capacity = self.capacity_model.calcular_rateio_por_capacity(competencia)
        
        if not rateios_capacity:
            return False
        
        # Aplica rateio proporcional
        valor_rateado_total = Decimal('0')
        
        for key, rateio in rateios_capacity.items():
            valor_rateado = (Decimal(str(valor_total)) * Decimal(str(rateio['percentual']))) / Decimal('100')
            valor_rateado = valor_rateado.quantize(Decimal('0.01'))
            valor_rateado_total += valor_rateado
            
            self.salvar_rateio_despesa(
                competencia_id=competencia_id,
                conta_pagar_id=conta_pagar_id,
                cliente_id=rateio['cliente_id'],
                produto_id=rateio['produto_id'],
                tipo_rateio='capacity',
                percentual=rateio['percentual'],
                valor_rateado=float(valor_rateado),
                usuario_id=usuario_id,
                observacoes='Rateio automático por capacity'
            )
        
        # Ajuste de arredondamento no último registro se necessário
        diferenca = Decimal(str(valor_total)) - valor_rateado_total
        if diferenca != 0:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE margem_rateio_despesas
                    SET valor_rateado = valor_rateado + %s
                    WHERE conta_pagar_id = %s AND competencia_id = %s
                    ORDER BY id DESC
                    LIMIT 1
                """, (float(diferenca), conta_pagar_id, competencia_id))
                conn.commit()
        
        return True
    
    # ========== DASHBOARD / RELATÓRIOS ==========
    
    def get_resumo_margem(self, competencia=None, ano=None):
        """
        Retorna resumo de margem operacional
        Se competencia informada: retorna apenas aquele mês
        Se ano informado: retorna todos os meses do ano
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            if competencia:
                # Busca apenas uma competência
                cursor.execute("""
                    SELECT * FROM vw_margem_resumo
                    WHERE competencia = %s
                    ORDER BY cliente_nome, produto_nome
                """, (competencia,))
                
                return cursor.fetchall()
            
            elif ano:
                # Busca todas as competências do ano
                cursor.execute("""
                    SELECT * FROM vw_margem_resumo
                    WHERE competencia LIKE %s
                    ORDER BY competencia, cliente_nome, produto_nome
                """, (f'%/{ano}',))
                
                return cursor.fetchall()
            
            else:
                # Retorna tudo
                cursor.execute("SELECT * FROM vw_margem_resumo ORDER BY competencia DESC, cliente_nome, produto_nome")
                return cursor.fetchall()
    
    def get_detalhamento_despesas(self, competencia_id, cliente_id=None, produto_id=None):
        """Retorna detalhamento de despesas por tipo de serviço"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ts.nome as tipo_servico,
                    ts.categoria,
                    cp.descricao as subtipo,
                    SUM(mrd.valor_rateado) as total
                FROM margem_rateio_despesas mrd
                INNER JOIN contas_pagar cp ON mrd.conta_pagar_id = cp.id
                LEFT JOIN tipos_servicos ts ON cp.tipo_servico_id = ts.id
                WHERE mrd.competencia_id = %s
            """
            
            params = [competencia_id]
            
            if cliente_id:
                query += " AND mrd.cliente_id = %s"
                params.append(cliente_id)
            
            if produto_id:
                query += " AND mrd.produto_id = %s"
                params.append(produto_id)
            
            query += " GROUP BY ts.nome, ts.categoria, cp.descricao ORDER BY ts.nome, cp.descricao"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_status_rateio_competencia(self, competencia_id):
        """Retorna estatísticas de progresso de rateio de uma competência"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Busca competência
            competencia = self.get_competencia(competencia_id)['competencia']
            
            # Total de receitas no período
            cursor.execute("""
                SELECT COUNT(*) as total, COALESCE(SUM(valor_total), 0) as valor_total
                FROM contas_receber
                WHERE referencia = %s
            """, (competencia,))
            receitas_total = cursor.fetchone()
            
            # Receitas já rateadas
            cursor.execute("""
                SELECT COUNT(DISTINCT conta_receber_id) as total, COALESCE(SUM(valor_rateado), 0) as valor_rateado
                FROM margem_rateio_receitas
                WHERE competencia_id = %s
            """, (competencia_id,))
            receitas_rateadas = cursor.fetchone()
            
            # Total de despesas no período
            cursor.execute("""
                SELECT COUNT(*) as total, COALESCE(SUM(valor_total), 0) as valor_total
                FROM contas_pagar
                WHERE referencia = %s
            """, (competencia,))
            despesas_total = cursor.fetchone()
            
            # Despesas já rateadas
            cursor.execute("""
                SELECT COUNT(DISTINCT conta_pagar_id) as total, COALESCE(SUM(valor_rateado), 0) as valor_rateado
                FROM margem_rateio_despesas
                WHERE competencia_id = %s
            """, (competencia_id,))
            despesas_rateadas = cursor.fetchone()
            
            return {
                'receitas': {
                    'total': receitas_total['total'],
                    'rateadas': receitas_rateadas['total'],
                    'percentual': round((receitas_rateadas['total'] / receitas_total['total'] * 100) if receitas_total['total'] > 0 else 0, 2),
                    'valor_total': float(receitas_total['valor_total']),
                    'valor_rateado': float(receitas_rateadas['valor_rateado'])
                },
                'despesas': {
                    'total': despesas_total['total'],
                    'rateadas': despesas_rateadas['total'],
                    'percentual': round((despesas_rateadas['total'] / despesas_total['total'] * 100) if despesas_total['total'] > 0 else 0, 2),
                    'valor_total': float(despesas_total['valor_total']),
                    'valor_rateado': float(despesas_rateadas['valor_rateado'])
                }
            }
