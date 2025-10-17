import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'meetcall-secret-key-2025'
    
    # Configurações do MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'meetcall_system'
    
    @property
    def MYSQL_CONFIG(self):
        return {
            'host': self.MYSQL_HOST,
            'port': self.MYSQL_PORT,
            'user': self.MYSQL_USER,
            'password': self.MYSQL_PASSWORD,
            'database': self.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }