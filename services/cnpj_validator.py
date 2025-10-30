"""
Serviço de validação de CNPJ/CPF
Valida documentos usando algoritmo de dígito verificador
"""

def validar_cnpj(cnpj):
    """
    Valida CNPJ usando algoritmo de dígito verificador
    
    Args:
        cnpj (str): CNPJ com ou sem formatação
        
    Returns:
        bool: True se válido, False se inválido
    """
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais (CNPJ inválido)
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    for i in range(12):
        soma += int(cnpj[i]) * peso[i]
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito
    if int(cnpj[12]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    for i in range(13):
        soma += int(cnpj[i]) * peso[i]
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito
    if int(cnpj[13]) != digito2:
        return False
    
    return True


def validar_cpf(cpf):
    """
    Valida CPF usando algoritmo de dígito verificador
    
    Args:
        cpf (str): CPF com ou sem formatação
        
    Returns:
        bool: True se válido, False se inválido
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito
    if int(cpf[9]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito
    if int(cpf[10]) != digito2:
        return False
    
    return True


def formatar_cnpj(cnpj):
    """
    Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj (str): CNPJ sem formatação
        
    Returns:
        str: CNPJ formatado ou None se inválido
    """
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj) != 14:
        return None
    
    return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'


def formatar_cpf(cpf):
    """
    Formata CPF para o padrão XXX.XXX.XXX-XX
    
    Args:
        cpf (str): CPF sem formatação
        
    Returns:
        str: CPF formatado ou None se inválido
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11:
        return None
    
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}'


def limpar_documento(documento):
    """
    Remove formatação de CPF/CNPJ
    
    Args:
        documento (str): Documento com ou sem formatação
        
    Returns:
        str: Apenas números
    """
    return ''.join(filter(str.isdigit, documento))
