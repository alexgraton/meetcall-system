#!/usr/bin/env python3
"""
Script para criar novos usuários no MeetCall System
"""

from database import db
import getpass
import sys

def create_new_user():
    """Cria um novo usuário no sistema"""
    
    print("="*60)
    print("👤 CRIAR NOVO USUÁRIO - MEETCALL SYSTEM")
    print("="*60)
    print()
    
    try:
        # Solicita informações do usuário
        email = input("Email do usuário: ").strip()
        
        if not email:
            print("❌ Email é obrigatório!")
            return False
        
        name = input("Nome completo: ").strip()
        
        if not name:
            print("❌ Nome é obrigatório!")
            return False
        
        # Solicita senha
        while True:
            password = getpass.getpass("Senha (mínimo 6 caracteres): ").strip()
            
            if len(password) < 6:
                print("❌ A senha deve ter no mínimo 6 caracteres. Tente novamente.\n")
                continue
            
            password_confirm = getpass.getpass("Confirme a senha: ").strip()
            
            if password != password_confirm:
                print("❌ As senhas não conferem. Tente novamente.\n")
                continue
            
            break
        
        # Solicita perfil
        print("\n📋 Perfil do usuário:")
        print("  1 - Usuário (padrão)")
        print("  2 - Administrador")
        role_choice = input("Escolha o perfil [1]: ").strip() or "1"
        role = 'admin' if role_choice == '2' else 'user'
        
        # Cria o usuário
        print("\n📝 Criando usuário...")
        
        user_id = db.create_user(
            email=email,
            password=password,
            name=name,
            role=role
        )
        
        print("\n" + "="*60)
        print("✅ USUÁRIO CRIADO COM SUCESSO!")
        print("="*60)
        print(f"\n👤 {name}")
        print(f"   Perfil: {'Administrador' if role == 'admin' else 'Usuário'}")
        print(f"   Email: {email}")
        print(f"   ID: {user_id}")
        print("\n" + "="*60)
        print("💡 O usuário já pode fazer login no sistema!")
        print()
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Erro: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_users():
    """Lista todos os usuários do sistema"""
    
    print("="*60)
    print("👥 USUÁRIOS DO SISTEMA")
    print("="*60)
    
    try:
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, email, name, role, created_at, is_active 
                FROM users 
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            
            if not users:
                print("\n⚠️  Nenhum usuário cadastrado")
                return
            
            print(f"\n📊 Total de usuários: {len(users)}\n")
            print("-"*60)
            
            for user in users:
                status = "✅ Ativo" if user['is_active'] else "❌ Inativo"
                perfil = "👑 Admin" if user['role'] == 'admin' else "👤 Usuário"
                print(f"\n{perfil} {user['name']} ({status})")
                print(f"   ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Criado em: {user['created_at']}")
            
            print("\n" + "="*60)
    
    except Exception as e:
        print(f"\n❌ Erro ao listar usuários: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_users()
    else:
        create_new_user()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        sys.exit(1)
