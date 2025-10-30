"""
Modelo para gerenciar Centros de Custo vinculados a Filiais
"""
from typing import List, Dict, Optional
from database import DatabaseManager

class CentroCustoModel:
    """Operações CRUD para centros de custo"""

    @staticmethod
    def create(dados: Dict) -> Dict:
        """Cria um centro de custo"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Gerar código se não houver
                if not dados.get('codigo'):
                    cursor.execute("SELECT MAX(CAST(SUBSTRING(codigo, 3) AS UNSIGNED)) FROM centro_custos")
                    res = cursor.fetchone()
                    next_num = (res[0] or 0) + 1
                    dados['codigo'] = f"CC{next_num:05d}"

                query = """
                    INSERT INTO centro_custos
                    (codigo, descricao, filial_id, parent_id, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    dados['codigo'],
                    dados['descricao'],
                    dados.get('filial_id'),
                    dados.get('parent_id')
                ))
                conn.commit()
                return {'success': True, 'message': 'Centro de custo cadastrado com sucesso', 'codigo': dados['codigo'], 'id': cursor.lastrowid}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_all(filial_id: Optional[int] = None, include_inactive: bool = False) -> List[Dict]:
        """Lista todos os centros de custo, opcionalmente filtrados por filial"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT cc.*, 
                       f.nome as filial_nome,
                       p.descricao as parent_descricao
                FROM centro_custos cc
                LEFT JOIN filiais f ON cc.filial_id = f.id
                LEFT JOIN centro_custos p ON cc.parent_id = p.id
                WHERE (cc.is_active = 1 OR %s)
            """
            params = [include_inactive]
            
            if filial_id:
                query += " AND (cc.filial_id = %s OR cc.filial_id IS NULL)"
                params.append(filial_id)
            
            query += " ORDER BY cc.codigo"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    @staticmethod
    def get_by_id(centro_custo_id: int) -> Optional[Dict]:
        """Busca um centro de custo por ID"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT cc.*, 
                       f.nome as filial_nome
                FROM centro_custos cc
                LEFT JOIN filiais f ON cc.filial_id = f.id
                WHERE cc.id = %s
            """
            cursor.execute(query, (centro_custo_id,))
            return cursor.fetchone()

    @staticmethod
    def update(centro_custo_id: int, dados: Dict) -> bool:
        """Atualiza um centro de custo"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE centro_custos
                SET descricao=%s, filial_id=%s, parent_id=%s, updated_at=NOW()
                WHERE id=%s
            """
            cursor.execute(query, (
                dados['descricao'],
                dados.get('filial_id'),
                dados.get('parent_id'),
                centro_custo_id
            ))
            conn.commit()
            return True

    @staticmethod
    def toggle_status(centro_custo_id: int) -> bool:
        """Alterna o status ativo/inativo de um centro de custo"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE centro_custos SET is_active = NOT is_active WHERE id = %s",
                (centro_custo_id,)
            )
            conn.commit()
            return True

    @staticmethod
    def delete(centro_custo_id: int) -> bool:
        """Desativa um centro de custo (soft delete)"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE centro_custos SET is_active = 0 WHERE id = %s",
                (centro_custo_id,)
            )
            conn.commit()
            return True

    @staticmethod
    def get_by_filial(filial_id: int, only_active: bool = True) -> List[Dict]:
        """Retorna centros de custo de uma filial específica"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM centro_custos WHERE filial_id = %s"
            if only_active:
                query += " AND is_active = 1"
            query += " ORDER BY codigo"
            cursor.execute(query, (filial_id,))
            return cursor.fetchall()

    @staticmethod
    def get_hierarchy() -> List[Dict]:
        """Retorna centros de custo organizados em hierarquia (raiz + filhos)"""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar centros raiz (sem parent)
            cursor.execute("""
                SELECT cc.*, f.nome as filial_nome
                FROM centro_custos cc
                LEFT JOIN filiais f ON cc.filial_id = f.id
                WHERE cc.parent_id IS NULL AND cc.is_active = 1
                ORDER BY cc.codigo
            """)
            raizes = cursor.fetchall()
            
            # Para cada raiz, buscar filhos
            for raiz in raizes:
                cursor.execute("""
                    SELECT cc.*, f.nome as filial_nome
                    FROM centro_custos cc
                    LEFT JOIN filiais f ON cc.filial_id = f.id
                    WHERE cc.parent_id = %s AND cc.is_active = 1
                    ORDER BY cc.codigo
                """, (raiz['id'],))
                raiz['filhos'] = cursor.fetchall()
            
            return raizes
