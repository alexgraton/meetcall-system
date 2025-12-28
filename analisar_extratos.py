"""
Script para analisar estrutura dos extratos bancários
"""
import pandas as pd
import sys

def analisar_extrato(arquivo):
    print(f"\n{'='*80}")
    print(f"ANALISANDO: {arquivo}")
    print('='*80)
    
    try:
        # Tentar ler o arquivo
        xl = pd.ExcelFile(arquivo)
        print(f"\n📋 Planilhas encontradas: {xl.sheet_names}")
        
        # Para cada planilha
        for sheet_name in xl.sheet_names:
            print(f"\n🔹 Planilha: {sheet_name}")
            print("-" * 80)
            
            # Ler a planilha
            df = pd.read_excel(arquivo, sheet_name=sheet_name)
            
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"\nColunas encontradas:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")
            
            print(f"\n📊 Primeiras 5 linhas:")
            print(df.head(5).to_string())
            
            print(f"\n📊 Tipos de dados:")
            print(df.dtypes)
            
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")

if __name__ == '__main__':
    arquivos = [
        'Extrato ITAU.xlsx',
        'Extrato BB FILIAL.xlsx',
        'Extrato  BB MATRIZ.xlsx'
    ]
    
    for arquivo in arquivos:
        analisar_extrato(arquivo)
    
    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA")
    print("="*80)
