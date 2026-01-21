"""
Script para atualizar campo referencia nas contas a pagar existentes
"""
from database import DatabaseManager

def atualizar_referencias():
    """Atualiza o campo referencia para 11/2025 para testes"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar contas sem referencia
        cursor.execute("""
            SELECT id, data_vencimento 
            FROM contas_pagar 
            WHERE referencia IS NULL OR referencia = ''
        """)
        
        contas = cursor.fetchall()
        
        print(f"Encontradas {len(contas)} contas a pagar sem referência")
        
        # Atualizar todas para 11/2025 para testes
        referencia_teste = '11/2025'
        
        if contas:
            cursor.execute("""
                UPDATE contas_pagar 
                SET referencia = %s 
                WHERE referencia IS NULL OR referencia = ''
            """, (referencia_teste,))
            
            conn.commit()
            print(f"\n✅ {len(contas)} contas atualizadas com referência {referencia_teste} para testes!")
        else:
            print("\nNenhuma conta sem referência encontrada.")

if __name__ == '__main__':
    atualizar_referencias()
