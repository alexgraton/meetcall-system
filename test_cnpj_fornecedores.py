"""
Teste rápido da funcionalidade de consulta de CNPJ em Fornecedores
"""
import sys
sys.path.append('c:\\meetcall-system')

from services.cnpj_consulta import buscar_cnpj

def testar_fornecedores():
    """Testa consulta de CNPJ para fornecedores"""
    print("=" * 60)
    print("TESTE: Consulta de CNPJ para Fornecedores")
    print("=" * 60)
    
    # CNPJ da Microsoft Brasil: 04.712.500/0001-07
    cnpj = '04.712.500/0001-07'
    print(f"\nConsultando CNPJ: {cnpj}")
    print("(Microsoft Brasil)\n")
    
    resultado = buscar_cnpj(cnpj)
    
    if resultado['success']:
        print("✅ SUCESSO!")
        print(f"API utilizada: {resultado['api_utilizada']}\n")
        print("Dados que serão preenchidos no formulário:")
        print("-" * 60)
        
        dados = resultado['data']
        print(f"Razão Social:  {dados.get('razao_social', 'N/A')}")
        print(f"Nome Fantasia: {dados.get('nome', 'N/A')}")
        print(f"CNPJ:          {dados.get('cnpj', 'N/A')}")
        print(f"Email:         {dados.get('email', 'N/A')}")
        print(f"Telefone:      {dados.get('telefone', 'N/A')}")
        print(f"CEP:           {dados.get('cep', 'N/A')}")
        print(f"Endereço:      {dados.get('rua', 'N/A')}, {dados.get('numero', 'N/A')}")
        print(f"Complemento:   {dados.get('complemento', 'N/A')}")
        print(f"Bairro:        {dados.get('bairro', 'N/A')}")
        print(f"Cidade:        {dados.get('cidade', 'N/A')}")
        print(f"Estado:        {dados.get('estado', 'N/A')}")
        print(f"Situação:      {dados.get('situacao', 'N/A')}")
        print(f"Atividade:     {dados.get('atividade_principal', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ Funcionalidade de Fornecedores está funcionando!")
        print("=" * 60)
        return True
    else:
        print("❌ ERRO!")
        print(f"Mensagem: {resultado['message']}")
        print(f"Código: {resultado.get('error_code', 'N/A')}")
        return False

if __name__ == '__main__':
    testar_fornecedores()
