"""
Model para gerenciamento de Capacity (operadores por cliente/produto)
"""
from database import DatabaseManager
from datetime import datetime
from decimal import Decimal

class CapacityModel:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_capacity_atual(self, cliente_id=None, produto_id=None, data_referencia=None):
        """
        Retorna o capacity atual de clientes/produtos
        Se data_referencia for informada, retorna o capacity válido naquela data
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            if data_referencia:
                # Busca capacity histórico para data específica
                query = """
                    SELECT 
                        ch.*,
                        c.nome as cliente_nome,
                        cp.nome as produto_nome
                    FROM capacity_historico ch
                    INNER JOIN clientes c ON ch.cliente_id = c.id
                    LEFT JOIN cliente_produtos cp ON ch.produto_id = cp.id
                    INNER JOIN (
                        SELECT 
                            cliente_id,
                            COALESCE(produto_id, 0) as produto_id,
                            MAX(data_vigencia) as max_data
                        FROM capacity_historico
                        WHERE data_vigencia <= %s
                        GROUP BY cliente_id, COALESCE(produto_id, 0)
                    ) latest ON ch.cliente_id = latest.cliente_id 
                        AND COALESCE(ch.produto_id, 0) = latest.produto_id 
                        AND ch.data_vigencia = latest.max_data
                    WHERE 1=1
                """
                params = [data_referencia]
            else:
                # Busca capacity mais recente (view otimizada)
                query = """
                    SELECT 
                        ch.*,
                        c.nome as cliente_nome,
                        cp.nome as produto_nome,
                        u.name as usuario_nome
                    FROM capacity_historico ch
                    INNER JOIN clientes c ON ch.cliente_id = c.id
                    LEFT JOIN cliente_produtos cp ON ch.produto_id = cp.id
                    LEFT JOIN users u ON ch.usuario_alteracao = u.id
                    INNER JOIN (
                        SELECT 
                            cliente_id,
                            COALESCE(produto_id, 0) as produto_id,
                            MAX(data_vigencia) as max_data
                        FROM capacity_historico
                        GROUP BY cliente_id, COALESCE(produto_id, 0)
                    ) latest ON ch.cliente_id = latest.cliente_id 
                        AND COALESCE(ch.produto_id, 0) = latest.produto_id 
                        AND ch.data_vigencia = latest.max_data
                    WHERE 1=1
                """
                params = []
            
            if cliente_id:
                query += " AND ch.cliente_id = %s"
                params.append(cliente_id)
            
            if produto_id:
                query += " AND ch.produto_id = %s"
                params.append(produto_id)
            
            query += " ORDER BY c.nome, cp.nome"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_clientes_com_produtos(self):
        """Retorna lista de clientes com seus produtos para interface de capacity"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Busca clientes
            cursor.execute("""
                SELECT 
                    id, 
                    nome, 
                    razao_social 
                FROM clientes 
                WHERE is_active = TRUE 
                ORDER BY nome
            """)
            clientes = cursor.fetchall()
            
            # Para cada cliente, busca produtos e capacity atual
            for cliente in clientes:
                cursor.execute("""
                    SELECT 
                        id, 
                        nome, 
                        descricao 
                    FROM cliente_produtos 
                    WHERE cliente_id = %s AND is_active = TRUE
                    ORDER BY nome
                """, (cliente['id'],))
                cliente['produtos'] = cursor.fetchall()
                
                # Busca capacity atual do cliente (sem produto)
                cursor.execute("""
                    SELECT 
                        capacity_atual,
                        capacity_necessario,
                        percentual_variacao,
                        data_vigencia
                    FROM capacity_historico
                    WHERE cliente_id = %s AND produto_id IS NULL
                    ORDER BY data_vigencia DESC
                    LIMIT 1
                """, (cliente['id'],))
                cliente['capacity'] = cursor.fetchone()
                
                # Busca capacity de cada produto
                for produto in cliente['produtos']:
                    cursor.execute("""
                        SELECT 
                            capacity_atual,
                            capacity_necessario,
                            percentual_variacao,
                            data_vigencia
                        FROM capacity_historico
                        WHERE cliente_id = %s AND produto_id = %s
                        ORDER BY data_vigencia DESC
                        LIMIT 1
                    """, (cliente['id'], produto['id']))
                    produto['capacity'] = cursor.fetchone()
            
            return clientes
    
    def salvar_capacity(self, cliente_id, produto_id, capacity_atual, capacity_necessario, 
                       data_vigencia, usuario_id, observacoes=None):
        """Salva novo registro de capacity"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO capacity_historico 
                (cliente_id, produto_id, capacity_atual, capacity_necessario, 
                 data_vigencia, usuario_alteracao, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                cliente_id,
                produto_id if produto_id else None,
                capacity_atual,
                capacity_necessario,
                data_vigencia,
                usuario_id,
                observacoes
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_historico(self, cliente_id, produto_id=None, limit=10):
        """Retorna histórico de alterações de capacity"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ch.*,
                    u.name as usuario_nome,
                    c.nome as cliente_nome,
                    cp.nome as produto_nome
                FROM capacity_historico ch
                INNER JOIN users u ON ch.usuario_alteracao = u.id
                INNER JOIN clientes c ON ch.cliente_id = c.id
                LEFT JOIN cliente_produtos cp ON ch.produto_id = cp.id
                WHERE ch.cliente_id = %s
            """
            
            params = [cliente_id]
            
            if produto_id:
                query += " AND ch.produto_id = %s"
                params.append(produto_id)
            else:
                query += " AND ch.produto_id IS NULL"
            
            query += " ORDER BY ch.data_vigencia DESC, ch.data_alteracao DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_total_capacity_por_periodo(self, data_inicio, data_fim):
        """Retorna total de capacity por cliente/produto em um período"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    ch.cliente_id,
                    ch.produto_id,
                    c.nome as cliente_nome,
                    cp.nome as produto_nome,
                    AVG(ch.capacity_atual) as capacity_medio,
                    MAX(ch.capacity_atual) as capacity_maximo,
                    MIN(ch.capacity_atual) as capacity_minimo
                FROM capacity_historico ch
                INNER JOIN clientes c ON ch.cliente_id = c.id
                LEFT JOIN cliente_produtos cp ON ch.produto_id = cp.id
                WHERE ch.data_vigencia BETWEEN %s AND %s
                GROUP BY ch.cliente_id, ch.produto_id, c.nome, cp.nome
                ORDER BY c.nome, cp.nome
            """
            
            cursor.execute(query, (data_inicio, data_fim))
            return cursor.fetchall()
    
    def calcular_rateio_por_capacity(self, competencia):
        """
        Calcula proporção de capacity de cada cliente/produto para rateio
        Retorna dicionário com cliente_id/produto_id como chave e % como valor
        """
        # Converte competencia MM/YYYY para primeiro dia do mês
        mes, ano = competencia.split('/')
        data_referencia = f"{ano}-{mes.zfill(2)}-01"
        
        capacities = self.get_capacity_atual(data_referencia=data_referencia)
        
        # Calcula total de capacity
        total_capacity = sum(c['capacity_atual'] for c in capacities)
        
        if total_capacity == 0:
            return {}
        
        # Calcula proporção de cada um
        rateios = {}
        for c in capacities:
            key = f"{c['cliente_id']}_{c['produto_id'] if c['produto_id'] else '0'}"
            rateios[key] = {
                'cliente_id': c['cliente_id'],
                'produto_id': c['produto_id'],
                'capacity': c['capacity_atual'],
                'percentual': round((c['capacity_atual'] / total_capacity) * 100, 2)
            }
        
        return rateios
