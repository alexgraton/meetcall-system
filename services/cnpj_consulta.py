"""
Serviço de consulta automática de CNPJ em APIs públicas
Implementa sistema de fallback entre 3 APIs diferentes
"""
import requests
import logging
from services.cnpj_validator import limpar_documento

# Configurar logging
logger = logging.getLogger(__name__)

def formatar_cep(cep):
    """Formata CEP no padrão 99999-999"""
    if not cep:
        return ''
    cep_limpo = ''.join(filter(str.isdigit, str(cep)))
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep_limpo

def formatar_telefone(telefone):
    """Remove caracteres especiais do telefone, mantendo apenas dígitos"""
    if not telefone:
        return ''
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
    # Limitar a 50 caracteres
    return telefone_limpo[:50]

def consultar_brasil_api(cnpj):
    """
    Consulta CNPJ na BrasilAPI
    
    Args:
        cnpj (str): CNPJ com 14 dígitos (apenas números)
        
    Returns:
        tuple: (dados_normalizados, status)
        status pode ser: 'success', 'not_found', 'rate_limit', 'error'
    """
    try:
        url = f'https://brasilapi.com.br/api/cnpj/v1/{cnpj}'
        logger.info(f"Consultando BrasilAPI para CNPJ: {cnpj}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            logger.warning(f"CNPJ não encontrado na BrasilAPI: {cnpj}")
            return None, 'not_found'
        
        if response.status_code == 429:
            logger.warning(f"Limite de requisições atingido na BrasilAPI")
            return None, 'rate_limit'
        
        if response.status_code != 200:
            logger.error(f"Erro na BrasilAPI: Status {response.status_code}")
            return None, 'error'
        
        data = response.json()
        
        # Normalizar dados
        dados_normalizados = {
            'razao_social': data.get('razao_social', ''),
            'nome': data.get('nome_fantasia', '') or data.get('razao_social', ''),
            'cnpj': cnpj,
            'cep': formatar_cep(data.get('cep', '')),
            'rua': data.get('logradouro', ''),
            'numero': data.get('numero', ''),
            'complemento': data.get('complemento', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('municipio', ''),
            'estado': data.get('uf', ''),
            'telefone': formatar_telefone(data.get('ddd_telefone_1', '')),
            'email': data.get('email', ''),
            'situacao': data.get('descricao_situacao_cadastral', ''),
            'atividade_principal': data.get('cnae_fiscal_descricao', '')
        }
        
        logger.info(f"CNPJ consultado com sucesso na BrasilAPI: {cnpj}")
        return dados_normalizados, 'success'
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao consultar BrasilAPI para CNPJ: {cnpj}")
        return None, 'error'
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar BrasilAPI: {str(e)}")
        return None, 'error'
    except Exception as e:
        logger.error(f"Erro inesperado na BrasilAPI: {str(e)}")
        return None, 'error'

def consultar_receita_ws(cnpj):
    """
    Consulta CNPJ na ReceitaWS
    
    Args:
        cnpj (str): CNPJ com 14 dígitos (apenas números)
        
    Returns:
        tuple: (dados_normalizados, status)
        status pode ser: 'success', 'not_found', 'rate_limit', 'error'
    """
    try:
        url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
        logger.info(f"Consultando ReceitaWS para CNPJ: {cnpj}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 429:
            logger.warning(f"Limite de requisições atingido na ReceitaWS")
            return None, 'rate_limit'
        
        if response.status_code != 200:
            logger.error(f"Erro na ReceitaWS: Status {response.status_code}")
            return None, 'error'
        
        data = response.json()
        
        # ReceitaWS retorna status: 'ERROR' quando CNPJ não é encontrado
        if data.get('status') == 'ERROR':
            logger.warning(f"CNPJ não encontrado na ReceitaWS: {cnpj}")
            return None, 'not_found'
        
        # Normalizar dados
        telefone = formatar_telefone(data.get('telefone', ''))
        cep = data.get('cep', '').replace('.', '').replace('-', '')
        
        # Atividade principal
        atividade_principal = ''
        if data.get('atividade_principal') and len(data['atividade_principal']) > 0:
            atividade_principal = data['atividade_principal'][0].get('text', '')
        
        dados_normalizados = {
            'razao_social': data.get('nome', ''),
            'nome': data.get('fantasia', '') or data.get('nome', ''),
            'cnpj': cnpj,
            'cep': formatar_cep(cep),
            'rua': data.get('logradouro', ''),
            'numero': data.get('numero', ''),
            'complemento': data.get('complemento', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('municipio', ''),
            'estado': data.get('uf', ''),
            'telefone': telefone,
            'email': data.get('email', ''),
            'situacao': data.get('situacao', ''),
            'atividade_principal': atividade_principal
        }
        
        logger.info(f"CNPJ consultado com sucesso na ReceitaWS: {cnpj}")
        return dados_normalizados, 'success'
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao consultar ReceitaWS para CNPJ: {cnpj}")
        return None, 'error'
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar ReceitaWS: {str(e)}")
        return None, 'error'
    except Exception as e:
        logger.error(f"Erro inesperado na ReceitaWS: {str(e)}")
        return None, 'error'

def consultar_cnpj_ws(cnpj):
    """
    Consulta CNPJ na CNPJ.WS
    
    Args:
        cnpj (str): CNPJ com 14 dígitos (apenas números)
        
    Returns:
        tuple: (dados_normalizados, status)
        status pode ser: 'success', 'not_found', 'rate_limit', 'error'
    """
    try:
        url = f'https://publica.cnpj.ws/cnpj/{cnpj}'
        logger.info(f"Consultando CNPJ.WS para CNPJ: {cnpj}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            logger.warning(f"CNPJ não encontrado na CNPJ.WS: {cnpj}")
            return None, 'not_found'
        
        if response.status_code == 429:
            logger.warning(f"Limite de requisições atingido na CNPJ.WS")
            return None, 'rate_limit'
        
        if response.status_code != 200:
            logger.error(f"Erro na CNPJ.WS: Status {response.status_code}")
            return None, 'error'
        
        data = response.json()
        estabelecimento = data.get('estabelecimento', {})
        
        # Concatenar telefone (DDD + número)
        ddd = estabelecimento.get('ddd1', '')
        telefone = estabelecimento.get('telefone1', '')
        telefone_completo = formatar_telefone(f"{ddd}{telefone}")
        
        # Concatenar tipo_logradouro + logradouro
        tipo_logradouro = estabelecimento.get('tipo_logradouro', '')
        logradouro = estabelecimento.get('logradouro', '')
        rua_completa = f"{tipo_logradouro} {logradouro}".strip()
        
        # CEP
        cep = estabelecimento.get('cep', '')
        
        # Cidade e Estado
        cidade = estabelecimento.get('cidade', {}).get('nome', '')
        estado = estabelecimento.get('estado', {}).get('sigla', '')
        
        # Atividade principal
        atividade_principal = estabelecimento.get('atividade_principal', {}).get('descricao', '')
        
        dados_normalizados = {
            'razao_social': data.get('razao_social', ''),
            'nome': estabelecimento.get('nome_fantasia', '') or data.get('razao_social', ''),
            'cnpj': cnpj,
            'cep': formatar_cep(cep),
            'rua': rua_completa,
            'numero': estabelecimento.get('numero', ''),
            'complemento': estabelecimento.get('complemento', ''),
            'bairro': estabelecimento.get('bairro', ''),
            'cidade': cidade,
            'estado': estado,
            'telefone': telefone_completo,
            'email': estabelecimento.get('email', ''),
            'situacao': estabelecimento.get('situacao_cadastral', ''),
            'atividade_principal': atividade_principal
        }
        
        logger.info(f"CNPJ consultado com sucesso na CNPJ.WS: {cnpj}")
        return dados_normalizados, 'success'
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao consultar CNPJ.WS para CNPJ: {cnpj}")
        return None, 'error'
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar CNPJ.WS: {str(e)}")
        return None, 'error'
    except Exception as e:
        logger.error(f"Erro inesperado na CNPJ.WS: {str(e)}")
        return None, 'error'

def buscar_cnpj(cnpj):
    """
    Função principal que implementa o sistema de fallback entre as 3 APIs
    
    Args:
        cnpj (str): CNPJ com ou sem formatação
        
    Returns:
        dict: Resposta com dados ou erro
        {
            'success': bool,
            'data': dict (se sucesso),
            'message': str,
            'api_utilizada': str (se sucesso)
        }
    """
    # Limpar CNPJ (remover caracteres especiais)
    cnpj_limpo = limpar_documento(cnpj)
    
    # Validar se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        logger.warning(f"CNPJ inválido (não tem 14 dígitos): {cnpj}")
        return {
            'success': False,
            'message': 'CNPJ inválido. Deve conter 14 dígitos.',
            'error_code': 'invalid_cnpj'
        }
    
    # Definir APIs na ordem de prioridade
    apis = [
        ('BrasilAPI', consultar_brasil_api),
        ('ReceitaWS', consultar_receita_ws),
        ('CNPJ.WS', consultar_cnpj_ws)
    ]
    
    erros_encontrados = []
    
    # Tentar cada API em sequência
    for nome_api, funcao_api in apis:
        resultado, status = funcao_api(cnpj_limpo)
        
        if status == 'success':
            logger.info(f"CNPJ {cnpj_limpo} consultado com sucesso na API: {nome_api}")
            return {
                'success': True,
                'data': resultado,
                'message': 'CNPJ consultado com sucesso',
                'api_utilizada': nome_api
            }
        
        # Registrar erro para retornar caso todas as APIs falhem
        erros_encontrados.append({
            'api': nome_api,
            'status': status
        })
        
        logger.warning(f"Falha ao consultar {nome_api}: {status}")
    
    # Se chegou aqui, nenhuma API funcionou
    logger.error(f"Todas as APIs falharam ao consultar CNPJ: {cnpj_limpo}")
    
    # Verificar se foi por CNPJ não encontrado
    if all(erro['status'] == 'not_found' for erro in erros_encontrados):
        return {
            'success': False,
            'message': 'CNPJ não encontrado em nenhuma base de dados.',
            'error_code': 'not_found'
        }
    
    # Verificar se foi por rate limit
    if any(erro['status'] == 'rate_limit' for erro in erros_encontrados):
        return {
            'success': False,
            'message': 'Limite de requisições atingido. Tente novamente em alguns minutos.',
            'error_code': 'rate_limit'
        }
    
    # Erro genérico
    return {
        'success': False,
        'message': 'Não foi possível consultar o CNPJ. As APIs estão temporariamente indisponíveis.',
        'error_code': 'service_unavailable'
    }
