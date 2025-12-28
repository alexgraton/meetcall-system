"""
Script para verificar estrutura das tabelas contas_pagar e contas_receber
"""

from database import DatabaseManager

def verificar_estrutura():
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 80)
        print("ESTRUTURA DA TABELA: contas_receber")
        print("=" * 80)
        cursor.execute("DESCRIBE contas_receber")
        for field in cursor.fetchall():
            print(f"{field['Field']:30} {field['Type']:20} {field['Null']:5} {field['Key']:5}")
        
        print("\n" + "=" * 80)
        print("ESTRUTURA DA TABELA: contas_pagar")
        print("=" * 80)
        cursor.execute("DESCRIBE contas_pagar")
        for field in cursor.fetchall():
            print(f"{field['Field']:30} {field['Type']:20} {field['Null']:5} {field['Key']:5}")

if __name__ == "__main__":
    verificar_estrutura()
