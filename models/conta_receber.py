"""
Modelo de dados para Contas a Receber
"""
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from database import DatabaseManager

class ContaReceberModel:
    """Classe para gerenciar operações de Contas a Receber"""
    
    @staticmethod
    def create(dados: Dict) -> int:
        """
        Cria uma nova conta a receber
        
        Args:
            dados: Dicionário com dados da conta
                - cliente_id (int): ID do cliente
                - descricao (str): Descrição da conta
                - valor_total (Decimal): Valor total
                - data_emissao (date): Data de emissão
                - data_vencimento (date): Data de vencimento
                - numero_parcelas (int): Número de parcelas
                - filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id (int, opcional)
                - numero_documento, observacoes (str, opcional)
                - percentual_juros, percentual_multa (Decimal, opcional)
                - is_recorrente, recorrencia_tipo (bool/str, opcional)
        
        Returns:
            int: ID da primeira conta criada (se parcelado, cria múltiplas)
        """
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            numero_parcelas = dados.get('numero_parcelas', 1)
            
            if numero_parcelas > 1:
                # Criar parcelas automáticas
                return ContaReceberModel._criar_parcelas(cursor, dados, conn)
            else:
                # Criar conta única
                query = """
                    INSERT INTO contas_receber 
                    (cliente_id, filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id,
                     descricao, numero_documento, valor_total, data_emissao, data_vencimento,
                     numero_parcelas, parcela_atual, intervalo_parcelas,
                     percentual_juros, percentual_multa, is_recorrente, recorrencia_tipo,
                     observacoes, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    dados['cliente_id'],
                    dados.get('filial_id'),
                    dados.get('tipo_servico_id'),
                    dados.get('centro_custo_id'),
                    dados.get('conta_contabil_id'),
                    dados['descricao'],
                    dados.get('numero_documento'),
                    dados['valor_total'],
                    dados['data_emissao'],
                    dados['data_vencimento'],
                    1,
                    1,
                    dados.get('intervalo_parcelas', 30),
                    dados.get('percentual_juros', 0),
                    dados.get('percentual_multa', 0),
                    dados.get('is_recorrente', False),
                    dados.get('recorrencia_tipo'),
                    dados.get('observacoes'),
                    dados.get('created_by')
                ))
                
                conn.commit()
                return cursor.lastrowid
    
    @staticmethod
    def _criar_parcelas(cursor, dados: Dict, conn) -> int:
        """Cria múltiplas parcelas automaticamente"""
        numero_parcelas = dados['numero_parcelas']
        valor_parcela = Decimal(str(dados['valor_total'])) / numero_parcelas
        data_vencimento = dados['data_vencimento']
        
        # Converter para date se for string
        if isinstance(data_vencimento, str):
            data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
        
        intervalo_dias = dados.get('intervalo_parcelas', 30)
        primeiro_id = None
        
        for i in range(1, numero_parcelas + 1):
            # Calcular data de vencimento da parcela
            if i == 1:
                data_parcela = data_vencimento
            else:
                data_parcela = data_vencimento + timedelta(days=(i-1) * intervalo_dias)
            
            query = """
                INSERT INTO contas_receber 
                (cliente_id, filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id,
                 descricao, numero_documento, valor_total, data_emissao, data_vencimento,
                 numero_parcelas, parcela_atual, intervalo_parcelas,
                 percentual_juros, percentual_multa, is_recorrente, recorrencia_tipo,
                 observacoes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                dados['cliente_id'],
                dados.get('filial_id'),
                dados.get('tipo_servico_id'),
                dados.get('centro_custo_id'),
                dados.get('conta_contabil_id'),
                f"{dados['descricao']} - Parcela {i}/{numero_parcelas}",
                dados.get('numero_documento'),
                float(valor_parcela),
                dados['data_emissao'],
                data_parcela,
                numero_parcelas,
                i,
                intervalo_dias,
                dados.get('percentual_juros', 0),
                dados.get('percentual_multa', 0),
                dados.get('is_recorrente', False),
                dados.get('recorrencia_tipo'),
                dados.get('observacoes'),
                dados.get('created_by')
            ))
            
            if i == 1:
                primeiro_id = cursor.lastrowid
        
        conn.commit()
        return primeiro_id
    
    @staticmethod
    def get_all(cliente_id: Optional[int] = None, 
                filial_id: Optional[int] = None,
                status: Optional[str] = None,
                data_inicio: Optional[date] = None,
                data_fim: Optional[date] = None) -> List[Dict]:
        """Lista todas as contas a receber com filtros opcionais"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT cr.*, 
                       c.razao_social as cliente_nome,
                       c.nome as cliente_fantasia,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       fil.nome as filial_nome
                FROM contas_receber cr
                INNER JOIN clientes c ON cr.cliente_id = c.id
                LEFT JOIN tipos_servicos ts ON cr.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON cr.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON cr.conta_contabil_id = pc.id
                LEFT JOIN filiais fil ON cr.filial_id = fil.id
                WHERE 1=1
            """
            params = []
            
            if cliente_id:
                query += " AND cr.cliente_id = %s"
                params.append(cliente_id)
            
            if filial_id:
                query += " AND cr.filial_id = %s"
                params.append(filial_id)
            
            if status:
                query += " AND cr.status = %s"
                params.append(status)
            
            if data_inicio:
                query += " AND cr.data_vencimento >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND cr.data_vencimento <= %s"
                params.append(data_fim)
            
            query += " ORDER BY cr.data_vencimento ASC, cr.parcela_atual ASC"
            
            cursor.execute(query, params)
            contas = cursor.fetchall()
            
            # Atualizar status de vencidas
            ContaReceberModel._atualizar_status_vencidas(cursor, conn)
            
            return contas
    
    @staticmethod
    def _atualizar_status_vencidas(cursor, conn):
        """Atualiza automaticamente o status de contas vencidas"""
        query = """
            UPDATE contas_receber 
            SET status = 'vencido'
            WHERE status = 'pendente' 
            AND data_vencimento < CURDATE()
        """
        cursor.execute(query)
        conn.commit()
    
    @staticmethod
    def get_by_id(conta_id: int) -> Optional[Dict]:
        """Busca uma conta por ID"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT cr.*, 
                       c.razao_social as cliente_nome,
                       c.nome as cliente_fantasia,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       fil.nome as filial_nome
                FROM contas_receber cr
                INNER JOIN clientes c ON cr.cliente_id = c.id
                LEFT JOIN tipos_servicos ts ON cr.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON cr.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON cr.conta_contabil_id = pc.id
                LEFT JOIN filiais fil ON cr.filial_id = fil.id
                WHERE cr.id = %s
            """
            cursor.execute(query, (conta_id,))
            return cursor.fetchone()
    
    @staticmethod
    def receber(conta_id: int, dados_recebimento: Dict) -> bool:
        """
        Registra o recebimento de uma conta
        
        Args:
            conta_id: ID da conta
            dados_recebimento:
                - conta_bancaria_id (int): ID da conta bancária
                - data_recebimento (date): Data do recebimento
                - valor_pago (Decimal): Valor recebido
                - valor_juros (Decimal, opcional): Juros cobrados
                - valor_multa (Decimal, opcional): Multa cobrada
                - valor_desconto (Decimal, opcional): Desconto concedido
        """
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Validar conta bancária
            if not dados_recebimento.get('conta_bancaria_id'):
                raise ValueError('Conta bancária é obrigatória para registrar recebimento')
            
            query = """
                UPDATE contas_receber
                SET conta_bancaria_id = %s,
                    data_recebimento = %s,
                    valor_pago = %s,
                    valor_juros = %s,
                    valor_multa = %s,
                    valor_desconto = %s,
                    status = 'recebido'
                WHERE id = %s
            """
            
            cursor.execute(query, (
                dados_recebimento['conta_bancaria_id'],
                dados_recebimento['data_recebimento'],
                dados_recebimento['valor_pago'],
                dados_recebimento.get('valor_juros', 0),
                dados_recebimento.get('valor_multa', 0),
                dados_recebimento.get('valor_desconto', 0),
                conta_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def cancelar(conta_id: int) -> bool:
        """Cancela uma conta a receber"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE contas_receber SET status = 'cancelado' WHERE id = %s"
            cursor.execute(query, (conta_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_totalizadores() -> Dict:
        """Retorna valores totalizados por status"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Atualizar vencidas primeiro
            cursor.execute("""
                UPDATE contas_receber 
                SET status = 'vencido'
                WHERE status = 'pendente' AND data_vencimento < CURDATE()
            """)
            conn.commit()
            
            # Buscar totalizadores
            query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN status = 'pendente' THEN valor_total ELSE 0 END), 0) as total_pendente,
                    COALESCE(SUM(CASE WHEN status = 'vencido' THEN valor_total ELSE 0 END), 0) as total_vencido,
                    COALESCE(SUM(CASE WHEN status = 'recebido' THEN valor_pago ELSE 0 END), 0) as total_recebido,
                    COALESCE(SUM(valor_total), 0) as total_geral
                FROM contas_receber
                WHERE status != 'cancelado'
            """
            
            cursor.execute(query)
            return cursor.fetchone()
