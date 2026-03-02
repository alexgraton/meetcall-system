from models.tipo_servico import TipoServicoModel
from database import DatabaseManager

print("=== TESTE DAS ALTERAÇÕES ===\n")

# Teste 1: UNIQUE constraint em tipos_servicos
print("1. Testando UNIQUE constraint em tipos_servicos...")
try:
    TipoServicoModel.create('Brindes', 'Teste duplicata', None, 'despesa', 'TEST01')
    print("   ❌ ERRO: Permitiu criar duplicata!\n")
except Exception as e:
    print(f"   ✓ UNIQUE constraint funcionando: {str(e)[:100]}\n")

# Teste 2: Campo prazo_dias em contas_receber
print("2. Verificando campo prazo_dias em contas_receber...")
db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM contas_receber LIKE 'prazo_dias'")
    campo = cursor.fetchone()
    if campo:
        print(f"   ✓ Campo prazo_dias existe: {campo}\n")
    else:
        print("   ❌ Campo prazo_dias não encontrado\n")

print("=" * 50)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 50)
