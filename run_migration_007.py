"""
Script para executar migration 007
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

def main():
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            print("🔄 Iniciando migração 007: Ajuste para Call Center...")
            print("   ➜ Removendo colunas aliquota e margem_esperada...")
            
            # Remover coluna aliquota
            try:
                cursor.execute("ALTER TABLE tipos_servicos DROP COLUMN aliquota")
                print("   ✓ Coluna 'aliquota' removida")
            except Exception as e:
                if "doesn't exist" in str(e).lower() or "unknown column" in str(e).lower():
                    print("   ℹ️  Coluna 'aliquota' já não existe")
                else:
                    raise
            
            # Remover coluna margem_esperada
            try:
                cursor.execute("ALTER TABLE tipos_servicos DROP COLUMN margem_esperada")
                print("   ✓ Coluna 'margem_esperada' removida")
            except Exception as e:
                if "doesn't exist" in str(e).lower() or "unknown column" in str(e).lower():
                    print("   ℹ️  Coluna 'margem_esperada' já não existe")
                else:
                    raise
            
            conn.commit()
            print("\n✅ Migração 007 concluída com sucesso!")
            print("📋 Tipos de Serviços agora representa Categorias de Despesas")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Erro na migração 007: {str(e)}")
            
        finally:
            cursor.close()

if __name__ == '__main__':
    main()
