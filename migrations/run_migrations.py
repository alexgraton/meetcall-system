#!/usr/bin/env python3
"""
Aplica migrations SQL contidas na pasta migrations/ em ordem alfabética
"""
import os
import sys
from pathlib import Path

# Garantir que o diretório raiz do projeto esteja no sys.path para importar modules locais
ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import db

MIGRATIONS_DIR = Path(__file__).parent

def run_migration_file(path: Path):
    print(f"Aplicando migration: {path.name}")
    sql = path.read_text(encoding='utf-8')
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Aviso/error ao executar stmt: {e}")
        conn.commit()
    print(f"OK: {path.name}\n")


def main():
    files = sorted([p for p in MIGRATIONS_DIR.glob('*.sql')])
    if not files:
        print('Nenhuma migration encontrada em', MIGRATIONS_DIR)
        return
    for f in files:
        run_migration_file(f)

if __name__ == '__main__':
    main()
