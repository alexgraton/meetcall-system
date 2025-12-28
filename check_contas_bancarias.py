"""Script para verificar estrutura da tabela contas_bancarias"""
from database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DESCRIBE contas_bancarias")
    fields = cursor.fetchall()
    
    print("=" * 80)
    print("ESTRUTURA DA TABELA: contas_bancarias")
    print("=" * 80)
    for field in fields:
        print(f"{field['Field']:30} {field['Type']:20} {field['Null']:5} {field['Key']:5}")
    
    print("\n" + "=" * 80)
    print("DADOS DA TABELA: contas_bancarias (primeiros 5 registros)")
    print("=" * 80)
    cursor.execute("SELECT * FROM contas_bancarias LIMIT 5")
    contas = cursor.fetchall()
    
    if contas:
        for conta in contas:
            print(f"\nID: {conta['id']}")
            for key, value in conta.items():
                if key != 'id':
                    print(f"  {key}: {value}")
    else:
        print("Nenhuma conta bancária encontrada")
    
    cursor.close()
