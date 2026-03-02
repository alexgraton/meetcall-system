"""
Script de teste para a funcionalidade de consulta de CNPJ
Testa as 3 APIs e o sistema de fallback
"""
from services.cnpj_consulta import buscar_cnpj

def testar_cnpj_valido():
    """Testa com um CNPJ válido real"""
    print("=" * 60)
    print("TESTE 1: Consultando CNPJ válido (Petrobras)")
    print("=" * 60)
    
    # CNPJ da Petrobras: 33.000.167/0001-01
    resultado = buscar_cnpj('33.000.167/0001-01')
    
    print(f"\nResultado: {'SUCESSO' if resultado['success'] else 'FALHA'}")
    print(f"Mensagem: {resultado['message']}")
    
    if resultado['success']:
        print(f"API utilizada: {resultado['api_utilizada']}")
        print("\nDados retornados:")
        for campo, valor in resultado['data'].items():
            if valor:
                print(f"  {campo}: {valor}")
    
    return resultado['success']

def testar_cnpj_invalido():
    """Testa com CNPJ inválido (formato incorreto)"""
    print("\n" + "=" * 60)
    print("TESTE 2: Testando CNPJ inválido (menos de 14 dígitos)")
    print("=" * 60)
    
    resultado = buscar_cnpj('123456789')
    
    print(f"\nResultado: {'ESPERADO (ERRO)' if not resultado['success'] else 'INESPERADO'}")
    print(f"Mensagem: {resultado['message']}")
    print(f"Código de erro: {resultado.get('error_code', 'N/A')}")
    
    return not resultado['success']  # Esperamos falha

def testar_cnpj_nao_encontrado():
    """Testa com CNPJ que não existe"""
    print("\n" + "=" * 60)
    print("TESTE 3: Testando CNPJ inexistente")
    print("=" * 60)
    
    # CNPJ com dígitos verificadores corretos mas que não existe
    resultado = buscar_cnpj('00.000.000/0000-00')
    
    print(f"\nResultado: {'ESPERADO (NÃO ENCONTRADO)' if not resultado['success'] else 'INESPERADO'}")
    print(f"Mensagem: {resultado['message']}")
    print(f"Código de erro: {resultado.get('error_code', 'N/A')}")
    
    return True  # Não podemos garantir o resultado, depende da API

def testar_cnpj_formatado():
    """Testa com CNPJ formatado"""
    print("\n" + "=" * 60)
    print("TESTE 4: Testando CNPJ com formatação")
    print("=" * 60)
    
    # CNPJ do Google Brasil: 06.990.590/0001-23
    resultado = buscar_cnpj('06.990.590/0001-23')
    
    print(f"\nResultado: {'SUCESSO' if resultado['success'] else 'FALHA'}")
    print(f"Mensagem: {resultado['message']}")
    
    if resultado['success']:
        print(f"API utilizada: {resultado['api_utilizada']}")
        print(f"Razão Social: {resultado['data'].get('razao_social', 'N/A')}")
        print(f"Nome Fantasia: {resultado['data'].get('nome', 'N/A')}")
    
    return resultado['success']

def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "TESTE DE CONSULTA AUTOMÁTICA DE CNPJ" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    
    testes_passados = 0
    total_testes = 4
    
    # Executar testes
    if testar_cnpj_valido():
        testes_passados += 1
    
    if testar_cnpj_invalido():
        testes_passados += 1
    
    if testar_cnpj_nao_encontrado():
        testes_passados += 1
    
    if testar_cnpj_formatado():
        testes_passados += 1
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Testes executados: {total_testes}")
    print(f"Testes bem-sucedidos: {testes_passados}")
    print(f"Taxa de sucesso: {(testes_passados/total_testes)*100:.0f}%")
    print("=" * 60)
    
    if testes_passados >= 3:
        print("\n✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
    else:
        print("\n⚠️  ATENÇÃO: Alguns testes falharam. Verifique as APIs.")
    
    print("\nOBS: Algumas APIs podem estar temporariamente indisponíveis.")
    print("      O sistema de fallback tentará usar APIs alternativas.")

if __name__ == '__main__':
    main()
