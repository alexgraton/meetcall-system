#!/usr/bin/env python3
"""
Script para testar a conexão com o MySQL
"""

import mysql.connector
from config import Config

def test_mysql_connection():
    """Testa a conexão com o MySQL"""
    config = Config()
    
    print("="*60)
    print("🔍 TESTANDO CONEXÃO COM MYSQL")
    print("="*60)
    print(f"\n📋 Configurações:")
    print(f"   Host: {config.MYSQL_HOST}")
    print(f"   Port: {config.MYSQL_PORT}")
    print(f"   User: {config.MYSQL_USER}")
    print(f"   Database: {config.MYSQL_DATABASE}")
    print(f"   Password: {'***' if config.MYSQL_PASSWORD else '(vazia)'}")
    
    # Primeiro testa conexão sem database
    print("\n🔌 Testando conexão com o servidor MySQL...")
    
    try:
        config_without_db = config.MYSQL_CONFIG.copy()
        db_name = config_without_db.pop('database')
        
        connection = mysql.connector.connect(**config_without_db)
        print("✅ Conexão com MySQL estabelecida com sucesso!")
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ Versão do MySQL: {version[0]}")
        
        # Verifica se o banco de dados existe
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if db_name in databases:
            print(f"✅ Banco de dados '{db_name}' encontrado!")
            
            # Conecta ao banco e verifica tabelas
            cursor.execute(f"USE {db_name}")
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if tables:
                print(f"✅ Tabelas encontradas: {', '.join(tables)}")
            else:
                print(f"⚠️  Banco '{db_name}' existe mas não tem tabelas")
        else:
            print(f"⚠️  Banco de dados '{db_name}' NÃO existe")
            print(f"   Bancos disponíveis: {', '.join(databases)}")
        
        connection.close()
        
        print("\n" + "="*60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ ERRO NA CONEXÃO:")
        print(f"   Código: {e.errno}")
        print(f"   Mensagem: {e.msg}")
        
        if e.errno == 1045:
            print("\n💡 Dica: Verifique o usuário e senha no arquivo .env")
        elif e.errno == 2003:
            print("\n💡 Dica: Verifique se o MySQL está rodando")
        
        print("\n" + "="*60)
        print("❌ TESTE FALHOU")
        print("="*60)
        return False
    
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        print("\n" + "="*60)
        print("❌ TESTE FALHOU")
        print("="*60)
        return False

if __name__ == '__main__':
    test_mysql_connection()
