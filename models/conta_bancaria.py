"""
Model para Contas Bancárias
Gerencia contas correntes, poupança e caixa da empresa
"""

from decimal import Decimal
from database import DatabaseManager

class ContaBancariaModel:
    """Modelo para gerenciar contas bancárias"""
    
    @staticmethod
    def create(dados):
        """
        Cria uma nova conta bancária
        
        Args:
            dados (dict): Dicionário com os dados da conta
                - banco (str): Nome do banco
                - agencia (str): Número da agência
                - numero_conta (str): Número da conta
                - tipo_conta (str): Tipo (corrente, poupanca, caixa)
                - descricao (str): Descrição opcional
                - saldo_inicial (Decimal): Saldo inicial
                - filial_id (int): ID da filial (opcional)
                - moeda (str): Código da moeda (default: BRL)
        
        Returns:
            int: ID da conta criada
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Saldo inicial = saldo atual ao criar
            saldo = dados.get('saldo_inicial', Decimal('0'))
            
            sql = """
                INSERT INTO contas_bancarias (
                    banco, agencia, numero_conta, tipo_conta, descricao,
                    saldo_inicial, saldo_atual, moeda, filial_id, ativo
                ) VALUES (
                    %(banco)s, %(agencia)s, %(numero_conta)s, %(tipo_conta)s, %(descricao)s,
                    %(saldo_inicial)s, %(saldo_atual)s, %(moeda)s, %(filial_id)s, %(ativo)s
                )
            """
            
            params = {
                'banco': dados['banco'],
                'agencia': dados['agencia'],
                'numero_conta': dados['numero_conta'],
                'tipo_conta': dados.get('tipo_conta', 'corrente'),
                'descricao': dados.get('descricao'),
                'saldo_inicial': saldo,
                'saldo_atual': saldo,
                'moeda': dados.get('moeda', 'BRL'),
                'filial_id': dados.get('filial_id'),
                'ativo': dados.get('ativo', 1)
            }
            
            cursor.execute(sql, params)
            conn.commit()
            
            return cursor.lastrowid
    
    @staticmethod
    def get_all(filtros=None):
        """
        Retorna todas as contas bancárias com filtros opcionais
        
        Args:
            filtros (dict): Filtros opcionais
                - filial_id (int): Filtrar por filial
                - tipo_conta (str): Filtrar por tipo
                - ativo (bool): Filtrar por status ativo/inativo
        
        Returns:
            list: Lista de contas bancárias
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    cb.*,
                    f.nome as filial_nome
                FROM contas_bancarias cb
                LEFT JOIN filiais f ON cb.filial_id = f.id
                WHERE 1=1
            """
            
            params = {}
            
            if filtros:
                if filtros.get('filial_id'):
                    sql += " AND cb.filial_id = %(filial_id)s"
                    params['filial_id'] = filtros['filial_id']
                
                if filtros.get('tipo_conta'):
                    sql += " AND cb.tipo_conta = %(tipo_conta)s"
                    params['tipo_conta'] = filtros['tipo_conta']
                
                if 'ativo' in filtros:
                    sql += " AND cb.ativo = %(ativo)s"
                    params['ativo'] = 1 if filtros['ativo'] else 0
            
            sql += " ORDER BY cb.banco, cb.agencia, cb.numero_conta"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(conta_id):
        """
        Retorna uma conta bancária por ID
        
        Args:
            conta_id (int): ID da conta
        
        Returns:
            dict: Dados da conta ou None
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    cb.*,
                    f.nome as filial_nome
                FROM contas_bancarias cb
                LEFT JOIN filiais f ON cb.filial_id = f.id
                WHERE cb.id = %s
            """
            
            cursor.execute(sql, (conta_id,))
            return cursor.fetchone()
    
    @staticmethod
    def update(conta_id, dados):
        """
        Atualiza dados de uma conta bancária
        
        Args:
            conta_id (int): ID da conta
            dados (dict): Dados para atualizar
        
        Returns:
            bool: True se atualizado com sucesso
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            campos_atualizaveis = ['banco', 'agencia', 'numero_conta', 'tipo_conta', 
                                   'descricao', 'filial_id', 'moeda', 'ativo']
            
            set_clause = []
            params = {}
            
            for campo in campos_atualizaveis:
                if campo in dados:
                    set_clause.append(f"{campo} = %({campo})s")
                    params[campo] = dados[campo]
            
            if not set_clause:
                return False
            
            params['conta_id'] = conta_id
            
            sql = f"""
                UPDATE contas_bancarias
                SET {', '.join(set_clause)}
                WHERE id = %(conta_id)s
            """
            
            cursor.execute(sql, params)
            conn.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(conta_id):
        """
        Desativa uma conta bancária (soft delete)
        
        Args:
            conta_id (int): ID da conta
        
        Returns:
            bool: True se desativada com sucesso
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = "UPDATE contas_bancarias SET ativo = 0 WHERE id = %s"
            cursor.execute(sql, (conta_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    def debitar(conta_id, valor):
        """
        Debita valor da conta bancária (para pagamentos)
        
        Args:
            conta_id (int): ID da conta bancária
            valor (Decimal): Valor a debitar
        
        Returns:
            bool: True se debitado com sucesso
        
        Raises:
            ValueError: Se conta não existir ou saldo insuficiente
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar saldo atual
            cursor.execute("SELECT saldo_atual FROM contas_bancarias WHERE id = %s AND ativo = 1", (conta_id,))
            conta = cursor.fetchone()
            
            if not conta:
                raise ValueError(f"Conta bancária {conta_id} não encontrada ou inativa")
            
            saldo_atual = Decimal(str(conta['saldo_atual']))
            valor_decimal = Decimal(str(valor))
            novo_saldo = saldo_atual - valor_decimal
            
            # Atualizar saldo
            cursor.execute(
                "UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s",
                (novo_saldo, conta_id)
            )
            conn.commit()
            
            return True
    
    @staticmethod
    def creditar(conta_id, valor):
        """
        Credita valor na conta bancária (para recebimentos)
        
        Args:
            conta_id (int): ID da conta bancária
            valor (Decimal): Valor a creditar
        
        Returns:
            bool: True se creditado com sucesso
        
        Raises:
            ValueError: Se conta não existir
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar saldo atual
            cursor.execute("SELECT saldo_atual FROM contas_bancarias WHERE id = %s AND ativo = 1", (conta_id,))
            conta = cursor.fetchone()
            
            if not conta:
                raise ValueError(f"Conta bancária {conta_id} não encontrada ou inativa")
            
            saldo_atual = Decimal(str(conta['saldo_atual']))
            valor_decimal = Decimal(str(valor))
            novo_saldo = saldo_atual + valor_decimal
            
            # Atualizar saldo
            cursor.execute(
                "UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s",
                (novo_saldo, conta_id)
            )
            conn.commit()
            
            return True
    
    @staticmethod
    def ajustar_saldo(conta_id, valor, operacao='credito', descricao=None):
        """
        Ajusta o saldo de uma conta bancária
        
        Args:
            conta_id (int): ID da conta
            valor (Decimal): Valor do ajuste
            operacao (str): 'credito' (adicionar) ou 'debito' (subtrair)
            descricao (str): Descrição do ajuste
        
        Returns:
            dict: Novo saldo ou None se erro
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar saldo atual
            cursor.execute("SELECT saldo_atual FROM contas_bancarias WHERE id = %s", (conta_id,))
            conta = cursor.fetchone()
            
            if not conta:
                return None
            
            saldo_atual = Decimal(str(conta['saldo_atual']))
            
            if operacao == 'credito':
                novo_saldo = saldo_atual + Decimal(str(valor))
            elif operacao == 'debito':
                novo_saldo = saldo_atual - Decimal(str(valor))
            else:
                return None
            
            # Atualizar saldo
            cursor.execute(
                "UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s",
                (novo_saldo, conta_id)
            )
            conn.commit()
            
            return {
                'saldo_anterior': saldo_atual,
                'valor_ajuste': valor,
                'operacao': operacao,
                'saldo_novo': novo_saldo
            }
    
    @staticmethod
    def get_totalizadores(filial_id=None):
        """
        Retorna totalizadores de contas bancárias
        
        Args:
            filial_id (int): Filtrar por filial (opcional)
        
        Returns:
            dict: Totalizadores (total_contas, saldo_total, por tipo)
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    COUNT(*) as total_contas,
                    SUM(saldo_atual) as saldo_total,
                    SUM(CASE WHEN tipo_conta = 'corrente' THEN saldo_atual ELSE 0 END) as saldo_corrente,
                    SUM(CASE WHEN tipo_conta = 'poupanca' THEN saldo_atual ELSE 0 END) as saldo_poupanca,
                    SUM(CASE WHEN tipo_conta = 'caixa' THEN saldo_atual ELSE 0 END) as saldo_caixa
                FROM contas_bancarias
                WHERE ativo = 1
            """
            
            params = {}
            
            if filial_id:
                sql += " AND filial_id = %(filial_id)s"
                params['filial_id'] = filial_id
            
            cursor.execute(sql, params if params else None)
            resultado = cursor.fetchone()
            
            return {
                'total_contas': resultado['total_contas'] or 0,
                'saldo_total': Decimal(str(resultado['saldo_total'] or 0)),
                'saldo_corrente': Decimal(str(resultado['saldo_corrente'] or 0)),
                'saldo_poupanca': Decimal(str(resultado['saldo_poupanca'] or 0)),
                'saldo_caixa': Decimal(str(resultado['saldo_caixa'] or 0))
            }
