#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar a migration do banco de dados
"""
import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def run_migration():
    """Executa o arquivo de migration SQL"""
    try:
        # Conecta ao MySQL (sem especificar database)
        print("Conectando ao MySQL...")
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        # Cria o database se não existir
        database_name = os.getenv('MYSQL_DATABASE', 'meetcall_system')
        print(f"Criando database '{database_name}' (se não existir)...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {database_name}")
        
        # Lê o arquivo SQL
        migration_file = 'migrations/001_schema_completo.sql'
        print(f"Lendo arquivo {migration_file}...")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Divide os comandos SQL
        # Remove comentários de linha
        lines = sql_content.split('\n')
        sql_lines = []
        for line in lines:
            # Remove comentários
            if '--' in line:
                line = line[:line.index('--')]
            line = line.strip()
            if line:
                sql_lines.append(line)
        
        sql_content = ' '.join(sql_lines)
        
        # Divide por comandos (;)
        commands = sql_content.split(';')
        
        print(f"Executando {len(commands)} comandos SQL...")
        
        success_count = 0
        error_count = 0
        
        for i, command in enumerate(commands, 1):
            command = command.strip()
            if not command:
                continue
            
            try:
                cursor.execute(command)
                success_count += 1
                
                # Mostra progresso a cada 5 comandos
                if i % 5 == 0:
                    print(f"  Executados {i} comandos...")
                    
            except mysql.connector.Error as e:
                error_count += 1
                # Ignora erros de "tabela já existe" e "já existe"
                if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                    print(f"  ⚠ Erro no comando {i}: {e}")
        
        conn.commit()
        
        print(f"\n✓ Migration concluída!")
        print(f"  - Comandos executados com sucesso: {success_count}")
        if error_count > 0:
            print(f"  - Erros ignorados: {error_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao executar migration: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("EXECUTANDO MIGRATION DO BANCO DE DADOS")
    print("="*60)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("Próximo passo: Execute 'python create_user.py' para criar o usuário admin")
    else:
        print("Migration falhou. Verifique as configurações no arquivo .env")
        sys.exit(1)
