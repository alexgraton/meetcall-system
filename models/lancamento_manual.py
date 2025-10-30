"""
Modelo de dados para Lancamentos Manuais
"""
from typing import List, Dict, Optional
from datetime import date
from decimal import Decimal
from database import DatabaseManager

class LancamentoManualModel:
    """Classe para gerenciar operacoes de Lancamentos Manuais"""
    
    @staticmethod
    def create(dados: Dict) -> int:
        """
        Cria um novo lancamento manual
        
        Args:
            dados: Dicionario com dados do lancamento
                - tipo (str): 'despesa' ou 'receita'
                - descricao (str): Descricao do lancamento
                - valor (Decimal): Valor do lancamento
                - data_lancamento (date): Data do lancamento
                - data_competencia (date, opcional): Data de competencia
                - filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id (int, opcional)
                - fornecedor_id (int, opcional): Para despesas
                - cliente_id (int, opcional): Para receitas
                - numero_documento, forma_pagamento, observacoes (str, opcional)
        
        Returns:
            int: ID do lancamento criado
        """
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO lancamentos_manuais 
                (tipo, descricao, filial_id, tipo_servico_id, centro_custo_id, conta_contabil_id,
                 fornecedor_id, cliente_id, valor, data_lancamento, data_competencia,
                 numero_documento, forma_pagamento, observacoes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                dados['tipo'],
                dados['descricao'],
                dados.get('filial_id'),
                dados.get('tipo_servico_id'),
                dados.get('centro_custo_id'),
                dados.get('conta_contabil_id'),
                dados.get('fornecedor_id'),
                dados.get('cliente_id'),
                dados['valor'],
                dados['data_lancamento'],
                dados.get('data_competencia'),
                dados.get('numero_documento'),
                dados.get('forma_pagamento'),
                dados.get('observacoes'),
                dados.get('created_by')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all(tipo: Optional[str] = None,
                filial_id: Optional[int] = None,
                data_inicio: Optional[date] = None,
                data_fim: Optional[date] = None,
                forma_pagamento: Optional[str] = None) -> List[Dict]:
        """Lista todos os lancamentos com filtros opcionais"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT lm.*, 
                       fil.nome as filial_nome,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       f.nome as fornecedor_nome,
                       c.nome as cliente_nome
                FROM lancamentos_manuais lm
                LEFT JOIN filiais fil ON lm.filial_id = fil.id
                LEFT JOIN tipos_servicos ts ON lm.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON lm.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON lm.conta_contabil_id = pc.id
                LEFT JOIN fornecedores f ON lm.fornecedor_id = f.id
                LEFT JOIN clientes c ON lm.cliente_id = c.id
                WHERE lm.status = 'ativo'
            """
            params = []
            
            if tipo:
                query += " AND lm.tipo = %s"
                params.append(tipo)
            
            if filial_id:
                query += " AND lm.filial_id = %s"
                params.append(filial_id)
            
            if data_inicio:
                query += " AND lm.data_lancamento >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND lm.data_lancamento <= %s"
                params.append(data_fim)
            
            if forma_pagamento:
                query += " AND lm.forma_pagamento = %s"
                params.append(forma_pagamento)
            
            query += " ORDER BY lm.data_lancamento DESC, lm.id DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(lancamento_id: int) -> Optional[Dict]:
        """Busca um lancamento por ID"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT lm.*, 
                       fil.nome as filial_nome,
                       ts.descricao as tipo_servico_descricao,
                       cc.descricao as centro_custo_descricao,
                       pc.codigo as conta_contabil_codigo,
                       pc.descricao as conta_contabil_descricao,
                       f.nome as fornecedor_nome,
                       c.nome as cliente_nome
                FROM lancamentos_manuais lm
                LEFT JOIN filiais fil ON lm.filial_id = fil.id
                LEFT JOIN tipos_servicos ts ON lm.tipo_servico_id = ts.id
                LEFT JOIN centro_custos cc ON lm.centro_custo_id = cc.id
                LEFT JOIN plano_contas pc ON lm.conta_contabil_id = pc.id
                LEFT JOIN fornecedores f ON lm.fornecedor_id = f.id
                LEFT JOIN clientes c ON lm.cliente_id = c.id
                WHERE lm.id = %s
            """
            cursor.execute(query, (lancamento_id,))
            return cursor.fetchone()
    
    @staticmethod
    def update(lancamento_id: int, dados: Dict) -> bool:
        """Atualiza um lancamento existente"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                UPDATE lancamentos_manuais
                SET tipo = %s,
                    descricao = %s,
                    filial_id = %s,
                    tipo_servico_id = %s,
                    centro_custo_id = %s,
                    conta_contabil_id = %s,
                    fornecedor_id = %s,
                    cliente_id = %s,
                    valor = %s,
                    data_lancamento = %s,
                    data_competencia = %s,
                    numero_documento = %s,
                    forma_pagamento = %s,
                    observacoes = %s
                WHERE id = %s
            """
            
            cursor.execute(query, (
                dados['tipo'],
                dados['descricao'],
                dados.get('filial_id'),
                dados.get('tipo_servico_id'),
                dados.get('centro_custo_id'),
                dados.get('conta_contabil_id'),
                dados.get('fornecedor_id'),
                dados.get('cliente_id'),
                dados['valor'],
                dados['data_lancamento'],
                dados.get('data_competencia'),
                dados.get('numero_documento'),
                dados.get('forma_pagamento'),
                dados.get('observacoes'),
                lancamento_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(lancamento_id: int) -> bool:
        """Cancela (soft delete) um lancamento"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE lancamentos_manuais SET status = 'cancelado' WHERE id = %s"
            cursor.execute(query, (lancamento_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_totalizadores(data_inicio: Optional[date] = None,
                          data_fim: Optional[date] = None,
                          filial_id: Optional[int] = None) -> Dict:
        """Retorna valores totalizados por tipo"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) as total_despesas,
                    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) as total_receitas,
                    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) as saldo
                FROM lancamentos_manuais
                WHERE status = 'ativo'
            """
            params = []
            
            if data_inicio:
                query += " AND data_lancamento >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND data_lancamento <= %s"
                params.append(data_fim)
            
            if filial_id:
                query += " AND filial_id = %s"
                params.append(filial_id)
            
            cursor.execute(query, params)
            return cursor.fetchone()
