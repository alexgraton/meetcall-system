#!/usr/bin/env python3
"""
Script para alterar senha de usuário no MeetCall System
"""

from database import db
import getpass
import sys

def change_password():
    """Altera a senha de um usuário"""
    
    print("="*60)
    print("🔐 ALTERAR SENHA - MEETCALL SYSTEM")
    print("="*60)
    print()
    
    try:
        # Solicita o email do usuário
        email = input("Email do usuário: ").strip()
        
        if not email:
            print("❌ Email é obrigatório!")
            return False
        
        # Verifica se o usuário existe
        user = db.get_user_by_email(email)
        
        if not user:
            print(f"❌ Usuário com email '{email}' não encontrado!")
            return False
        
        print(f"\n👤 Usuário encontrado: {user['name']}")
        print("-"*60)
        
        # Solicita nova senha
        while True:
            new_password = getpass.getpass("\nNova senha (mínimo 6 caracteres): ").strip()
            
            if len(new_password) < 6:
                print("❌ A senha deve ter no mínimo 6 caracteres. Tente novamente.")
                continue
            
            confirm_password = getpass.getpass("Confirme a nova senha: ").strip()
            
            if new_password != confirm_password:
                print("❌ As senhas não conferem. Tente novamente.")
                continue
            
            break
        
        # Atualiza a senha
        print("\n🔄 Atualizando senha...")
        
        if db.update_user_password(email, new_password):
            print("\n" + "="*60)
            print("✅ SENHA ALTERADA COM SUCESSO!")
            print("="*60)
            print(f"\n👤 {user['name']}")
            print(f"   Email: {email}")
            print("\n💡 Use a nova senha no próximo login!")
            print("="*60)
            print()
            return True
        else:
            print("\n❌ Erro ao atualizar senha!")
            return False
        
    except Exception as e:
        print(f"\n❌ Erro ao alterar senha: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        change_password()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        sys.exit(1)
