"""
Modelo de dados para Filiais
"""

import mysql.connector
from database import db

class FilialModel:
    """Classe para gerenciar operações de Filiais"""
    
    @staticmethod
    def create(data, user_id):
        """
        Cria uma nova filial
        
        Args:
            data (dict): Dados da filial
            user_id (int): ID do usuário que está criando
            
        Returns:
            int: ID da filial criada
        """
        with db.get_connection() as connection:
            cursor = connection.cursor()
            
            query = """
            INSERT INTO filiais (
                codigo, nome, razao_social, cnpj, email, telefone,
                cep, endereco, numero, complemento, bairro, cidade, estado,
                is_matriz, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                data.get('codigo'),
                data.get('nome'),
                data.get('razao_social'),
                data.get('cnpj'),
                data.get('email'),
                data.get('telefone'),
                data.get('cep'),
                data.get('endereco'),
                data.get('numero'),
                data.get('complemento'),
                data.get('bairro'),
                data.get('cidade'),
                data.get('estado'),
                data.get('is_matriz', False),
                user_id
            )
            
            try:
                cursor.execute(query, values)
                connection.commit()
                return cursor.lastrowid
            except mysql.connector.IntegrityError as e:
                if 'Duplicate entry' in str(e):
                    if 'codigo' in str(e):
                        raise ValueError("Código já está em uso")
                    elif 'cnpj' in str(e):
                        raise ValueError("CNPJ já está cadastrado")
                raise ValueError(str(e))
    
    @staticmethod
    def get_all(include_inactive=False):
        """
        Retorna todas as filiais
        
        Args:
            include_inactive (bool): Se deve incluir filiais inativas
            
        Returns:
            list: Lista de filiais
        """
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT f.*, u.name as criado_por_nome
            FROM filiais f
            LEFT JOIN users u ON f.created_by = u.id
            """
            
            if not include_inactive:
                query += " WHERE f.is_active = TRUE"
            
            query += " ORDER BY f.is_matriz DESC, f.nome ASC"
            
            cursor.execute(query)
            return cursor.fetchall()
    
    @staticmethod
    def get_by_id(filial_id):
        """
        Busca uma filial por ID
        
        Args:
            filial_id (int): ID da filial
            
        Returns:
            dict: Dados da filial ou None
        """
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT f.*, u.name as criado_por_nome
            FROM filiais f
            LEFT JOIN users u ON f.created_by = u.id
            WHERE f.id = %s
            """
            
            cursor.execute(query, (filial_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_by_codigo(codigo):
        """
        Busca uma filial por código
        
        Args:
            codigo (str): Código da filial
            
        Returns:
            dict: Dados da filial ou None
        """
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM filiais WHERE codigo = %s"
            cursor.execute(query, (codigo,))
            return cursor.fetchone()
    
    @staticmethod
    def update(filial_id, data):
        """
        Atualiza uma filial
        
        Args:
            filial_id (int): ID da filial
            data (dict): Dados a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        with db.get_connection() as connection:
            cursor = connection.cursor()
            
            # Constrói a query dinamicamente apenas com os campos fornecidos
            fields = []
            values = []
            
            allowed_fields = [
                'codigo', 'nome', 'razao_social', 'cnpj', 'email', 'telefone',
                'cep', 'endereco', 'numero', 'complemento', 'bairro', 
                'cidade', 'estado', 'is_matriz'
            ]
            
            for field in allowed_fields:
                if field in data:
                    fields.append(f"{field} = %s")
                    values.append(data[field])
            
            if not fields:
                return False
            
            values.append(filial_id)
            
            query = f"""
            UPDATE filiais 
            SET {', '.join(fields)}
            WHERE id = %s
            """
            
            try:
                cursor.execute(query, values)
                connection.commit()
                return cursor.rowcount > 0
            except mysql.connector.IntegrityError as e:
                if 'Duplicate entry' in str(e):
                    if 'codigo' in str(e):
                        raise ValueError("Código já está em uso")
                    elif 'cnpj' in str(e):
                        raise ValueError("CNPJ já está cadastrado")
                raise ValueError(str(e))
    
    @staticmethod
    def toggle_status(filial_id):
        """
        Ativa ou desativa uma filial
        
        Args:
            filial_id (int): ID da filial
            
        Returns:
            bool: True se alterado com sucesso
        """
        with db.get_connection() as connection:
            cursor = connection.cursor()
            
            query = """
            UPDATE filiais 
            SET is_active = NOT is_active 
            WHERE id = %s
            """
            
            cursor.execute(query, (filial_id,))
            connection.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(filial_id):
        """
        Deleta uma filial (soft delete via is_active)
        
        Args:
            filial_id (int): ID da filial
            
        Returns:
            bool: True se deletado com sucesso
        """
        with db.get_connection() as connection:
            cursor = connection.cursor()
            
            query = """
            UPDATE filiais 
            SET is_active = FALSE 
            WHERE id = %s
            """
            
            cursor.execute(query, (filial_id,))
            connection.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    def get_matriz():
        """
        Retorna a filial matriz
        
        Returns:
            dict: Dados da matriz ou None
        """
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM filiais 
            WHERE is_matriz = TRUE AND is_active = TRUE
            LIMIT 1
            """
            
            cursor.execute(query)
            return cursor.fetchone()
