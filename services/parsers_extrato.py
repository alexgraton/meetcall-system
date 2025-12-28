"""
Parsers para extratos bancários
Cada banco tem seu formato específico de extrato
"""
import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List, Dict
import re

class ParserExtratoBase:
    """Classe base para parsers de extrato"""
    
    def __init__(self, arquivo_path: str):
        self.arquivo_path = arquivo_path
        self.nome_arquivo = arquivo_path.split('\\')[-1].split('/')[-1]
    
    def parse(self) -> List[Dict]:
        """
        Método abstrato que deve ser implementado por cada parser específico
        
        Returns:
            List[Dict]: Lista de lançamentos processados com estrutura padrão:
                - data_lancamento: date
                - historico: str
                - valor: Decimal
                - tipo_movimento: 'credito' ou 'debito'
                - documento: str (opcional)
                - complemento: str (opcional)
                - saldo_apos: Decimal (opcional)
        """
        raise NotImplementedError()
    
    def limpar_valor(self, valor_str) -> Decimal:
        """Converte string de valor para Decimal"""
        if pd.isna(valor_str) or valor_str is None or valor_str == '':
            return Decimal('0')
        
        # Remove espaços e converte para string
        valor_str = str(valor_str).strip()
        
        # Remove pontos de milhar e substitui vírgula por ponto
        valor_str = valor_str.replace('.', '').replace(',', '.')
        
        # Remove caracteres não numéricos exceto ponto e sinal negativo
        valor_str = re.sub(r'[^\d.-]', '', valor_str)
        
        try:
            return Decimal(valor_str)
        except:
            return Decimal('0')
    
    def converter_data(self, data_str) -> datetime:
        """Converte string de data para datetime"""
        if pd.isna(data_str):
            return None
        
        # Tentar diferentes formatos
        formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        
        data_str = str(data_str).strip()
        
        for formato in formatos:
            try:
                return datetime.strptime(data_str, formato).date()
            except:
                continue
        
        return None


class ParserItau(ParserExtratoBase):
    """Parser para extratos do Itaú"""
    
    def parse(self) -> List[Dict]:
        # Ler arquivo Excel pulando cabeçalho
        df = pd.read_excel(self.arquivo_path, sheet_name='Lançamentos', skiprows=6)
        
        lancamentos = []
        
        # A partir da linha que tem "Data" como primeiro campo, são os lançamentos
        inicio_dados = None
        for idx, row in df.iterrows():
            if str(row.iloc[0]).strip() == 'Data':
                inicio_dados = idx + 1
                break
        
        if inicio_dados is None:
            return []
        
        # Processar lançamentos
        for idx in range(inicio_dados, len(df)):
            row = df.iloc[idx]
            
            # Pular linhas vazias ou totalizadoras
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() in ['', 'Periodo:', 'Lançamentos']:
                continue
            
            data = self.converter_data(row.iloc[0])
            if data is None:
                continue
            
            lancamento_tipo = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else ''
            razao_social = str(row.iloc[2]) if not pd.isna(row.iloc[2]) else ''
            cpf_cnpj = str(row.iloc[3]) if not pd.isna(row.iloc[3]) else ''
            valor = self.limpar_valor(row.iloc[4])
            saldo = self.limpar_valor(row.iloc[5]) if len(row) > 5 else None
            
            # Determinar tipo de movimento (valor negativo = débito)
            tipo_movimento = 'debito' if valor < 0 else 'credito'
            valor_abs = abs(valor)
            
            # Montar histórico
            historico = f"{lancamento_tipo}"
            if razao_social and razao_social != 'nan':
                historico += f" - {razao_social}"
            
            complemento = f"CPF/CNPJ: {cpf_cnpj}" if cpf_cnpj and cpf_cnpj != 'nan' else None
            
            lancamentos.append({
                'data_lancamento': data,
                'historico': historico.strip(),
                'valor': valor_abs,
                'tipo_movimento': tipo_movimento,
                'documento': cpf_cnpj if cpf_cnpj != 'nan' else None,
                'complemento': complemento,
                'saldo_apos': saldo,
                'banco_origem': 'ITAU'
            })
        
        return lancamentos


