#!/usr/bin/env python3
"""Script para atualizar usuários existentes com roles"""

from database import db

print("Atualizando usuários existentes...")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Define admin para o usuário admin@meetcall.com
    cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@meetcall.com'")
    
    # Define user para todos os outros
    cursor.execute("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''")
    
    conn.commit()
    
print("✅ Usuários atualizados com sucesso!")
print("   - admin@meetcall.com: admin")
print("   - demais usuários: user")
