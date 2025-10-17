#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do MeetCall System
"""

from database import db

def initialize_system():
    """Inicializa o sistema criando o banco e usuários padrão"""
    
    print("Inicializando o banco de dados...")
    
    try:
        # Inicializa o banco de dados e tabelas
        db.initialize_database()
        
        # Usuários padrão para inicializar o sistema
        default_users = [
            {
                'email': 'admin@meetcall.com',
                'password': 'admin123',
                'name': 'Administrador'
            },
            {
                'email': 'usuario@meetcall.com',
                'password': 'user123',
                'name': 'Usuário Teste'
            }
        ]
        
        print("\nCriando usuários padrão...")
        
        for user_data in default_users:
            try:
                user_id = db.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    name=user_data['name']
                )
                print(f"✓ Usuário criado: {user_data['email']} (ID: {user_id})")
            
            except ValueError as e:
                print(f"⚠ Usuário {user_data['email']} já existe")
            except Exception as e:
                print(f"✗ Erro ao criar usuário {user_data['email']}: {e}")
        
        print("\n" + "="*50)
        print("🎉 Sistema inicializado com sucesso!")
        print("="*50)
        print("\nCredenciais de acesso:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("👤 Administrador:")
        print("   Email: admin@meetcall.com")
        print("   Senha: admin123")
        print()
        print("👤 Usuário Teste:")
        print("   Email: usuario@meetcall.com")
        print("   Senha: user123")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Erro ao inicializar o sistema: {e}")
        return False
    
    return True

if __name__ == '__main__':
    initialize_system()