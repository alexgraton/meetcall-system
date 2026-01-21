"""Script para testar o módulo de auditoria"""
from models.auditoria import AuditoriaModel

def test_listar_logs():
    """Testa listagem de logs"""
    try:
        print("Testando listar_logs...")
        logs = AuditoriaModel.listar_logs(limit=5)
        print(f"✓ Retornou {len(logs)} logs")
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_contar_logs():
    """Testa contagem de logs"""
    try:
        print("\nTestando contar_logs...")
        total = AuditoriaModel.contar_logs()
        print(f"✓ Total de logs: {total}")
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def test_estatisticas():
    """Testa obtenção de estatísticas"""
    try:
        print("\nTestando obter_estatisticas...")
        stats = AuditoriaModel.obter_estatisticas()
        print(f"✓ Estatísticas retornadas:")
        print(f"  - Ações: {stats.get('acoes', [])}")
        print(f"  - Usuários ativos: {len(stats.get('usuarios_ativos', []))}")
        print(f"  - Tabelas: {len(stats.get('tabelas_modificadas', []))}")
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("TESTE DO MÓDULO DE AUDITORIA")
    print("=" * 50)
    
    test_listar_logs()
    test_contar_logs()
    test_estatisticas()
    
    print("\n" + "=" * 50)
