"""
Executa migration 009: UNIQUE em tipos_servicos e prazo_dias em contas_receber
"""
from database import DatabaseManager

def main():
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("=== MIGRATION 009 ===\n")
        
        # 1. Verificar duplicatas em tipos_servicos
        print("1. Verificando duplicatas em tipos_servicos...")
        cursor.execute("""
            SELECT nome, COUNT(*) as total 
            FROM tipos_servicos 
            GROUP BY nome 
            HAVING COUNT(*) > 1
        """)
        duplicatas = cursor.fetchall()
        
        if duplicatas:
            print(f"   ⚠️  ATENÇÃO: {len(duplicatas)} nome(s) duplicado(s) encontrado(s):")
            for nome, total in duplicatas:
                print(f"      - '{nome}': {total} registros")
            print("\n   Resolva as duplicatas antes de continuar.")
            return
        else:
            print("   ✓ Nenhuma duplicata encontrada\n")
        
        # 2. Adicionar UNIQUE constraint
        print("2. Adicionando constraint UNIQUE em tipos_servicos.nome...")
        try:
            cursor.execute("""
                ALTER TABLE tipos_servicos 
                ADD UNIQUE INDEX idx_nome_unique (nome)
            """)
            print("   ✓ Constraint UNIQUE adicionada com sucesso\n")
        except Exception as e:
            if "Duplicate entry" in str(e) or "1062" in str(e):
                print(f"   ⚠️  Erro: {e}")
                print("   Resolva as duplicatas manualmente.\n")
                return
            elif "Duplicate key name" in str(e):
                print("   ℹ️  Constraint já existe\n")
            else:
                raise
        
        # 3. Adicionar campo prazo_dias
        print("3. Adicionando campo prazo_dias em contas_receber...")
        try:
            cursor.execute("""
                ALTER TABLE contas_receber 
                ADD COLUMN prazo_dias INT DEFAULT 30 
                COMMENT 'Prazo em dias para vencimento (ex: 15, 30, 45, 60, 90, 120)' 
                AFTER data_emissao
            """)
            print("   ✓ Campo prazo_dias adicionado\n")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("   ℹ️  Campo prazo_dias já existe\n")
            else:
                raise
        
        # 4. Calcular prazo_dias para registros existentes
        print("4. Calculando prazo_dias para registros existentes...")
        cursor.execute("""
            UPDATE contas_receber 
            SET prazo_dias = DATEDIFF(data_vencimento, data_emissao)
            WHERE data_emissao IS NOT NULL 
            AND data_vencimento IS NOT NULL
            AND prazo_dias IS NULL
        """)
        print(f"   ✓ {cursor.rowcount} registros atualizados\n")
        
        # 5. Corrigir valores NULL ou negativos
        print("5. Corrigindo valores NULL ou negativos...")
        cursor.execute("""
            UPDATE contas_receber 
            SET prazo_dias = 30 
            WHERE prazo_dias IS NULL OR prazo_dias < 0
        """)
        if cursor.rowcount > 0:
            print(f"   ✓ {cursor.rowcount} registros corrigidos para 30 dias\n")
        else:
            print("   ✓ Nenhum registro necessitou correção\n")
        
        # 6. Adicionar índice
        print("6. Adicionando índice em prazo_dias...")
        try:
            cursor.execute("""
                CREATE INDEX idx_prazo_dias ON contas_receber(prazo_dias)
            """)
            print("   ✓ Índice criado com sucesso\n")
        except Exception as e:
            if "Duplicate key name" in str(e):
                print("   ℹ️  Índice já existe\n")
            else:
                raise
        
        conn.commit()
        
        print("=" * 50)
        print("✅ MIGRATION 009 CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print("\nAlterações aplicadas:")
        print("  1. tipos_servicos.nome agora é UNIQUE")
        print("  2. contas_receber.prazo_dias adicionado")
        print("  3. Registros existentes atualizados")

if __name__ == "__main__":
    main()
