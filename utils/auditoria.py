"""
Utilitários de Auditoria
Decorators e helpers para captura automática de ações
"""
from functools import wraps
from flask import request, session
from models.auditoria import AuditoriaModel
import json

def obter_ip_usuario():
    """Obtém o endereço IP do usuário"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        # Se estiver atrás de um proxy
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.environ.get('REMOTE_ADDR', 'unknown')
    return ip

def obter_usuario_sessao():
    """Obtém informações do usuário da sessão"""
    return {
        'id': session.get('user_id'),
        'email': session.get('user'),
        'name': session.get('name'),
        'role': session.get('role')
    }

def auditar_acao(tabela, acao='insert'):
    """
    Decorator para auditar ações automaticamente
    
    Usage:
        @auditar_acao('fornecedores', 'insert')
        def criar_fornecedor():
            ...
        
        @auditar_acao('fornecedores', 'update')
        def atualizar_fornecedor(id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            usuario = obter_usuario_sessao()
            ip = obter_ip_usuario()
            
            # Capturar dados antes (para update/delete)
            dados_anteriores = None
            registro_id = None
            
            # Tentar extrair ID do registro dos argumentos
            if 'id' in kwargs:
                registro_id = kwargs['id']
            elif len(args) > 0 and isinstance(args[0], int):
                registro_id = args[0]
            
            # Executar função original
            resultado = f(*args, **kwargs)
            
            # Tentar extrair ID do resultado (para insert)
            if acao == 'insert' and isinstance(resultado, (int, str)):
                registro_id = resultado
            elif acao == 'insert' and isinstance(resultado, dict) and 'id' in resultado:
                registro_id = resultado['id']
            
            # Capturar dados novos do form (para insert/update)
            dados_novos = None
            if request.method == 'POST':
                dados_novos = request.form.to_dict()
                # Remover campos sensíveis
                dados_novos.pop('password', None)
                dados_novos.pop('password_hash', None)
                dados_novos.pop('senha', None)
            
            # Registrar auditoria
            if registro_id:
                AuditoriaModel.registrar_acao(
                    tabela=tabela,
                    registro_id=registro_id,
                    acao=acao,
                    usuario_id=usuario.get('id'),
                    dados_anteriores=dados_anteriores,
                    dados_novos=dados_novos,
                    ip_address=ip
                )
            
            return resultado
        return wrapper
    return decorator

def auditar_exclusao(tabela):
    """
    Decorator específico para exclusões
    Captura os dados antes de deletar
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            usuario = obter_usuario_sessao()
            ip = obter_ip_usuario()
            
            # Extrair ID do registro
            registro_id = None
            if 'id' in kwargs:
                registro_id = kwargs['id']
            elif len(args) > 0:
                registro_id = args[0]
            
            # Capturar dados antes da exclusão
            dados_anteriores = None
            if registro_id and hasattr(f, '__self__'):
                # Se for um método de classe, tentar obter dados
                try:
                    # Aqui você pode adicionar lógica para buscar o registro antes de deletar
                    pass
                except:
                    pass
            
            # Executar exclusão
            resultado = f(*args, **kwargs)
            
            # Registrar auditoria
            if registro_id:
                AuditoriaModel.registrar_acao(
                    tabela=tabela,
                    registro_id=registro_id,
                    acao='delete',
                    usuario_id=usuario.get('id'),
                    dados_anteriores=dados_anteriores,
                    ip_address=ip
                )
            
            return resultado
        return wrapper
    return decorator

def auditar_visualizacao(tabela):
    """
    Decorator para auditar visualizações de registros
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            usuario = obter_usuario_sessao()
            ip = obter_ip_usuario()
            
            # Extrair ID do registro
            registro_id = None
            if 'id' in kwargs:
                registro_id = kwargs['id']
            elif len(args) > 0:
                registro_id = args[0]
            
            # Executar função original
            resultado = f(*args, **kwargs)
            
            # Registrar visualização
            if registro_id and usuario.get('id'):
                AuditoriaModel.registrar_visualizacao(
                    tabela=tabela,
                    registro_id=registro_id,
                    usuario_id=usuario.get('id'),
                    ip_address=ip
                )
            
            return resultado
        return wrapper
    return decorator

def registrar_login(usuario_id, email, sucesso=True):
    """Helper para registrar login"""
    ip = obter_ip_usuario()
    return AuditoriaModel.registrar_login(usuario_id, email, ip, sucesso)

def registrar_logout(usuario_id, email):
    """Helper para registrar logout"""
    ip = obter_ip_usuario()
    return AuditoriaModel.registrar_logout(usuario_id, email, ip)

def registrar_acao_customizada(tabela, registro_id, acao, dados=None):
    """
    Helper para registrar ações customizadas
    Use quando precisar de mais controle sobre o que é registrado
    """
    usuario = obter_usuario_sessao()
    ip = obter_ip_usuario()
    
    return AuditoriaModel.registrar_acao(
        tabela=tabela,
        registro_id=registro_id,
        acao=acao,
        usuario_id=usuario.get('id'),
        dados_novos=dados,
        ip_address=ip
    )

def obter_dados_form_seguros():
    """
    Obtém dados do formulário removendo campos sensíveis
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        dados = request.form.to_dict()
        
        # Remover campos sensíveis
        campos_sensiveis = [
            'password', 'password_hash', 'senha', 
            'token', 'secret', 'api_key'
        ]
        
        for campo in campos_sensiveis:
            dados.pop(campo, None)
        
        return dados
    
    return None

def formatar_mudancas(dados_anteriores, dados_novos):
    """
    Compara dados anteriores e novos e retorna apenas as mudanças
    """
    if not dados_anteriores or not dados_novos:
        return None
    
    mudancas = {}
    
    for chave, valor_novo in dados_novos.items():
        valor_antigo = dados_anteriores.get(chave)
        if valor_antigo != valor_novo:
            mudancas[chave] = {
                'de': valor_antigo,
                'para': valor_novo
            }
    
    return mudancas if mudancas else None
