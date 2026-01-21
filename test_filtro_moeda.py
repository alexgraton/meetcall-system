"""Teste do filtro de formatação monetária"""
from app import app

# Testar o filtro
with app.app_context():
    filtro_moeda = app.jinja_env.filters['moeda']
    
    # Testes
    valores = [
        (147000.00, "147.000,00"),
        (1500.50, "1.500,50"),
        (50.00, "50,00"),
        (1234567.89, "1.234.567,89"),
        (0, "0,00"),
        (None, "0,00"),
    ]
    
    print("Testando filtro de formatação monetária:")
    print("=" * 60)
    
    todos_ok = True
    for valor, esperado in valores:
        resultado = filtro_moeda(valor)
        status = "✓" if resultado == esperado else "✗"
        if resultado != esperado:
            todos_ok = False
        valor_str = str(valor) if valor is not None else "None"
        print(f"{status} Valor: {valor_str:>15} | Esperado: {esperado:>20} | Resultado: {resultado}")
    
    print("=" * 60)
    if todos_ok:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")
