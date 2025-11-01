"""
Rotas para relatórios financeiros
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.relatorios import Relatorios
from datetime import datetime, timedelta
from decimal import Decimal
import functools


relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


def login_required(f):
    """Decorator para verificar se usuário está logado"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def converter_decimal(obj):
    """Converte objetos Decimal para float recursivamente"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: converter_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_decimal(item) for item in obj]
    return obj


@relatorios_bp.route('/')
@login_required
def index():
    """Página principal de relatórios"""
    return render_template('relatorios/index.html')


@relatorios_bp.route('/dre')
@login_required
def dre():
    """Página do DRE"""
    # Período padrão: mês atual
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1)
    
    # Obter parâmetros da URL ou usar padrão
    data_inicio = request.args.get('data_inicio', primeiro_dia.strftime('%Y-%m-%d'))
    data_fim = request.args.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    # Gerar DRE
    dados_dre = Relatorios.get_dre(data_inicio, data_fim)
    
    return render_template('relatorios/dre.html', 
                         dre=dados_dre,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/balanco')
@login_required
def balanco():
    """Página do Balanço Patrimonial"""
    # Data padrão: hoje
    hoje = datetime.now()
    data_referencia = request.args.get('data_referencia', hoje.strftime('%Y-%m-%d'))
    
    # Gerar Balanço
    dados_balanco = Relatorios.get_balanco_patrimonial(data_referencia)
    
    return render_template('relatorios/balanco.html',
                         balanco=dados_balanco,
                         data_referencia=data_referencia)


@relatorios_bp.route('/dfc')
@login_required
def dfc():
    """Página do DFC (Demonstração do Fluxo de Caixa)"""
    # Período padrão: mês atual
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1)
    
    data_inicio = request.args.get('data_inicio', primeiro_dia.strftime('%Y-%m-%d'))
    data_fim = request.args.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    # Gerar DFC
    dados_dfc = Relatorios.get_dfc(data_inicio, data_fim)
    
    return render_template('relatorios/dfc.html',
                         dfc=dados_dfc,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/analise-horizontal')
@login_required
def analise_horizontal():
    """Página de Análise Horizontal"""
    hoje = datetime.now()
    
    # Período 2: mês atual
    periodo_2_fim = hoje
    periodo_2_inicio = hoje.replace(day=1)
    
    # Período 1: mês anterior
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
    periodo_1_inicio = ultimo_dia_mes_anterior.replace(day=1)
    periodo_1_fim = ultimo_dia_mes_anterior
    
    # Obter parâmetros ou usar padrão
    data_inicio_1 = request.args.get('data_inicio_1', periodo_1_inicio.strftime('%Y-%m-%d'))
    data_fim_1 = request.args.get('data_fim_1', periodo_1_fim.strftime('%Y-%m-%d'))
    data_inicio_2 = request.args.get('data_inicio_2', periodo_2_inicio.strftime('%Y-%m-%d'))
    data_fim_2 = request.args.get('data_fim_2', periodo_2_fim.strftime('%Y-%m-%d'))
    
    # Gerar análise
    analise = Relatorios.get_analise_horizontal(data_inicio_1, data_fim_1, data_inicio_2, data_fim_2)
    
    return render_template('relatorios/analise_horizontal.html',
                         analise=analise,
                         data_inicio_1=data_inicio_1,
                         data_fim_1=data_fim_1,
                         data_inicio_2=data_inicio_2,
                         data_fim_2=data_fim_2)


@relatorios_bp.route('/analise-vertical')
@login_required
def analise_vertical():
    """Página de Análise Vertical"""
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1)
    
    data_inicio = request.args.get('data_inicio', primeiro_dia.strftime('%Y-%m-%d'))
    data_fim = request.args.get('data_fim', hoje.strftime('%Y-%m-%d'))
    
    # Gerar análise
    analise = Relatorios.get_analise_vertical(data_inicio, data_fim)
    
    return render_template('relatorios/analise_vertical.html',
                         analise=analise,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


# APIs JSON para consultas via AJAX
@relatorios_bp.route('/api/dre')
@login_required
def api_dre():
    """API JSON para DRE"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        return jsonify({'erro': 'Parâmetros data_inicio e data_fim são obrigatórios'}), 400
    
    try:
        dre = Relatorios.get_dre(data_inicio, data_fim)
        return jsonify(converter_decimal(dre))
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/api/balanco')
@login_required
def api_balanco():
    """API JSON para Balanço"""
    data_referencia = request.args.get('data_referencia')
    
    if not data_referencia:
        return jsonify({'erro': 'Parâmetro data_referencia é obrigatório'}), 400
    
    try:
        balanco = Relatorios.get_balanco_patrimonial(data_referencia)
        return jsonify(converter_decimal(balanco))
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/api/dfc')
@login_required
def api_dfc():
    """API JSON para DFC"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        return jsonify({'erro': 'Parâmetros data_inicio e data_fim são obrigatórios'}), 400
    
    try:
        dfc = Relatorios.get_dfc(data_inicio, data_fim)
        return jsonify(converter_decimal(dfc))
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
