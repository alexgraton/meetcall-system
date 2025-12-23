"""
Modelo para gerenciar Tipos de Serviços
Estrutura hierárquica com categorias pai e subcategorias
"""
import mysql.connector
from typing import List, Dict, Optional
from database import DatabaseManager

class TipoServicoModel:
    """Modelo para operações CRUD de Tipos de Serviços / Categorias de Despesas"""
    
    @staticmethod
    def create(nome: str, descricao: str = None, parent_id: int = None, 
               tipo: str = 'despesa', codigo: str = None) -> int:
        """Cria uma nova categoria de despesa"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            
            # Gerar código automaticamente se não fornecido
            if not codigo:
                cursor.execute("SELECT MAX(CAST(SUBSTRING(codigo, 3) AS UNSIGNED)) FROM tipos_servicos")
                result = cursor.fetchone()
                next_num = (result[0] or 0) + 1
                codigo = f"TS{next_num:04d}"
            
            query = """
                INSERT INTO tipos_servicos 
                (codigo, nome, descricao, tipo, parent_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (codigo, nome, descricao, tipo, parent_id))
            db.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all(include_inactive: bool = False) -> List[Dict]:
        """Retorna todos os tipos de serviços"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor(dictionary=True)
            
            if include_inactive:
                query = """
                    SELECT ts.*, parent.nome as parent_nome
                    FROM tipos_servicos ts
                    LEFT JOIN tipos_servicos parent ON ts.parent_id = parent.id
                    ORDER BY 
                        CASE WHEN ts.parent_id IS NULL THEN ts.id ELSE ts.parent_id END,
                        ts.parent_id IS NOT NULL,
                        ts.nome
                """
            else:
                query = """
                    SELECT ts.*, parent.nome as parent_nome
                    FROM tipos_servicos ts
                    LEFT JOIN tipos_servicos parent ON ts.parent_id = parent.id
                    WHERE ts.is_active = 1
                    ORDER BY 
                        CASE WHEN ts.parent_id IS NULL THEN ts.id ELSE ts.parent_id END,
                        ts.parent_id IS NOT NULL,
                        ts.nome
                """
            
            cursor.execute(query)
            return cursor.fetchall()
    
    @staticmethod
    def get_hierarchy() -> List[Dict]:
        """Retorna tipos de serviços organizados em hierarquia"""
        tipos = TipoServicoModel.get_all()
        
        # Separar categorias raiz (sem pai) e subcategorias
        categorias = {}
        subcategorias = {}
        
        for tipo in tipos:
            if tipo['parent_id'] is None:
                categorias[tipo['id']] = {
                    **tipo,
                    'children': []
                }
            else:
                if tipo['parent_id'] not in subcategorias:
                    subcategorias[tipo['parent_id']] = []
                subcategorias[tipo['parent_id']].append(tipo)
        
        # Montar hierarquia
        for parent_id, children in subcategorias.items():
            if parent_id in categorias:
                categorias[parent_id]['children'] = children
        
        return list(categorias.values())
    
    @staticmethod
    def get_categories() -> List[Dict]:
        """Retorna apenas as categorias raiz (sem pai)"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT * FROM tipos_servicos
                WHERE parent_id IS NULL AND is_active = 1
                ORDER BY nome
            """
            cursor.execute(query)
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(tipo_id: int) -> Optional[Dict]:
        """Busca um tipo de serviço por ID"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT ts.*, parent.nome as parent_nome
                FROM tipos_servicos ts
                LEFT JOIN tipos_servicos parent ON ts.parent_id = parent.id
                WHERE ts.id = %s
            """
            cursor.execute(query, (tipo_id,))
            return cursor.fetchone()
    
    @staticmethod
    def update(tipo_id: int, nome: str, descricao: str = None, 
               parent_id: int = None) -> bool:
        """Atualiza uma categoria de despesa"""
        # Validar se não está tentando ser pai de si mesmo
        if parent_id == tipo_id:
            raise ValueError("Uma categoria não pode ser pai de si mesma")
        
        # Validar ciclos na hierarquia
        if parent_id:
            if TipoServicoModel._has_circular_reference(tipo_id, parent_id):
                raise ValueError("Esta alteração criaria uma referência circular na hierarquia")
        
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            query = """
                UPDATE tipos_servicos
                SET nome = %s, descricao = %s, parent_id = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (nome, descricao, parent_id, tipo_id))
            db.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def toggle_status(tipo_id: int) -> bool:
        """Alterna o status ativo/inativo de um tipo de serviço"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            query = """
                UPDATE tipos_servicos
                SET is_active = NOT is_active, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (tipo_id,))
            db.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(tipo_id: int) -> bool:
        """Exclui logicamente um tipo de serviço (soft delete)"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            
            # Desativar o tipo
            query = """
                UPDATE tipos_servicos
                SET is_active = 0, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (tipo_id,))
            
            # Desativar todos os filhos
            query_children = """
                UPDATE tipos_servicos
                SET is_active = 0, updated_at = NOW()
                WHERE parent_id = %s
            """
            cursor.execute(query_children, (tipo_id,))
            
            db.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def has_children(tipo_id: int) -> bool:
        """Verifica se um tipo de serviço possui subcategorias"""
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            query = "SELECT COUNT(*) as count FROM tipos_servicos WHERE parent_id = %s"
            cursor.execute(query, (tipo_id,))
            result = cursor.fetchone()
            return result[0] > 0
    
    @staticmethod
    def _has_circular_reference(tipo_id: int, new_parent_id: int) -> bool:
        """Verifica se uma mudança de pai criaria uma referência circular"""
        current_id = new_parent_id
        visited = set()
        
        db_manager = DatabaseManager()
        with db_manager.get_connection() as db:
            cursor = db.cursor()
            
            while current_id is not None:
                if current_id in visited or current_id == tipo_id:
                    return True
                
                visited.add(current_id)
                
                query = "SELECT parent_id FROM tipos_servicos WHERE id = %s"
                cursor.execute(query, (current_id,))
                result = cursor.fetchone()
                
                if result is None:
                    break
                
                current_id = result[0]
        
        return False
