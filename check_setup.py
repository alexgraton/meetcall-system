#!/usr/bin/env python3
"""
Script para verificar se todas as dependências estão instaladas
e se o ambiente está configurado corretamente
"""

import sys
import importlib
import os
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Versão muito antiga!")
        print("   Requerida: Python 3.8+")
        return False

def check_packages():
    """Verifica se os pacotes necessários estão instalados"""
    required_packages = [
        ('flask', 'Flask'),
        ('mysql.connector', 'MySQL Connector'),
        ('bcrypt', 'bcrypt'),
        ('dotenv', 'python-dotenv')
    ]
    
    all_ok = True
    
    print("\n📦 Verificando pacotes Python:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {name} - Instalado")
        except ImportError:
            print(f"❌ {name} - NÃO ENCONTRADO")
            all_ok = False
    
    return all_ok

def check_environment():
    """Verifica se os arquivos de configuração existem"""
    print("\n🔧 Verificando configuração:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ Arquivo .env - Encontrado")
        return True
    elif env_example.exists():
        print("⚠️  Arquivo .env - NÃO ENCONTRADO")
        print("   Arquivo .env.example encontrado")
        print("   Execute: cp .env.example .env")
        return False
    else:
        print("❌ Arquivos de configuração - NÃO ENCONTRADOS")
        return False

def check_database_config():
    """Verifica se as configurações do banco estão definidas"""
    try:
        from config import Config
        config = Config()
        
        print("\n🗄️  Verificando configuração do banco:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        required_vars = [
            ('MYSQL_HOST', config.MYSQL_HOST),
            ('MYSQL_PORT', config.MYSQL_PORT),
            ('MYSQL_USER', config.MYSQL_USER),
            ('MYSQL_DATABASE', config.MYSQL_DATABASE)
        ]
        
        all_ok = True
        
        for var_name, value in required_vars:
            if value:
                print(f"✅ {var_name}: {value}")
            else:
                print(f"❌ {var_name}: NÃO DEFINIDO")
                all_ok = False
        
        # Senha pode estar vazia (para desenvolvimento local)
        if config.MYSQL_PASSWORD:
            print(f"✅ MYSQL_PASSWORD: ••••••••")
        else:
            print(f"⚠️  MYSQL_PASSWORD: VAZIO (OK para desenvolvimento)")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return False

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        print("\n🔌 Testando conexão com banco:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        from database import db
        
        with db.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                print("✅ Conexão com MySQL - OK")
                return True
            
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        print("\n💡 Possíveis soluções:")
        print("   - Verifique se o MySQL está rodando")
        print("   - Verifique as credenciais no arquivo .env")
        print("   - Execute: python init_database.py")
        return False

def main():
    """Função principal de verificação"""
    print("🔍 VERIFICAÇÃO DO AMBIENTE MEETCALL SYSTEM")
    print("=" * 50)
    
    checks = [
        ("Versão do Python", check_python_version),
        ("Pacotes Python", check_packages),
        ("Arquivos de configuração", check_environment),
        ("Configuração do banco", check_database_config),
        ("Conexão com banco", test_database_connection)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro em '{name}': {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 50)
    
    for (name, _), result in zip(checks, results):
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    all_ok = all(results)
    
    if all_ok:
        print("\n🎉 SISTEMA PRONTO PARA USO!")
        print("Execute: python app.py")
    else:
        print("\n⚠️  CORRIJA OS PROBLEMAS ANTES DE CONTINUAR")
        print("\n📋 Passos recomendados:")
        print("1. pip install -r requirements.txt")
        print("2. cp .env.example .env (edite as configurações)")
        print("3. python init_database.py")
        print("4. python check_setup.py (execute novamente)")
    
    print("=" * 50)

if __name__ == '__main__':
    main()