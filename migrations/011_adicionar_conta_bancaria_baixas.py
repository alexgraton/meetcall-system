"""
Migração 011: Adicionar campo conta_bancaria_id para vincular baixas às contas bancárias
Data: 2025-12-27

Conceito: A conta bancária é vinculada apenas no momento da BAIXA (pagamento/recebimento),
não no cadastro da conta. Isso segue o princípio de Regime de Caixa para movimentações bancárias.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

def upgrade():
    """Aplica a migração"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("Iniciando migração 011...")
        
        # 1. Adicionar conta_bancaria_id em contas_pagar
        print("1. Adicionando conta_bancaria_id em contas_pagar...")
        cursor.execute("""
            ALTER TABLE contas_pagar
            ADD COLUMN conta_bancaria_id INT NULL AFTER conta_contabil_id,
            ADD FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id)
        """)
        
        cursor.execute("""
            ALTER TABLE contas_pagar
            ADD INDEX idx_conta_bancaria (conta_bancaria_id)
        """)
        
        # 2. Adicionar conta_bancaria_id em contas_receber
        print("2. Adicionando conta_bancaria_id em contas_receber...")
        cursor.execute("""
            ALTER TABLE contas_receber
            ADD COLUMN conta_bancaria_id INT NULL AFTER conta_contabil_id,
            ADD FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(id)
        """)
        
        cursor.execute("""
            ALTER TABLE contas_receber
            ADD INDEX idx_conta_bancaria (conta_bancaria_id)
        """)
        
        # 3. Adicionar campo referencia para controle de margem gerencial
        print("3. Adicionando campo referencia (MM/AAAA)...")
        cursor.execute("""
            ALTER TABLE contas_pagar
            ADD COLUMN referencia VARCHAR(7) NULL COMMENT 'Período de referência MM/AAAA' AFTER data_vencimento
        """)
        
        cursor.execute("""
            ALTER TABLE contas_receber
            ADD COLUMN referencia VARCHAR(7) NULL COMMENT 'Período de referência MM/AAAA' AFTER data_vencimento
        """)
        
        cursor.execute("""
            ALTER TABLE contas_pagar
            ADD INDEX idx_referencia (referencia)
        """)
        
        cursor.execute("""
            ALTER TABLE contas_receber
            ADD INDEX idx_referencia (referencia)
        """)
        
        conn.commit()
        print("✓ Migração 011 concluída com sucesso!")
        print("")
        print("📌 IMPORTANTE:")
        print("   - conta_bancaria_id é preenchida apenas na BAIXA (pagamento/recebimento)")
        print("   - referencia (MM/AAAA) é usada para análise de margem gerencial")
        print("")

def downgrade():
    """Reverte a migração"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("Revertendo migração 011...")
        
        # Remover campos de contas_pagar
        cursor.execute("""
            ALTER TABLE contas_pagar
            DROP FOREIGN KEY contas_pagar_ibfk_5
        """)
        
        cursor.execute("""
            ALTER TABLE contas_pagar
            DROP COLUMN conta_bancaria_id,
            DROP COLUMN referencia
        """)
        
        # Remover campos de contas_receber
        cursor.execute("""
            ALTER TABLE contas_receber
            DROP FOREIGN KEY contas_receber_ibfk_5
        """)
        
        cursor.execute("""
            ALTER TABLE contas_receber
            DROP COLUMN conta_bancaria_id,
            DROP COLUMN referencia
        """)
        
        conn.commit()
        print("✓ Migração 011 revertida")

if __name__ == '__main__':
    import sys
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'down':
            downgrade()
        else:
            upgrade()
    except Exception as e:
        print(f"❌ Erro na migração: {str(e)}")
        sys.exit(1)
