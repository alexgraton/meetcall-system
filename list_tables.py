#!/usr/bin/env python3
"""Lista as tabelas do banco configurado em config.py """
from database import db

try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tabelas no banco:")
        if not tables:
            print("<nenhuma>")
        else:
            for t in tables:
                print(f"- {t}")
except Exception as e:
    print(f"Erro ao listar tabelas: {e}")
    import traceback
    traceback.print_exc()
