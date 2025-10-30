"""
Modelo para gerenciar o Plano de Contas com estrutura hierárquica DRE
"""
from typing import List, Dict, Optional
from database import DatabaseManager

class PlanoContaModel:
    """Operações CRUD para Plano de Contas"""

    @staticmethod
    def create(dados: Dict) -> Dict:
        """Cria uma conta no plano de contas"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Validar nível baseado no código (contar pontos)
                codigo = dados.get('codigo', '')
                nivel = codigo.count('.') + 1
                
                # Se é nível > 1, validar que o parent existe
                if nivel > 1:
                    parent_codigo = '.'.join(codigo.split('.')[:-1])
                    cursor.execute("SELECT id FROM plano_contas WHERE codigo = %s", (parent_codigo,))
                    parent = cursor.fetchone()
                    if not parent:
                        return {'success': False, 'message': f'Conta pai {parent_codigo} não encontrada'}
                    dados['parent_id'] = parent[0]
                else:
                    dados['parent_id'] = None
                
                # Contas sintéticas (que têm filhos) não aceitam lançamento
                # Por padrão, criar como analítica (aceita lançamento)
                # Se depois criar filhos, marcar como sintética
                
                query = """
                    INSERT INTO plano_contas
                    (codigo, descricao, tipo, nivel, parent_id, aceita_lancamento, dre_grupo, ordem, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    dados['codigo'],
                    dados['descricao'],
                    dados['tipo'],
                    nivel,
                    dados.get('parent_id'),
                    dados.get('aceita_lancamento', True),
                    dados.get('dre_grupo'),
                    dados.get('ordem', 0)
                ))
                
                # Se tem parent, marcar o parent como sintético (não aceita lançamento)
                if dados.get('parent_id'):
                    cursor.execute(
                        "UPDATE plano_contas SET aceita_lancamento = 0 WHERE id = %s",
                        (dados['parent_id'],)
                    )
                
                conn.commit()
                return {'success': True, 'message': 'Conta cadastrada com sucesso', 'codigo': dados['codigo'], 'id': cursor.lastrowid}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_all(tipo: Optional[str] = None, nivel: Optional[int] = None, aceita_lancamento: Optional[bool] = None) -> List[Dict]:
        """Lista todas as contas, com filtros opcionais"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT pc.*, 
                       p.descricao as parent_descricao,
                       (SELECT COUNT(*) FROM plano_contas WHERE parent_id = pc.id) as filhos_count
                FROM plano_contas pc
                LEFT JOIN plano_contas p ON pc.parent_id = p.id
                WHERE pc.is_active = 1
            """
            params = []
            
            if tipo:
                query += " AND pc.tipo = %s"
                params.append(tipo)
            
            if nivel:
                query += " AND pc.nivel = %s"
                params.append(nivel)
            
            if aceita_lancamento is not None:
                query += " AND pc.aceita_lancamento = %s"
                params.append(aceita_lancamento)
            
            query += " ORDER BY pc.codigo"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    @staticmethod
    def get_by_id(conta_id: int) -> Optional[Dict]:
        """Busca uma conta por ID"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT pc.*, 
                       p.descricao as parent_descricao,
                       (SELECT COUNT(*) FROM plano_contas WHERE parent_id = pc.id) as filhos_count
                FROM plano_contas pc
                LEFT JOIN plano_contas p ON pc.parent_id = p.id
                WHERE pc.id = %s
            """
            cursor.execute(query, (conta_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Dict]:
        """Busca uma conta por código"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM plano_contas WHERE codigo = %s", (codigo,))
            return cursor.fetchone()

    @staticmethod
    def update(conta_id: int, dados: Dict) -> bool:
        """Atualiza uma conta (não permite alterar código nem nível)"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE plano_contas
                SET descricao=%s, dre_grupo=%s, ordem=%s, updated_at=NOW()
                WHERE id=%s
            """
            cursor.execute(query, (
                dados['descricao'],
                dados.get('dre_grupo'),
                dados.get('ordem', 0),
                conta_id
            ))
            conn.commit()
            return True

    @staticmethod
    def toggle_status(conta_id: int) -> bool:
        """Alterna o status ativo/inativo de uma conta"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE plano_contas SET is_active = NOT is_active WHERE id = %s",
                (conta_id,)
            )
            conn.commit()
            return True

    @staticmethod
    def delete(conta_id: int) -> Dict:
        """Desativa uma conta (soft delete) - valida se não tem filhos ou lançamentos"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Verificar se tem filhos
            cursor.execute("SELECT COUNT(*) as count FROM plano_contas WHERE parent_id = %s AND is_active = 1", (conta_id,))
            result = cursor.fetchone()
            if result['count'] > 0:
                return {'success': False, 'message': 'Esta conta possui subcontas ativas e não pode ser excluída'}
            
            # TODO: Verificar se tem lançamentos quando implementar contas a pagar/receber
            
            cursor.execute("UPDATE plano_contas SET is_active = 0 WHERE id = %s", (conta_id,))
            conn.commit()
            return {'success': True, 'message': 'Conta desativada com sucesso'}

    @staticmethod
    def get_hierarchy(tipo: Optional[str] = None) -> List[Dict]:
        """Retorna o plano de contas em estrutura hierárquica"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar contas nível 1 (raiz)
            query = "SELECT * FROM plano_contas WHERE nivel = 1 AND is_active = 1 ORDER BY ordem, codigo"
            if tipo:
                query = "SELECT * FROM plano_contas WHERE nivel = 1 AND is_active = 1 AND tipo = %s ORDER BY ordem, codigo"
                cursor.execute(query, (tipo,))
            else:
                cursor.execute(query)
            
            nivel1 = cursor.fetchall()
            
            # Para cada nível 1, buscar filhos recursivamente
            for n1 in nivel1:
                n1['filhos'] = PlanoContaModel._get_filhos(cursor, n1['id'])
            
            return nivel1

    @staticmethod
    def _get_filhos(cursor, parent_id: int, visited: set = None) -> List[Dict]:
        """Método auxiliar para buscar filhos recursivamente"""
        if visited is None:
            visited = set()
        
        # Proteção contra loop infinito
        if parent_id in visited:
            return []
        
        visited.add(parent_id)
        
        cursor.execute(
            "SELECT * FROM plano_contas WHERE parent_id = %s AND is_active = 1 ORDER BY codigo",
            (parent_id,)
        )
        filhos = cursor.fetchall()
        
        for filho in filhos:
            filho['filhos'] = PlanoContaModel._get_filhos(cursor, filho['id'], visited.copy())
        
        return filhos

    @staticmethod
    def get_analiticas(tipo: Optional[str] = None) -> List[Dict]:
        """Retorna apenas contas analíticas (que aceitam lançamento)"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM plano_contas 
                WHERE aceita_lancamento = 1 AND is_active = 1
            """
            
            if tipo:
                query += " AND tipo = %s"
                cursor.execute(query + " ORDER BY codigo", (tipo,))
            else:
                cursor.execute(query + " ORDER BY codigo")
            
            return cursor.fetchall()

    @staticmethod
    def get_por_dre_grupo(dre_grupo: str) -> List[Dict]:
        """Retorna contas de um grupo DRE específico"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM plano_contas WHERE dre_grupo = %s AND is_active = 1 ORDER BY codigo",
                (dre_grupo,)
            )
            return cursor.fetchall()
