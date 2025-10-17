import mysql.connector
import bcrypt
from contextlib import contextmanager
from config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco de dados"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config.MYSQL_CONFIG)
            yield connection
        except mysql.connector.Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def initialize_database(self):
        """Cria o banco de dados e as tabelas se não existirem"""
        # Primeiro, conecta sem especificar o banco para criá-lo
        config_without_db = self.config.MYSQL_CONFIG.copy()
        db_name = config_without_db.pop('database')
        
        try:
            with mysql.connector.connect(**config_without_db) as connection:
                cursor = connection.cursor()
                
                # Cria o banco de dados se não existir
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.execute(f"USE {db_name}")
                
                # Cria a tabela de usuários
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_users_table)
                
                connection.commit()
                print("Banco de dados e tabelas criados com sucesso!")
                
        except mysql.connector.Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def create_user(self, email, password, name):
        """Cria um novo usuário no banco de dados"""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as connection:
            cursor = connection.cursor()
            
            query = """
            INSERT INTO users (email, password_hash, name) 
            VALUES (%s, %s, %s)
            """
            
            try:
                cursor.execute(query, (email, password_hash, name))
                connection.commit()
                return cursor.lastrowid
            except mysql.connector.IntegrityError:
                raise ValueError("Email já está em uso")
    
    def authenticate_user(self, email, password):
        """Autentica um usuário"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT id, email, password_hash, name 
            FROM users 
            WHERE email = %s AND is_active = TRUE
            """
            
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user and self._verify_password(password, user['password_hash']):
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name']
                }
            
            return None
    
    def get_user_by_email(self, email):
        """Busca um usuário pelo email"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT id, email, name, created_at 
            FROM users 
            WHERE email = %s AND is_active = TRUE
            """
            
            cursor.execute(query, (email,))
            return cursor.fetchone()
    
    def update_user_password(self, email, new_password):
        """Atualiza a senha de um usuário"""
        password_hash = self._hash_password(new_password)
        
        with self.get_connection() as connection:
            cursor = connection.cursor()
            
            query = """
            UPDATE users 
            SET password_hash = %s 
            WHERE email = %s AND is_active = TRUE
            """
            
            cursor.execute(query, (password_hash, email))
            connection.commit()
            
            return cursor.rowcount > 0
    
    def _hash_password(self, password):
        """Cria o hash da senha usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password, password_hash):
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# Instância global do gerenciador de banco
db = DatabaseManager()