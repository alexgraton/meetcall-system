"""
Script para analisar extratos bancários com melhor parsing
"""
import pandas as pd

def analisar_itau(arquivo):
    print(f"\n{'='*80}")
    print(f"🏦 ITAÚ - {arquivo}")
    print('='*80)
    
    # Ler pulando as primeiras linhas de cabeçalho
    df = pd.read_excel(arquivo, sheet_name='Lançamentos', skiprows=6)
    
    print(f"\n📋 Colunas: {list(df.columns)}")
    print(f"📊 Total de lançamentos: {len(df)}")
    print(f"\n🔍 Primeiros 10 lançamentos:")
    print(df.head(10).to_string())
    
    print(f"\n📝 Exemplo de tipos de lançamento:")
    if 'Unnamed: 2' in df.columns:
        print(df['Unnamed: 2'].value_counts().head(10))

def analisar_bb(arquivo):
    print(f"\n{'='*80}")
    print(f"🏦 BANCO DO BRASIL - {arquivo}")
    print('='*80)
    
    # Ler pulando as primeiras linhas de cabeçalho
    df = pd.read_excel(arquivo, sheet_name='Extrato', skiprows=2)
    
    print(f"\n📋 Colunas: {list(df.columns)}")
    print(f"📊 Total de lançamentos: {len(df)}")
    print(f"\n🔍 Primeiros 15 lançamentos:")
    print(df.head(15).to_string())
    
    # Analisar tipos de histórico
    print(f"\n📝 Tipos de histórico encontrados:")
    if 'Historico' in df.columns or 'Unnamed: 7' in df.columns:
        col_hist = 'Historico' if 'Historico' in df.columns else 'Unnamed: 7'
        print(df[col_hist].value_counts().head(15))

if __name__ == '__main__':
    analisar_itau('Extrato ITAU.xlsx')
    analisar_bb('Extrato BB FILIAL.xlsx')
    analisar_bb('Extrato  BB MATRIZ.xlsx')
    
    print("\n" + "="*80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("="*80)
