#!/usr/bin/env python3
"""
Script para executar migration inicial do banco de dados
Executa apenas a migration 000_initial_schema.sql que contém o schema completo
"""

import mysql.connector
from config import Config
import os

def run_initial_migration():
    """Executa a migration inicial consolidada"""
    
    config = Config()
    migration_file = os.path.join('migrations', '000_initial_schema.sql')
    
    print("="*60)
    print("🚀 EXECUTANDO MIGRATION INICIAL")
    print("="*60)
    print(f"\n📄 Arquivo: {migration_file}")
    print("\nEsta migration irá criar:")
    print("  • 18 tabelas completas do sistema")
    print("  • Todas as foreign keys e índices")
    print("  • Schema pronto para produção")
    print("\n" + "="*60)
    
    try:
        connection = mysql.connector.connect(**config.MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Lê o arquivo SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Separa e executa os comandos
        commands = sql_content.split(';')
        
        executed = 0
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    executed += 1
                except mysql.connector.Error as e:
                    # Ignora erros de "tabela já existe"
                    if e.errno != 1050:  # Table already exists
                        print(f"⚠️  Aviso: {e}")
        
        connection.commit()
        
        print("\n" + "="*60)
        print("✅ MIGRATION EXECUTADA COM SUCESSO!")
        print("="*60)
        print(f"  • {executed} comandos executados")
        print("  • Banco de dados pronto para uso")
        print("\n💡 Próximo passo:")
        print("   python init_database.py  # Para criar o primeiro usuário admin")
        print("="*60)
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"\n❌ ERRO: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ ERRO: Arquivo {migration_file} não encontrado!")
        return False
    
    return True


if __name__ == '__main__':
    print("\n")
    success = run_initial_migration()
    exit(0 if success else 1)
