#!/usr/bin/env python3
"""
Script para executar migrations do banco de dados
"""

import mysql.connector
from config import Config
import os

def run_migration(migration_file):
    """Executa um arquivo de migration SQL"""
    
    config = Config()
    
    print(f"\n🔄 Executando migration: {migration_file}")
    print("="*60)
    
    try:
        connection = mysql.connector.connect(**config.MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Lê o arquivo SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # Separa e executa os comandos
        commands = sql_commands.split(';')
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                except mysql.connector.Error as e:
                    # Ignora erros de tabela já existente
                    if e.errno != 1050:  # Table already exists
                        print(f"⚠️  Aviso: {e}")
        
        connection.commit()
        
        print(f"✅ Migration {migration_file} executada com sucesso!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_migrations():
    """Executa todas as migrations na pasta migrations/"""
    
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    
    if not os.path.exists(migrations_dir):
        print("❌ Pasta migrations/ não encontrada!")
        return False
    
    # Lista todos os arquivos .sql
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    if not migration_files:
        print("⚠️  Nenhuma migration encontrada!")
        return True
    
    print("\n" + "="*60)
    print("🗄️  EXECUTANDO MIGRATIONS DO BANCO DE DADOS")
    print("="*60)
    
    success = True
    for migration_file in migration_files:
        file_path = os.path.join(migrations_dir, migration_file)
        if not run_migration(file_path):
            success = False
            break
    
    if success:
        print("\n" + "="*60)
        print("✅ TODAS AS MIGRATIONS EXECUTADAS COM SUCESSO!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ ERRO AO EXECUTAR MIGRATIONS")
        print("="*60)
    
    return success

if __name__ == '__main__':
    run_all_migrations()
