"""
Parser para arquivos CSV de extrato bancário
Suporta múltiplos formatos bancários
"""
import csv
from datetime import datetime
from decimal import Decimal
import re


class CSVParser:
    """Parser genérico para extratos CSV"""
    
    def __init__(self, arquivo_path, encoding='utf-8', delimiter=';'):
        """
        Inicializa o parser
        
        Args:
            arquivo_path: Caminho do arquivo CSV
            encoding: Codificação do arquivo (padrão: utf-8)
            delimiter: Delimitador usado no CSV (padrão: ;)
        """
        self.arquivo_path = arquivo_path
        self.encoding = encoding
        self.delimiter = delimiter
        self.transacoes = []
    
    def detectar_formato(self, primeira_linha):
        """
        Detecta o formato do CSV baseado no cabeçalho
        
        Returns:
            dict com mapeamento de colunas
        """
        # Formatos conhecidos (exemplos)
        formatos = [
            # Formato padrão genérico
            {
                'tipo': 'generico',
                'colunas': {
                    'data': ['data', 'data_transacao', 'date'],
                    'descricao': ['descricao', 'historico', 'description', 'desc'],
                    'documento': ['documento', 'doc', 'number', 'numero'],
                    'valor': ['valor', 'amount', 'value'],
                    'tipo': ['tipo', 'type', 'd/c'],
                    'saldo': ['saldo', 'balance', 'saldo_apos']
                }
            },
            # Formato Bradesco
            {
                'tipo': 'bradesco',
                'colunas': {
                    'data': ['data'],
                    'descricao': ['lancamento', 'historico'],
                    'documento': ['numero do documento'],
                    'valor': ['valor'],
                    'tipo': ['c/d'],
                    'saldo': ['saldo']
                }
            },
            # Formato Itaú
            {
                'tipo': 'itau',
                'colunas': {
                    'data': ['data'],
                    'descricao': ['descricao'],
                    'documento': ['documento'],
                    'valor': ['valor'],
                    'tipo': ['tipo'],
                    'saldo': ['saldo']
                }
            }
        ]
        
        # Normalizar cabeçalho
        header_lower = [col.strip().lower() for col in primeira_linha]
        
        # Tentar identificar formato
        for formato in formatos:
            score = 0
            mapeamento = {}
            
            for campo, variacoes in formato['colunas'].items():
                for idx, col in enumerate(header_lower):
                    if any(var in col for var in variacoes):
                        mapeamento[campo] = idx
                        score += 1
                        break
            
            # Se encontrou pelo menos data, descrição e valor
            if score >= 3 and 'data' in mapeamento and 'descricao' in mapeamento and 'valor' in mapeamento:
                return mapeamento
        
        # Retorna mapeamento genérico se não identificou
        return {
            'data': 0,
            'descricao': 1,
            'documento': 2 if len(header_lower) > 2 else None,
            'valor': 3 if len(header_lower) > 3 else 2,
            'tipo': 4 if len(header_lower) > 4 else None,
            'saldo': 5 if len(header_lower) > 5 else None
        }
    
    def limpar_valor(self, valor_str):
        """
        Limpa e converte string de valor para Decimal
        
        Args:
            valor_str: String com valor (ex: "R$ 1.234,56" ou "-1234.56")
            
        Returns:
            Decimal com valor numérico
        """
        if not valor_str or valor_str.strip() == '':
            return Decimal('0')
        
        # Remover símbolos de moeda e espaços
        valor_str = valor_str.strip()
        valor_str = re.sub(r'[R$\s]', '', valor_str)
        
        # Detectar formato (BR ou US)
        if ',' in valor_str and '.' in valor_str:
            # Tem ambos - determinar qual é decimal
            ultima_virgula = valor_str.rfind(',')
            ultimo_ponto = valor_str.rfind('.')
            
            if ultima_virgula > ultimo_ponto:
                # Formato BR: 1.234,56
                valor_str = valor_str.replace('.', '').replace(',', '.')
            else:
                # Formato US: 1,234.56
                valor_str = valor_str.replace(',', '')
        elif ',' in valor_str:
            # Só tem vírgula - assumir formato BR
            valor_str = valor_str.replace(',', '.')
        
        # Converter para Decimal
        try:
            return Decimal(valor_str)
        except:
            return Decimal('0')
    
    def parse_data(self, data_str):
        """
        Converte string de data para datetime
        
        Args:
            data_str: String com data em diversos formatos
            
        Returns:
            datetime ou None
        """
        if not data_str or data_str.strip() == '':
            return None
        
        data_str = data_str.strip()
        
        # Formatos suportados
        formatos = [
            '%d/%m/%Y',
            '%d/%m/%y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d.%m.%Y',
            '%Y/%m/%d'
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(data_str, formato)
            except:
                continue
        
        return None
    
    def detectar_tipo(self, linha, mapeamento):
        """
        Detecta se transação é débito ou crédito
        
        Returns:
            'debito' ou 'credito'
        """
        # Se tem coluna tipo, usar ela
        if mapeamento.get('tipo') is not None:
            tipo_str = linha[mapeamento['tipo']].strip().upper()
            
            if tipo_str in ['D', 'DEBITO', 'DÉBITO', 'DEB', '-']:
                return 'debito'
            elif tipo_str in ['C', 'CREDITO', 'CRÉDITO', 'CRE', '+']:
                return 'credito'
        
        # Senão, usar o sinal do valor
        valor_str = linha[mapeamento['valor']]
        if '-' in valor_str:
            return 'debito'
        else:
            return 'credito'
    
    def parse(self):
        """
        Faz o parse do arquivo CSV
        
        Returns:
            list de dict com transações
        """
        try:
            with open(self.arquivo_path, 'r', encoding=self.encoding, errors='ignore') as arquivo:
                reader = csv.reader(arquivo, delimiter=self.delimiter)
                
                # Ler cabeçalho
                primeira_linha = next(reader)
                mapeamento = self.detectar_formato(primeira_linha)
                
                # Processar linhas
                for linha in reader:
                    # Pular linhas vazias
                    if not linha or all(not cell.strip() for cell in linha):
                        continue
                    
                    # Garantir que linha tem dados suficientes
                    if len(linha) <= max(v for v in mapeamento.values() if v is not None):
                        continue
                    
                    # Extrair dados
                    data = self.parse_data(linha[mapeamento['data']])
                    if not data:
                        continue
                    
                    descricao = linha[mapeamento['descricao']].strip()
                    if not descricao:
                        continue
                    
                    documento = linha[mapeamento['documento']].strip() if mapeamento.get('documento') is not None else ''
                    valor = abs(self.limpar_valor(linha[mapeamento['valor']]))
                    tipo = self.detectar_tipo(linha, mapeamento)
                    saldo = self.limpar_valor(linha[mapeamento['saldo']]) if mapeamento.get('saldo') is not None else None
                    
                    self.transacoes.append({
                        'data_transacao': data.date(),
                        'descricao': descricao,
                        'documento': documento,
                        'valor': valor,
                        'tipo': tipo,
                        'saldo_apos': saldo
                    })
                
                return self.transacoes
                
        except Exception as e:
            raise Exception(f"Erro ao fazer parse do CSV: {str(e)}")
    
    def get_resumo(self):
        """Retorna resumo do parse"""
        if not self.transacoes:
            return None
        
        total_creditos = sum(t['valor'] for t in self.transacoes if t['tipo'] == 'credito')
        total_debitos = sum(t['valor'] for t in self.transacoes if t['tipo'] == 'debito')
        
        datas = [t['data_transacao'] for t in self.transacoes]
        
        return {
            'total_transacoes': len(self.transacoes),
            'total_creditos': total_creditos,
            'total_debitos': total_debitos,
            'saldo_liquido': total_creditos - total_debitos,
            'data_inicio': min(datas),
            'data_fim': max(datas)
        }
