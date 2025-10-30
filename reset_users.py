#!/usr/bin/env python3
"""
Script para resetar usuários do banco de dados
⚠️ CUIDADO: Este script apaga TODOS os usuários!
"""

from database import db
import sys

def reset_users():
    """Remove todos os usuários do banco"""
    
    print("="*60)
    print("⚠️  RESETAR USUÁRIOS - MEETCALL SYSTEM")
    print("="*60)
    print("\n🚨 ATENÇÃO: Esta operação irá DELETAR TODOS os usuários!")
    print()
    
    confirm = input("Digite 'CONFIRMAR' para continuar: ").strip()
    
    if confirm != 'CONFIRMAR':
        print("\n❌ Operação cancelada!")
        return False
    
    try:
        with db.get_connection() as connection:
            cursor = connection.cursor()
            
            # Lista usuários antes de deletar
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            print(f"\n🔍 Encontrados {count} usuário(s) no banco")
            
            # Deleta todos os usuários
            cursor.execute("DELETE FROM users")
            connection.commit()
            
            print(f"✅ {cursor.rowcount} usuário(s) removido(s)")
            print("\n" + "="*60)
            print("✅ RESET CONCLUÍDO!")
            print("="*60)
            print("\n💡 Execute 'python init_database.py' para recriar usuários")
            print()
            
            return True
    
    except Exception as e:
        print(f"\n❌ Erro ao resetar usuários: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        reset_users()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        sys.exit(1)
