"""
Helper para configurar as credenciais do MySQL
Execute este arquivo para atualizar o .env com suas credenciais
"""

import os
from pathlib import Path

def update_env_file():
    """Atualiza o arquivo .env com as credenciais do MySQL"""
    
    print("="*60)
    print("🔧 CONFIGURAÇÃO DO MYSQL - MEETCALL SYSTEM")
    print("="*60)
    print()
    
    # Configurações atuais
    current_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': os.getenv('MYSQL_PORT', '3306'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'database': os.getenv('MYSQL_DATABASE', 'meetcall_system')
    }
    
    print("📋 Configuração atual:")
    print(f"   Host: {current_config['host']}")
    print(f"   Porta: {current_config['port']}")
    print(f"   Usuário: {current_config['user']}")
    print(f"   Banco: {current_config['database']}")
    print()
    
    # Solicita informações
    print("Digite as informações do MySQL (Enter para manter o padrão):")
    print()
    
    host = input(f"Host [{current_config['host']}]: ").strip() or current_config['host']
    port = input(f"Porta [{current_config['port']}]: ").strip() or current_config['port']
    user = input(f"Usuário [{current_config['user']}]: ").strip() or current_config['user']
    password = input("Senha: ").strip()
    database = input(f"Nome do Banco [{current_config['database']}]: ").strip() or current_config['database']
    
    # Conteúdo do arquivo .env
    env_content = f"""# Configurações do Flask
SECRET_KEY=meetcall-secret-key-2025

# Configurações do MySQL
MYSQL_HOST={host}
MYSQL_PORT={port}
MYSQL_USER={user}
MYSQL_PASSWORD={password}
MYSQL_DATABASE={database}
"""
    
    # Salva no arquivo .env
    env_path = Path(__file__).parent / '.env'
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print()
    print("="*60)
    print("✅ Arquivo .env atualizado com sucesso!")
    print("="*60)
    print()
    print("🔍 Execute agora: python test_connection.py")
    print("   Para verificar se a conexão está funcionando")
    print()

if __name__ == '__main__':
    try:
        update_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