class ParserBancoBrasil(ParserExtratoBase):
    """Parser para extratos do Banco do Brasil"""
    
    def parse(self) -> List[Dict]:
        # Ler arquivo Excel pulando cabeçalho
        df = pd.read_excel(self.arquivo_path, sheet_name='Extrato', skiprows=2)
        
        lancamentos = []
        
        for idx, row in df.iterrows():
            # Pular saldo anterior e linhas vazias
            if pd.isna(row['Data']) or 'Saldo Anterior' in str(row.get('Historico', '')):
                continue
            
            # Pular linha de SALDO final
            if 'S A L D O' in str(row.get('Historico', '')):
                continue
            
            data = self.converter_data(row['Data'])
            if data is None:
                continue
            
            historico = str(row.get('Historico', '')) if not pd.isna(row.get('Historico')) else ''
            valor_str = str(row.get('Valor R$ ', '0'))
            tipo_str = str(row.get('Inf.', '')).strip().upper()
            detalhamento = str(row.get('Detalhamento Hist.', '')) if not pd.isna(row.get('Detalhamento Hist.')) else ''
            documento = str(row.get('Numero Documento', '')) if not pd.isna(row.get('Numero Documento')) else ''
            codigo_hist = str(row.get('Cod. Historico', '')) if not pd.isna(row.get('Cod. Historico')) else ''
            
            valor = self.limpar_valor(valor_str)
            
            # Determinar tipo de movimento (C = crédito, D = débito)
            tipo_movimento = 'credito' if tipo_str == 'C' else 'debito'
            
            # Complemento com detalhamento
            complemento_parts = []
            if detalhamento and detalhamento != 'nan':
                complemento_parts.append(detalhamento)
            if codigo_hist and codigo_hist != 'nan':
                complemento_parts.append(f"Cód: {codigo_hist}")
            
            complemento = ' | '.join(complemento_parts) if complemento_parts else None
            
            lancamentos.append({
                'data_lancamento': data,
                'historico': historico.strip(),
                'valor': valor,
                'tipo_movimento': tipo_movimento,
                'documento': documento if documento != 'nan' else None,
                'complemento': complemento,
                'saldo_apos': None,  # BB não fornece saldo por linha neste formato
                'banco_origem': 'BANCO DO BRASIL',
                'codigo_historico': codigo_hist if codigo_hist != 'nan' else None
            })
        
        return lancamentos


def detectar_banco(arquivo_path: str) -> str:
    """
    Detecta qual banco baseado no conteúdo do arquivo
    
    Returns:
        str: 'itau', 'banco_brasil', ou 'desconhecido'
    """
    try:
        # Tentar ler as primeiras linhas
        xl = pd.ExcelFile(arquivo_path)
        
        # Itaú tem planilha "Lançamentos"
        if 'Lançamentos' in xl.sheet_names:
            return 'itau'
        
        # Banco do Brasil tem planilha "Extrato"
        if 'Extrato' in xl.sheet_names:
            # Ler primeiras linhas para confirmar
            df = pd.read_excel(arquivo_path, sheet_name='Extrato', nrows=5)
            if 'Extrato Conta Corrente' in df.columns:
                return 'banco_brasil'
        
        return 'desconhecido'
    except:
        return 'desconhecido'


def criar_parser(arquivo_path: str) -> ParserExtratoBase:
    """
    Cria o parser apropriado baseado no tipo de banco
    
    Args:
        arquivo_path: Caminho do arquivo
    
    Returns:
        ParserExtratoBase: Parser específico do banco
    
    Raises:
        ValueError: Se o banco não for reconhecido
    """
    banco = detectar_banco(arquivo_path)
    
    if banco == 'itau':
        return ParserItau(arquivo_path)
    elif banco == 'banco_brasil':
        return ParserBancoBrasil(arquivo_path)
    else:
        raise ValueError(f"Formato de extrato não reconhecido. Banco: {banco}")
