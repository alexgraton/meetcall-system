#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do MeetCall System
"""

from database import db
import getpass
import sys

def initialize_system(interactive=True):
    """Inicializa o sistema criando o banco e usuários padrão"""
    
    print("="*60)
    print("🚀 INICIALIZAÇÃO DO MEETCALL SYSTEM")
    print("="*60)
    print("\nInicializando o banco de dados...")
    
    try:
        # Inicializa o banco de dados e tabelas
        db.initialize_database()
        
        if interactive:
            print("\n" + "="*60)
            print("👤 CRIAÇÃO DO USUÁRIO ADMINISTRADOR")
            print("="*60)
            print("\nPor favor, configure o usuário administrador do sistema:\n")
            
            admin_email = input("Email do administrador [admin@meetcall.com]: ").strip() or "admin@meetcall.com"
            admin_name = input("Nome do administrador [Administrador]: ").strip() or "Administrador"
            
            while True:
                admin_password = getpass.getpass("Senha do administrador (mínimo 6 caracteres): ").strip()
                if len(admin_password) < 6:
                    print("❌ A senha deve ter no mínimo 6 caracteres. Tente novamente.\n")
                    continue
                    
                admin_password_confirm = getpass.getpass("Confirme a senha: ").strip()
                if admin_password != admin_password_confirm:
                    print("❌ As senhas não conferem. Tente novamente.\n")
                    continue
                break
            
            default_users = [
                {
                    'email': admin_email,
                    'password': admin_password,
                    'name': admin_name,
                    'role': 'admin'
                }
            ]
            
            # Perguntar se quer criar usuário de teste
            print("\n" + "-"*60)
            criar_teste = input("\nDeseja criar um usuário de teste? (s/N): ").strip().lower()
            
            if criar_teste in ['s', 'sim', 'y', 'yes']:
                test_email = input("Email do usuário teste [usuario@meetcall.com]: ").strip() or "usuario@meetcall.com"
                test_name = input("Nome do usuário teste [Usuário Teste]: ").strip() or "Usuário Teste"
                test_password = getpass.getpass("Senha do usuário teste: ").strip() or "teste123"
                
                default_users.append({
                    'email': test_email,
                    'password': test_password,
                    'name': test_name,
                    'role': 'user'
                })
        else:
            # Modo não interativo - usa senhas padrão (apenas para desenvolvimento)
            print("\n⚠️  MODO NÃO INTERATIVO - USANDO CREDENCIAIS PADRÃO")
            print("   (Altere as senhas após o primeiro login!)\n")
            
            default_users = [
                {
                    'email': 'admin@meetcall.com',
                    'password': 'Admin@123',
                    'name': 'Administrador',
                    'role': 'admin'
                }
            ]
        
        print("\n" + "="*60)
        print("📝 Criando usuários...")
        print("="*60)
        
        created_users = []
        
        for user_data in default_users:
            try:
                user_id = db.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    name=user_data['name'],
                    role=user_data.get('role', 'user')
                )
                print(f"✓ Usuário criado: {user_data['email']} (ID: {user_id}) - Perfil: {user_data.get('role', 'user')}")
                created_users.append(user_data)
            
            except ValueError as e:
                print(f"⚠ Usuário {user_data['email']} já existe")
            except Exception as e:
                print(f"✗ Erro ao criar usuário {user_data['email']}: {e}")
        
        print("\n" + "="*60)
        print("🎉 SISTEMA INICIALIZADO COM SUCESSO!")
        print("="*60)
        
        if created_users:
            print("\n✅ Usuários criados:")
            print("-"*60)
            for user in created_users:
                print(f"👤 {user['name']}")
                print(f"   Email: {user['email']}")
            print("="*60)
        
        print("\n💡 Dica: Acesse http://localhost:5000 para fazer login")
        print()
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar o sistema: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    # Verifica se foi passado o argumento --no-interactive
    interactive = '--no-interactive' not in sys.argv
    initialize_system(interactive=interactive)